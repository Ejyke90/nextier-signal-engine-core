from typing import List, Dict, Any, Optional
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from bson import ObjectId
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
            self.raw_articles_collection = self.db.raw_articles
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
                result = self.parsed_events_collection.insert_many(events)
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
    
    def get_uncategorized_articles(self) -> List[Dict[str, Any]]:
        """Get articles that haven't been categorized yet"""
        try:
            uncategorized = list(self.raw_articles_collection.find(
                {"features.conflict_type": "Unknown"}
            ).sort('scraped_at', -1))
            
            # Convert ObjectId to string
            for article in uncategorized:
                if '_id' in article:
                    article['_id'] = str(article['_id'])
            
            logger.info("Retrieved uncategorized articles", count=len(uncategorized))
            return uncategorized
            
        except PyMongoError as e:
            logger.error("Failed to get uncategorized articles", error=str(e))
            return []
    
    def update_article_category(self, article_id: str, category: str, confidence: int = 0) -> bool:
        """Update the conflict_type and confidence of an article"""
        try:
            result = self.raw_articles_collection.update_one(
                {"_id": ObjectId(article_id)},
                {"$set": {"features.conflict_type": category, "features.confidence": confidence}}
            )
            
            if result.modified_count > 0:
                logger.info("Updated article category", article_id=article_id, category=category, confidence=confidence)
                return True
            else:
                logger.warning("No article updated", article_id=article_id)
                return False
                
        except PyMongoError as e:
            logger.error("Failed to update article category", article_id=article_id, error=str(e))
            return False
    
    def get_categorization_stats(self) -> List[Dict[str, Any]]:
        """Get categorization statistics with average confidence"""
        try:
            # Aggregate articles by conflict_type
            pipeline = [
                {"$match": {"features.conflict_type": {"$ne": "Unknown"}}},
                {"$group": {
                    "_id": "$features.conflict_type",
                    "count": {"$sum": 1},
                    "avg_confidence": {"$avg": "$features.confidence"}
                }},
                {"$project": {
                    "category": "$_id",
                    "count": 1,
                    "avg_confidence": 1,
                    "_id": 0
                }}
            ]
            
            results = list(self.raw_articles_collection.aggregate(pipeline))
            
            # Ensure all categories are represented
            categories = ["Banditry", "Kidnapping", "Gunmen Violence", "Farmer-Herder Clashes"]
            stats = []
            
            for cat in categories:
                existing = next((r for r in results if r["category"] == cat), None)
                if existing:
                    stats.append({
                        "category": cat,
                        "count": existing["count"],
                        "confidence": existing["avg_confidence"] or 0
                    })
                else:
                    stats.append({
                        "category": cat,
                        "count": 0,
                        "confidence": 0
                    })
            
            logger.info("Retrieved categorization stats", stats=stats)
            return stats
            
        except PyMongoError as e:
            logger.error("Failed to get categorization stats", error=str(e))
            return []
    
    def get_categorization_audit(self) -> Dict[str, Any]:
        """Get comprehensive categorization audit data"""
        try:
            total_articles = self.raw_articles_collection.count_documents({})
            processed_articles = self.raw_articles_collection.count_documents({"features.conflict_type": {"$ne": "Unknown"}})
            remaining_articles = total_articles - processed_articles
            
            # Get categories stats
            categories_stats = self.get_categorization_stats()
            categories = {stat["category"]: {"count": stat["count"], "avg_confidence": stat["confidence"]} for stat in categories_stats}
            
            # Get recent confidence logs (last 10 categorized articles)
            recent_articles = list(self.raw_articles_collection.find(
                {"features.conflict_type": {"$ne": "Unknown"}},
                {"features.conflict_type": 1, "features.confidence": 1, "scraped_at": 1}
            ).sort("scraped_at", -1).limit(10))
            
            confidence_logs = []
            for doc in recent_articles:
                confidence_logs.append({
                    "article_id": str(doc["_id"]),
                    "category": doc["features"]["conflict_type"],
                    "confidence": doc["features"].get("confidence", 0),
                    "timestamp": doc.get("scraped_at", "")
                })
            
            audit_data = {
                "total_articles": total_articles,
                "processed_articles": processed_articles,
                "remaining_articles": remaining_articles,
                "categories": categories,
                "confidence_logs": confidence_logs
            }
            
            logger.info("Retrieved categorization audit", audit_data=audit_data)
            return audit_data
            
        except PyMongoError as e:
            logger.error("Failed to get categorization audit", error=str(e))
            return {}
    
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
