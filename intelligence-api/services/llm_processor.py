import json
import httpx
import asyncio
from typing import Dict, Any, Optional
from functools import lru_cache
from circuitbreaker import circuit
from tenacity import retry, stop_after_attempt, wait_exponential
from ..utils import get_logger, Config

logger = get_logger(__name__)

CATEGORIZATION_SYSTEM_PROMPT = """
You are an expert conflict analyst for the Nigerian Violent Conflicts Database (NNVCD).

Classify the conflict described in the provided text into exactly ONE of these predefined categories:
- Banditry: Criminal activities involving armed robbery, theft, or banditry by organized groups.
- Kidnapping: Abduction of individuals for ransom or other purposes.
- Gunmen Violence: Attacks or shootings by unidentified armed gunmen, often in hit-and-run style.
- Farmer-Herder Clashes: Conflicts between farming communities and nomadic herders over land, water, or resources.

Also provide a confidence score (0-100) indicating how certain you are of this classification, where:
- 100 = Completely certain, matches category perfectly
- 80-99 = High confidence, strong indicators present
- 60-79 = Moderate confidence, some indicators but ambiguity
- 40-59 = Low confidence, weak indicators
- 0-39 = Very low confidence, classification is a best guess

Analyze the text carefully and return a JSON object with exactly these fields:
- "category": The chosen category from the list above
- "confidence": Integer confidence score (0-100)

If the text does not clearly fit any category or describes a different type of conflict, use "Unknown" as category and provide appropriate confidence.

Examples:
- Text about cattle rustling: {"category": "Farmer-Herder Clashes", "confidence": 95}
- Text about armed robbery: {"category": "Banditry", "confidence": 90}
- Text about unclear violence: {"category": "Gunmen Violence", "confidence": 60}

Return ONLY valid JSON with the "category" and "confidence" fields.
"""


class LLMProcessor:
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
    async def analyze_with_ollama(self, text: str) -> Optional[str]:
        """Analyze text with Ollama to categorize conflict type"""
        try:
            prompt = f"{CATEGORIZATION_SYSTEM_PROMPT}\n\nText to analyze:\n{text}"

            payload = {
                "model": "llama3.2",
                "prompt": prompt,
                "format": "json",
                "stream": False,
                "options": {
                    "temperature": 0.1,
                    "max_tokens": 50  # Short response for categorization
                }
            }

            response = await self.client.post("http://localhost:11434/api/generate", json=payload)
            response.raise_for_status()

            result = response.json()

            if "response" in result:
                llm_response = result["response"].strip()

                # Parse JSON response
                try:
                    parsed_data = json.loads(llm_response)
                    category = parsed_data.get("category", "Unknown")
                    confidence = parsed_data.get("confidence", 0)

                    # Validate category
                    valid_categories = ["Banditry", "Kidnapping", "Gunmen Violence", "Farmer-Herder Clashes", "Unknown"]
                    if category not in valid_categories:
                        logger.warning(f"Invalid category returned: {category}, defaulting to Unknown")
                        category = "Unknown"

                    # Validate confidence
                    try:
                        confidence = int(confidence)
                        if confidence < 0 or confidence > 100:
                            logger.warning(f"Confidence out of range: {confidence}, defaulting to 0")
                            confidence = 0
                    except (ValueError, TypeError):
                        logger.warning(f"Invalid confidence: {confidence}, defaulting to 0")
                        confidence = 0

                    return {"category": category, "confidence": confidence}
                except json.JSONDecodeError as e:
                    logger.error("Failed to parse JSON from LLM response", response=llm_response, error=str(e))
                    return {"category": "Unknown", "confidence": 0}
            else:
                logger.error("Unexpected LLM response format", response=result)
                return {"category": "Unknown", "confidence": 0}

        except httpx.TimeoutException:
            logger.error("Timeout calling Ollama LLM for categorization")
            return {"category": "Unknown", "confidence": 0}
        except httpx.ConnectError:
            logger.error("Connection error calling Ollama LLM for categorization")
            return {"category": "Unknown", "confidence": 0}
        except httpx.HTTPStatusError as e:
            logger.error("HTTP error calling Ollama LLM for categorization", status_code=e.response.status_code)
            return {"category": "Unknown", "confidence": 0}
        except Exception as e:
            logger.error("Unexpected error calling Ollama LLM for categorization", error=str(e))
            return {"category": "Unknown", "confidence": 0}

    async def categorize_articles_batch(self, articles: list) -> list:
        """Categorize multiple articles concurrently"""
        try:
            # Create semaphore to limit concurrent processing
            semaphore = asyncio.Semaphore(Config.MAX_CONCURRENT_PROCESSING)

            async def categorize_with_semaphore(article):
                async with semaphore:
                    text = f"Title: {article.get('title', '')}\n\nContent: {article.get('content', '')}"
                    result = await self.analyze_with_ollama(text)
                    if isinstance(result, dict):
                        return {
                            "id": article.get("_id"),
                            "category": result["category"],
                            "confidence": result["confidence"]
                        }
                    else:
                        # Fallback for unexpected return type
                        return {
                            "id": article.get("_id"),
                            "category": "Unknown",
                            "confidence": 0
                        }

            # Process articles concurrently
            tasks = [categorize_with_semaphore(article) for article in articles]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Filter successful results
            categorized = []
            for result in results:
                if isinstance(result, dict):
                    categorized.append(result)
                elif isinstance(result, Exception):
                    logger.error("Error categorizing article", error=str(result))
                else:
                    logger.warning("Failed to categorize article")

            logger.info("Categorized articles batch",
                       total=len(articles),
                       successful=len(categorized))

            return categorized

        except Exception as e:
            logger.error("Error categorizing articles batch", error=str(e))
            return []

    async def close(self) -> None:
        """Close HTTP client"""
        if self.client:
            await self.client.aclose()
            logger.info("Closed LLM processor HTTP client")
