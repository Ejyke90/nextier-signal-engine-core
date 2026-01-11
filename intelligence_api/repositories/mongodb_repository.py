from typing import List, Dict, Any, Optional
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from ..models import ParsedEvent, EventCreate
from ..utils import get_logger, Config

logger = get_logger(__name__)


class MongoDBRepository:
    def __init__(self):
        self.client = None
        self.db = None
        self.raw_articles_collection = None
        self.parsed_events_collection = None
        self._connect()
    
    def _connect(self) -> None:
        """Connect to MongoDB"""
        try:
            self.client = MongoClient(Config.MONGODB_URL)
            self.db = self.client[Config.MONGODB_DATABASE]
            self.raw_articles_collection = self.db.articles  # Match scraper collection name
            self.parsed_events_collection = self.db.parsed_events
            logger.info("Connected to MongoDB", database=Config.MONGODB_DATABASE)
        except Exception as e:
            logger.error("Failed to connect to MongoDB", error=str(e))
            raise
    
    def get_unprocessed_articles(self) -> List[Dict[str, Any]]:
        """Get articles that haven't been processed yet"""
        try:
            # Get all processed URLs
            processed_urls = set()
            processed_events = self.parsed_events_collection.find({}, {"source_url": 1})
            for event in processed_events:
                processed_urls.add(event.get("source_url", ""))
            
            # Get unprocessed articles
            unprocessed = list(self.raw_articles_collection.find(
                {"url": {"$nin": list(processed_urls)}}
            ).sort('scraped_at', -1))
            
            # Convert ObjectId to string
            for article in unprocessed:
                if '_id' in article:
                    article['_id'] = str(article['_id'])
            
            logger.info("Retrieved unprocessed articles", count=len(unprocessed))
            return unprocessed
            
        except PyMongoError as e:
            logger.error("Failed to get unprocessed articles", error=str(e))
            return []
    
    def save_parsed_events(self, events: List[Dict[str, Any]]) -> bool:
        """Save parsed events to MongoDB"""
        try:
            if events:
                # Remove any _id fields before inserting (MongoDB will create them)
                events_to_save = []
                for event in events:
                    event_copy = event.copy()
                    if '_id' in event_copy:
                        del event_copy['_id']
                    events_to_save.append(event_copy)
                
                result = self.parsed_events_collection.insert_many(events_to_save)
                logger.info("Saved parsed events", count=len(result.inserted_ids))
            return True
        except PyMongoError as e:
            logger.error("Failed to save parsed events", error=str(e))
            return False
    
    def get_parsed_events(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Retrieve parsed events from MongoDB"""
        try:
            events = list(self.parsed_events_collection.find().sort('parsed_at', -1).limit(limit))
            # Convert ObjectId to string for JSON serialization
            for event in events:
                if '_id' in event:
                    event['_id'] = str(event['_id'])
            logger.info("Retrieved parsed events", count=len(events))
            return events
        except PyMongoError as e:
            logger.error("Failed to retrieve parsed events", error=str(e))
            return []
    
    def get_processing_status(self) -> Dict[str, Any]:
        """Get processing statistics"""
        try:
            raw_count = self.raw_articles_collection.count_documents({})
            parsed_count = self.parsed_events_collection.count_documents({})
            
            # Get processed URLs
            processed_urls = set()
            processed_events = self.parsed_events_collection.find({}, {"source_url": 1})
            for event in processed_events:
                processed_urls.add(event.get("source_url", ""))
            
            unprocessed_count = max(0, raw_count - len(processed_urls))
            
            return {
                "raw_articles_count": raw_count,
                "parsed_events_count": parsed_count,
                "unprocessed_count": unprocessed_count
            }
        except PyMongoError as e:
            logger.error("Failed to get processing status", error=str(e))
            return {
                "raw_articles_count": 0,
                "parsed_events_count": 0,
                "unprocessed_count": 0
            }
    
    def health_check(self) -> bool:
        """Check MongoDB connection health"""
        try:
            self.client.admin.command('ping')
            return True
        except Exception as e:
            logger.error("MongoDB health check failed", error=str(e))
            return False
    
    def close(self) -> None:
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            logger.info("Closed MongoDB connection")
