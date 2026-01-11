import json
import pika
from pika.exceptions import AMQPError
from typing import List, Dict, Any
from scraper.utils import get_logger, Config

logger = get_logger(__name__)


class MessageBrokerService:
    def __init__(self):
        self.connection = None
        self.channel = None
        self._connect()
    
    def _connect(self) -> bool:
        """Connect to RabbitMQ"""
        try:
            parameters = pika.URLParameters(Config.RABBITMQ_URL)
            self.connection = pika.BlockingConnection(parameters)
            self.channel = self.connection.channel()
            
            # Declare queue
            self.channel.queue_declare(queue=Config.RABBITMQ_QUEUE_ARTICLES, durable=True)
            
            logger.info("Connected to RabbitMQ")
            return True
        except AMQPError as e:
            logger.warning("Failed to connect to RabbitMQ (demo mode active)", error=str(e))
            return False
    
    def publish_articles(self, articles: List[Dict[str, Any]]) -> bool:
        """Publish articles to message broker"""
        if not self.channel:
            logger.warning("Skipping publish (demo mode active)")
            return True
            
        try:
            for article in articles:
                message = json.dumps(article)
                self.channel.basic_publish(
                    exchange='',
                    routing_key=Config.RABBITMQ_QUEUE_ARTICLES,
                    body=message,
                    properties=pika.BasicProperties(
                        delivery_mode=2,  # make message persistent
                    )
                )
            logger.info(f"Published {len(articles)} articles to RabbitMQ")
            return True
        except AMQPError as e:
            logger.error("Failed to publish articles to RabbitMQ", error=str(e))
            return False
    
    def health_check(self) -> bool:
        """Check RabbitMQ connection health"""
        try:
            if self.connection and self.connection.is_open:
                return True
            return False
        except Exception as e:
            logger.error("RabbitMQ health check failed", error=str(e))
            return False
    
    def close(self) -> None:
        """Close RabbitMQ connection"""
        if self.connection and self.connection.is_open:
            self.connection.close()
            logger.info("Closed RabbitMQ connection")
