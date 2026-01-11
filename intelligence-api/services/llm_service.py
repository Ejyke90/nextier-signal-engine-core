import json
import httpx
import asyncio
from typing import Dict, Any, Optional
from functools import lru_cache
from circuitbreaker import circuit
from tenacity import retry, stop_after_attempt, wait_exponential
from fastapi import HTTPException
from ..utils import get_logger, Config
from ..models import ParsedEvent

logger = get_logger(__name__)


class LLMService:
    def __init__(self):
        self.client = None
        self._create_client()
    
    def _create_client(self) -> None:
        """Create HTTP client with connection pooling"""
        self.client = httpx.AsyncClient(
            timeout=Config.REQUEST_TIMEOUT,
            limits=httpx.Limits(
                max_connections=Config.MAX_CONNECTIONS,
                max_keepalive_connections=Config.MAX_KEEPALIVE_CONNECTIONS
            )
        )
    
    @lru_cache(maxsize=100)
    def _get_text_hash(self, text: str) -> str:
        """Get hash of text for caching"""
        return hash(text)
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    @circuit(failure_threshold=5, recovery_timeout=30)
    async def call_ollama_llm(self, text: str) -> Optional[Dict[str, Any]]:
        """Call local Ollama LLM to parse news text with retry and circuit breaker"""
        try:
            prompt = f"{Config.SYSTEM_PROMPT}\n\nText to analyze:\n{text}"
            
            payload = {
                "model": Config.OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.1,
                    "max_tokens": 200
                }
            }
            
            response = await self.client.post(Config.OLLAMA_URL, json=payload)
            response.raise_for_status()
            
            result = response.json()
            
            # Extract the response text
            if "response" in result:
                llm_response = result["response"].strip()
                
                # Try to parse JSON from the response
                try:
                    # Clean up the response to extract JSON
                    if "```json" in llm_response:
                        json_start = llm_response.find("```json") + 7
                        json_end = llm_response.find("```", json_start)
                        json_str = llm_response[json_start:json_end].strip()
                    elif "{" in llm_response and "}" in llm_response:
                        json_start = llm_response.find("{")
                        json_end = llm_response.rfind("}") + 1
                        json_str = llm_response[json_start:json_end]
                    else:
                        json_str = llm_response
                    
                    parsed_data = json.loads(json_str)
                    
                    # Validate required fields
                    required_fields = ["Event_Type", "State", "LGA", "Severity"]
                    if all(field in parsed_data for field in required_fields):
                        return {
                            "event_type": parsed_data.get("Event_Type", "unknown"),
                            "state": parsed_data.get("State", "unknown") or "unknown",
                            "lga": parsed_data.get("LGA", "unknown") or "unknown",
                            "severity": parsed_data.get("Severity", "unknown") or "unknown"
                        }
                    else:
                        logger.warning("LLM response missing required fields", response=parsed_data)
                        return None
                        
                except json.JSONDecodeError as e:
                    logger.error("Failed to parse JSON from LLM response", response=llm_response, error=str(e))
                    return None
            else:
                logger.error("Unexpected LLM response format", response=result)
                return None
                
        except httpx.TimeoutException:
            logger.error("Timeout calling Ollama LLM")
            return None
        except httpx.ConnectError:
            logger.error("Connection error calling Ollama LLM")
            return None
        except httpx.HTTPStatusError as e:
            logger.error("HTTP error calling Ollama LLM", status_code=e.response.status_code)
            return None
        except Exception as e:
            logger.error("Unexpected error calling Ollama LLM", error=str(e))
            return None
    
    async def parse_article_with_llm(self, article: Dict[str, Any]) -> Optional[ParsedEvent]:
        """Parse a single article using LLM"""
        try:
            # Combine title and content for better context
            text_to_analyze = f"Title: {article.get('title', '')}\n\nContent: {article.get('content', '')}"
            
            # Call LLM
            parsed_data = await self.call_ollama_llm(text_to_analyze)
            
            if parsed_data:
                return ParsedEvent(
                    event_type=parsed_data["event_type"],
                    state=parsed_data["state"],
                    lga=parsed_data["lga"],
                    severity=parsed_data["severity"],
                    source_title=article.get("title", ""),
                    source_url=article.get("url", "")
                )
            else:
                logger.warning("Failed to parse article", title=article.get('title', 'Unknown title'))
                return None
                
        except Exception as e:
            logger.error("Error parsing article", error=str(e))
            return None
    
    async def process_articles_batch(self, articles: list) -> list:
        """Process multiple articles concurrently"""
        try:
            # Create semaphore to limit concurrent processing
            semaphore = asyncio.Semaphore(Config.MAX_CONCURRENT_PROCESSING)
            
            async def process_with_semaphore(article):
                async with semaphore:
                    return await self.parse_article_with_llm(article)
            
            # Process articles concurrently
            tasks = [process_with_semaphore(article) for article in articles]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Filter successful results
            parsed_events = []
            for result in results:
                if isinstance(result, ParsedEvent):
                    parsed_events.append(result.dict())
                elif isinstance(result, Exception):
                    logger.error("Error processing article", error=str(result))
                else:
                    logger.warning("Failed to parse article")
            
            logger.info("Processed articles batch", 
                       total=len(articles), 
                       successful=len(parsed_events))
            
            return parsed_events
            
        except Exception as e:
            logger.error("Error processing articles batch", error=str(e))
            return []
    
    async def close(self) -> None:
        """Close HTTP client"""
        if self.client:
            await self.client.aclose()
            logger.info("Closed LLM service HTTP client")
