from typing import List, Dict, Any, Optional
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from scraper.models import Article, ArticleCreate
from scraper.utils import get_logger, Config

logger = get_logger(__name__)


class MongoDBRepository:
    def __init__(self):
        self.client = None
        self.db = None
        self.collection = None
        self._connect()
    
    def _connect(self):
        """Connect to MongoDB"""
        try:
            self.client = MongoClient(Config.MONGODB_URL, serverSelectionTimeoutMS=2000)
            # Test connection
            self.client.server_info()
            self.db = self.client[Config.MONGODB_DATABASE]
            self.collection = self.db['articles']
            logger.info("Connected to MongoDB")
            return True
        except PyMongoError as e:
            logger.warning("Failed to connect to MongoDB (demo mode active)", error=str(e))
            return False
    
    def save_articles(self, articles: List[Dict[str, Any]]) -> bool:
        """Save articles to MongoDB, avoiding duplicates"""
        if not self.collection:
            logger.warning("Skipping save (demo mode active)")
            return True
            
        try:
            saved_count = 0
            for article in articles:
                result = self.collection.update_one(
                    {'url': article['url']},
                    {'$setOnInsert': article},
                    upsert=True
                )
                if result.upserted_id:
                    saved_count += 1
            
            logger.info(f"Saved {saved_count} new articles to MongoDB")
            return True
        except PyMongoError as e:
            logger.error("Failed to save articles to MongoDB", error=str(e))
            return False
    
    def get_articles(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Retrieve articles from MongoDB"""
        if not self.collection:
            logger.warning("Using demo data (demo mode active)")
            # Return some demo data
            return [
                {
                    "_id": "demo1",
                    "title": "Demo Article 1",
                    "content": "This is a demo article for testing without MongoDB",
                    "url": "https://example.com/demo1",
                    "source": "Demo Source",
                    "scraped_at": "2026-01-10T00:00:00Z"
                },
                {
                    "_id": "demo2",
                    "title": "Demo Article 2",
                    "content": "Another demo article for testing",
                    "url": "https://example.com/demo2",
                    "source": "Demo Source",
                    "scraped_at": "2026-01-10T00:00:00Z"
                }
            ]
            
        try:
            articles = list(self.collection.find().sort('scraped_at', -1).limit(limit))
            # Convert ObjectId to string for JSON serialization
            for article in articles:
                if '_id' in article:
                    article['_id'] = str(article['_id'])
            logger.info("Retrieved articles from MongoDB", count=len(articles))
            return articles
        except PyMongoError as e:
            logger.error("Failed to retrieve articles from MongoDB", error=str(e))
            return []
    
    def get_article_by_url(self, url: str) -> Optional[Dict[str, Any]]:
        """Get a single article by URL"""
        try:
            article = self.collection.find_one({'url': url})
            if article and '_id' in article:
                article['_id'] = str(article['_id'])
            return article
        except PyMongoError as e:
            logger.error("Failed to get article by URL", url=url, error=str(e))
            return None
    
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
