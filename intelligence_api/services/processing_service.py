import asyncio
from datetime import datetime
from typing import Dict, Any
from ..utils import get_logger, Config
from ..repositories import MongoDBRepository
from ..services import LLMService, MessageBrokerService

logger = get_logger(__name__)


class ProcessingService:
    def __init__(self, mongodb_repo: MongoDBRepository, llm_service: LLMService, message_broker: MessageBrokerService):
        self.mongodb_repo = mongodb_repo
        self.llm_service = llm_service
        self.message_broker = message_broker
        self._running = False
    
    async def process_news_articles(self) -> Dict[str, Any]:
        """Main processing function - process unprocessed articles"""
        try:
            logger.info("Starting news processing cycle")
            
            # Get unprocessed articles
            unprocessed_articles = self.mongodb_repo.get_unprocessed_articles()
            
            if not unprocessed_articles:
                logger.info("No unprocessed articles found")
                return {
                    "status": "success",
                    "articles_processed": 0,
                    "events_created": 0,
                    "message": "No new articles to process"
                }
            
            logger.info("Processing articles", count=len(unprocessed_articles))
            
            # Process articles with LLM
            parsed_events = await self.llm_service.process_articles_batch(unprocessed_articles)
            
            if parsed_events:
                # Save to MongoDB
                db_success = self.mongodb_repo.save_parsed_events(parsed_events)
                
                # Publish to message broker
                mq_success = self.message_broker.publish_events(parsed_events)
                
                if db_success and mq_success:
                    logger.info("Successfully processed and published events", count=len(parsed_events))
                    return {
                        "status": "success",
                        "articles_processed": len(unprocessed_articles),
                        "events_created": len(parsed_events),
                        "message": f"Successfully processed {len(parsed_events)} events"
                    }
                else:
                    logger.warning("Partial success - some operations failed")
                    return {
                        "status": "partial",
                        "articles_processed": len(unprocessed_articles),
                        "events_created": len(parsed_events),
                        "message": "Events processed but some operations failed"
                    }
            else:
                logger.warning("No events were successfully parsed")
                return {
                    "status": "warning",
                    "articles_processed": len(unprocessed_articles),
                    "events_created": 0,
                    "message": "No events were successfully parsed"
                }
                
        except Exception as e:
            logger.error("Error in processing cycle", error=str(e))
            return {
                "status": "error",
                "articles_processed": 0,
                "events_created": 0,
                "message": f"Processing failed: {str(e)}"
            }
    
    async def start_background_processor(self) -> None:
        """Start background processing loop"""
        self._running = True
        logger.info("Starting background processor")
        
        while self._running:
            try:
                result = await self.process_news_articles()
                await asyncio.sleep(Config.POLL_INTERVAL)
            except Exception as e:
                logger.error("Error in background processor", error=str(e))
                await asyncio.sleep(Config.POLL_INTERVAL)
    
    def stop_background_processor(self) -> None:
        """Stop background processing loop"""
        self._running = False
        logger.info("Stopping background processor")
    
    async def get_processing_status(self) -> Dict[str, Any]:
        """Get current processing status"""
        try:
            status = self.mongodb_repo.get_processing_status()
            status.update({
                "last_poll": datetime.now().isoformat(),
                "poll_interval_seconds": Config.POLL_INTERVAL,
                "background_processor_running": self._running
            })
            return status
        except Exception as e:
            logger.error("Error getting processing status", error=str(e))
            return {
                "raw_articles_count": 0,
                "parsed_events_count": 0,
                "unprocessed_count": 0,
                "last_poll": datetime.now().isoformat(),
                "poll_interval_seconds": Config.POLL_INTERVAL,
                "background_processor_running": self._running
            }
