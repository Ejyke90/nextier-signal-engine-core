import pandas as pd
from typing import List, Dict, Any, Optional
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from ..models import RiskSignal, RiskSignalCreate
from ..utils import get_logger, Config

logger = get_logger(__name__)


class MongoDBRepository:
    def __init__(self):
        self.client = None
        self.db = None
        self.parsed_events_collection = None
        self.risk_signals_collection = None
        self.economic_data_collection = None
        self.articles_collection = None
        self._connect()
    
    def _connect(self) -> None:
        """Connect to MongoDB"""
        try:
            self.client = MongoClient(Config.MONGODB_URL)
            self.db = self.client[Config.MONGODB_DATABASE]
            self.parsed_events_collection = self.db.parsed_events
            self.risk_signals_collection = self.db.risk_signals
            self.economic_data_collection = self.db.economic_data
            self.articles_collection = self.db.articles
            logger.info("Connected to MongoDB", database=Config.MONGODB_DATABASE)
        except Exception as e:
            logger.error("Failed to connect to MongoDB", error=str(e))
            raise
    
    def get_parsed_events(self, limit: int = 1000) -> List[Dict[str, Any]]:
        """Get parsed events from MongoDB"""
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
    
    def get_articles_count(self) -> int:
        """Get total count of articles in MongoDB"""
        try:
            count = self.articles_collection.count_documents({})
            logger.info("Retrieved articles count", count=count)
            return count
        except PyMongoError as e:
            logger.error("Failed to retrieve articles count", error=str(e))
            return 0
        """Get economic data from MongoDB as DataFrame"""
        try:
            data = list(self.economic_data_collection.find())
            if data:
                # Convert ObjectId to string and remove it from DataFrame
                for item in data:
                    if '_id' in item:
                        item['_id'] = str(item['_id'])
                df = pd.DataFrame(data)
                logger.info("Retrieved economic data", rows=len(df))
                return df
            else:
                logger.warning("No economic data found in MongoDB")
                return pd.DataFrame()
        except PyMongoError as e:
            logger.error("Failed to retrieve economic data", error=str(e))
            return pd.DataFrame()
    
    def save_risk_signals(self, signals: List[Dict[str, Any]]) -> bool:
        """Save risk signals to MongoDB"""
        try:
            if signals:
                # Check for duplicates based on source_url
                for signal in signals:
                    self.risk_signals_collection.update_one(
                        {'source_url': signal['source_url']},
                        {'$set': signal},
                        upsert=True
                    )
                logger.info("Saved risk signals", count=len(signals))
            return True
        except PyMongoError as e:
            logger.error("Failed to save risk signals", error=str(e))
            return False
    
    def get_risk_signals(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Retrieve risk signals from MongoDB"""
        try:
            signals = list(self.risk_signals_collection.find().sort('calculated_at', -1).limit(limit))
            # Convert ObjectId to string for JSON serialization
            for signal in signals:
                if '_id' in signal:
                    signal['_id'] = str(signal['_id'])
            logger.info("Retrieved risk signals", count=len(signals))
            return signals
        except PyMongoError as e:
            logger.error("Failed to retrieve risk signals", error=str(e))
            return []
    
    def get_prediction_status(self) -> Dict[str, Any]:
        """Get prediction statistics"""
        try:
            events_count = self.parsed_events_collection.count_documents({})
            signals_count = self.risk_signals_collection.count_documents({})
            econ_data_count = self.economic_data_collection.count_documents({})
            
            return {
                "parsed_events_count": events_count,
                "risk_signals_count": signals_count,
                "economic_data_points": econ_data_count
            }
        except PyMongoError as e:
            logger.error("Failed to get prediction status", error=str(e))
            return {
                "parsed_events_count": 0,
                "risk_signals_count": 0,
                "economic_data_points": 0
            }
    
    def initialize_economic_data(self, csv_file_path: str) -> bool:
        """Initialize economic data from CSV file"""
        try:
            df = pd.read_csv(csv_file_path)
            
            # Clear existing data
            self.economic_data_collection.delete_many({})
            
            # Insert new data
            data = df.to_dict('records')
            if data:
                self.economic_data_collection.insert_many(data)
                logger.info("Initialized economic data", count=len(data))
                return True
            else:
                logger.warning("No data found in CSV file")
                return False
                
        except Exception as e:
            logger.error("Failed to initialize economic data", error=str(e))
            return False
    
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
        try:
            if self.client:
                self.client.close()
                logger.info("Closed MongoDB connection")
        except Exception as e:
            logger.error("Error closing MongoDB connection", error=str(e))
    
    def get_categorized_articles_count(self) -> int:
        """Get count of categorized articles"""
        try:
            count = self.articles_collection.count_documents({"category": {"$exists": True}})
            logger.info("Retrieved categorized articles count", count=count)
            return count
        except PyMongoError as e:
            logger.error("Failed to retrieve categorized articles count", error=str(e))
            return 0
    
    def get_uncategorized_articles(self) -> List[Dict]:
        """Get uncategorized articles"""
        try:
            articles = list(self.articles_collection.find({"category": {"$exists": False}}))
            # Convert ObjectId to string for JSON serialization
            for article in articles:
                if '_id' in article:
                    article['_id'] = str(article['_id'])
            logger.info("Retrieved uncategorized articles", count=len(articles))
            return articles
        except PyMongoError as e:
            logger.error("Failed to retrieve uncategorized articles", error=str(e))
            return []
    
    def get_economic_data(self) -> pd.DataFrame:
        """Get economic data from MongoDB as DataFrame"""
        try:
            data = list(self.economic_data_collection.find())
            if data:
                # Convert ObjectId to string and remove it from DataFrame
                for item in data:
                    if '_id' in item:
                        item['_id'] = str(item['_id'])
                df = pd.DataFrame(data)
                logger.info("Retrieved economic data", rows=len(df))
                return df
            else:
                logger.warning("No economic data found in MongoDB")
                return pd.DataFrame()
        except PyMongoError as e:
            logger.error("Failed to retrieve economic data", error=str(e))
            return pd.DataFrame()
