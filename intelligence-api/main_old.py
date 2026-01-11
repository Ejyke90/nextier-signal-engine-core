import json
import os
import logging
import asyncio
from datetime import datetime
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx
from requests.exceptions import RequestException, Timeout, ConnectionError

app = FastAPI(title="Intelligence API Service", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
DATA_DIR = "/data"
RAW_NEWS_FILE = os.path.join(DATA_DIR, "raw_news.json")
PARSED_EVENTS_FILE = os.path.join(DATA_DIR, "parsed_events.json")
OLLAMA_URL = "http://host.docker.internal:11434/api/generate"
SYSTEM_PROMPT = "You are a Nextier Conflict Analyst. Extract Event_Type, State, LGA, and Severity from this text. Return strictly valid JSON."

# Polling interval in seconds
POLL_INTERVAL = 30


class ParsedEvent(BaseModel):
    event_type: str
    state: str
    lga: str
    severity: str
    source_title: str
    source_url: str
    parsed_at: str


class HealthResponse(BaseModel):
    status: str
    service: str


class AnalysisResponse(BaseModel):
    status: str
    events_processed: int
    message: str


class EventsResponse(BaseModel):
    events: List[ParsedEvent]
    count: int


def ensure_data_directory():
    """Ensure the data directory exists"""
    os.makedirs(DATA_DIR, exist_ok=True)


async def call_ollama_llm(text: str) -> Optional[Dict[str, Any]]:
    """
    Call local Ollama LLM to parse news text
    """
    try:
        prompt = f"{SYSTEM_PROMPT}\n\nText to analyze:\n{text}"
        
        payload = {
            "model": "llama3.2:latest",  # Updated to match available model
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.1,  # Low temperature for consistent output
                "max_tokens": 200
            }
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(OLLAMA_URL, json=payload)
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
                        logger.warning(f"LLM response missing required fields: {parsed_data}")
                        return None
                        
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse JSON from LLM response: {llm_response}. Error: {e}")
                    return None
            else:
                logger.error(f"Unexpected LLM response format: {result}")
                return None
                
    except Timeout:
        logger.error("Timeout calling Ollama LLM")
        return None
    except ConnectionError:
        logger.error("Connection error calling Ollama LLM")
        return None
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error calling Ollama LLM: {e.response.status_code}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error calling Ollama LLM: {str(e)}")
        return None


async def parse_article_with_llm(article: Dict[str, Any]) -> Optional[ParsedEvent]:
    """Parse a single article using LLM"""
    try:
        # Combine title and content for better context
        text_to_analyze = f"Title: {article.get('title', '')}\n\nContent: {article.get('content', '')}"
        
        # Call LLM
        parsed_data = await call_ollama_llm(text_to_analyze)
        
        if parsed_data:
            return ParsedEvent(
                event_type=parsed_data["event_type"],
                state=parsed_data["state"],
                lga=parsed_data["lga"],
                severity=parsed_data["severity"],
                source_title=article.get("title", ""),
                source_url=article.get("url", ""),
                parsed_at=datetime.now().isoformat()
            )
        else:
            logger.warning(f"Failed to parse article: {article.get('title', 'Unknown title')}")
            return None
            
    except Exception as e:
        logger.error(f"Error parsing article: {str(e)}")
        return None


async def load_raw_news() -> List[Dict[str, Any]]:
    """Load raw news from JSON file"""
    try:
        if not os.path.exists(RAW_NEWS_FILE):
            logger.info("No raw news file found")
            return []
        
        with open(RAW_NEWS_FILE, 'r', encoding='utf-8') as f:
            articles = json.load(f)
        
        logger.info(f"Loaded {len(articles)} articles from {RAW_NEWS_FILE}")
        return articles
        
    except json.JSONDecodeError as e:
        logger.error(f"Error parsing raw news JSON: {str(e)}")
        return []
    except Exception as e:
        logger.error(f"Error loading raw news: {str(e)}")
        return []


async def load_parsed_events() -> List[Dict[str, Any]]:
    """Load existing parsed events"""
    try:
        if not os.path.exists(PARSED_EVENTS_FILE):
            return []
        
        with open(PARSED_EVENTS_FILE, 'r', encoding='utf-8') as f:
            events = json.load(f)
        
        return events
        
    except json.JSONDecodeError:
        logger.warning("Existing parsed events file is corrupted, starting fresh")
        return []
    except Exception as e:
        logger.error(f"Error loading parsed events: {str(e)}")
        return []


async def save_parsed_events(events: List[Dict[str, Any]]) -> bool:
    """Save parsed events to JSON file"""
    try:
        ensure_data_directory()
        
        with open(PARSED_EVENTS_FILE, 'w', encoding='utf-8') as f:
            json.dump(events, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Saved {len(events)} events to {PARSED_EVENTS_FILE}")
        return True
        
    except Exception as e:
        logger.error(f"Error saving parsed events: {str(e)}")
        return False


async def process_news_articles():
    """Main processing function - poll raw news and parse with LLM"""
    try:
        logger.info("Starting news processing cycle")
        
        # Load raw news and existing parsed events
        raw_articles = await load_raw_news()
        existing_events = await load_parsed_events()
        
        if not raw_articles:
            logger.info("No raw articles to process")
            return
        
        # Get URLs of already processed articles
        processed_urls = {event.get("source_url", "") for event in existing_events}
        
        # Filter unprocessed articles
        unprocessed_articles = [
            article for article in raw_articles 
            if article.get("url", "") not in processed_urls
        ]
        
        if not unprocessed_articles:
            logger.info("No new articles to process")
            return
        
        logger.info(f"Processing {len(unprocessed_articles)} new articles")
        
        # Process articles with LLM
        new_events = []
        for article in unprocessed_articles:
            try:
                parsed_event = await parse_article_with_llm(article)
                if parsed_event:
                    new_events.append(parsed_event.dict())
                    logger.info(f"Successfully parsed: {parsed_event.source_title[:50]}...")
                else:
                    logger.warning(f"Failed to parse: {article.get('title', 'Unknown')}")
                    
            except Exception as e:
                logger.error(f"Error processing article {article.get('url', 'unknown')}: {str(e)}")
                continue
        
        if new_events:
            # Combine existing and new events
            all_events = existing_events + new_events
            
            # Save updated events
            success = await save_parsed_events(all_events)
            
            if success:
                logger.info(f"Successfully processed and saved {len(new_events)} new events")
            else:
                logger.error("Failed to save parsed events")
        else:
            logger.info("No new events were parsed successfully")
            
    except Exception as e:
        logger.error(f"Error in processing cycle: {str(e)}")


async def background_poller():
    """Background task to continuously poll for new articles"""
    while True:
        try:
            await process_news_articles()
            await asyncio.sleep(POLL_INTERVAL)
        except Exception as e:
            logger.error(f"Error in background poller: {str(e)}")
            await asyncio.sleep(POLL_INTERVAL)


@app.on_event("startup")
async def startup_event():
    """Start background polling on startup"""
    logger.info("Starting Intelligence API service")
    # Start background poller
    asyncio.create_task(background_poller())


@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Welcome to Intelligence API Service"}


@app.get("/health", response_model=HealthResponse)
async def health():
    """Health check endpoint"""
    return HealthResponse(status="healthy", service="intelligence-api")


@app.get("/analyze", response_model=AnalysisResponse)
async def analyze_news(background_tasks: BackgroundTasks):
    """Trigger immediate analysis of news articles"""
    try:
        # Run processing in background
        background_tasks.add_task(process_news_articles)
        
        return AnalysisResponse(
            status="processing",
            events_processed=0,
            message="News analysis started in background"
        )
        
    except Exception as e:
        logger.error(f"Error triggering analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@app.get("/events", response_model=EventsResponse)
async def get_events():
    """Get all parsed events"""
    try:
        events = await load_parsed_events()
        
        # Convert to ParsedEvent models
        event_models = [ParsedEvent(**event) for event in events]
        
        return EventsResponse(events=event_models, count=len(event_models))
        
    except Exception as e:
        logger.error(f"Error getting events: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve events")


@app.get("/status")
async def get_status():
    """Get processing status"""
    try:
        raw_articles = await load_raw_news()
        parsed_events = await load_parsed_events()
        
        processed_urls = {event.get("source_url", "") for event in parsed_events}
        unprocessed_count = len([
            article for article in raw_articles 
            if article.get("url", "") not in processed_urls
        ])
        
        return {
            "raw_articles_count": len(raw_articles),
            "parsed_events_count": len(parsed_events),
            "unprocessed_count": unprocessed_count,
            "last_poll": datetime.now().isoformat(),
            "poll_interval_seconds": POLL_INTERVAL
        }
        
    except Exception as e:
        logger.error(f"Error getting status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get status")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
