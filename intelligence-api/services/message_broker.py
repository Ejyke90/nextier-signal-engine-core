import json
import pika
from pika.exceptions import AMQPError
from typing import List, Dict, Any
from ..utils import get_logger, Config

logger = get_logger(__name__)


class MessageBrokerService:
    def __init__(self):
        self.connection = None
        self.channel = None
        self._connect()
    
    def _connect(self):
        """Connect to RabbitMQ"""
        try:
            parameters = pika.URLParameters(Config.RABBITMQ_URL)
            self.connection = pika.BlockingConnection(parameters)
            self.channel = self.connection.channel()
            
            # Declare queues
            self.channel.queue_declare(queue=Config.RABBITMQ_QUEUE_ARTICLES, durable=True)
            self.channel.queue_declare(queue=Config.RABBITMQ_QUEUE_EVENTS, durable=True)
            
            logger.info("Connected to RabbitMQ")
            return True
        except AMQPError as e:
            logger.warning("Failed to connect to RabbitMQ (demo mode active)", error=str(e))
            return False
        except Exception as e:
            logger.error("Failed to connect to RabbitMQ", error=str(e))
            raise
    
    def consume_articles(self, callback) -> None:
        """Consume articles from message broker"""
        if not self.channel:
            logger.warning("Skipping consume (demo mode active)")
            return
            
        try:
            def wrapper(ch, method, properties, body):
                try:
                    article = json.loads(body)
                    callback(article)
                    ch.basic_ack(delivery_tag=method.delivery_tag)
                except Exception as e:
                    logger.error("Error processing message", error=str(e))
                    ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
            
            self.channel.basic_qos(prefetch_count=1)
            self.channel.basic_consume(
                queue=Config.RABBITMQ_QUEUE_ARTICLES,
                on_message_callback=wrapper
            )
            
            logger.info("Started consuming articles from RabbitMQ")
            self.channel.start_consuming()
        except AMQPError as e:
            logger.error("Failed to consume articles from RabbitMQ", error=str(e))
            raise
    
    def publish_events(self, events: List[Dict[str, Any]]) -> bool:
        """Publish parsed events to message broker"""
        if not self.channel:
            logger.warning("Skipping publish (demo mode active)")
            return True
            
        try:
            for event in events:
                message = json.dumps(event)
                self.channel.basic_publish(
                    exchange='',
                    routing_key=Config.RABBITMQ_QUEUE_EVENTS,
                    body=message,
                    properties=pika.BasicProperties(
                        delivery_mode=2,  # make message persistent
                    )
                )
            logger.info(f"Published {len(events)} events to RabbitMQ")
            return True
        except AMQPError as e:
            logger.error("Failed to publish events to RabbitMQ", error=str(e))
            return False
    
    def start_consuming(self) -> None:
        """Start consuming messages"""
        try:
            self.channel.start_consuming()
        except KeyboardInterrupt:
            self.stop_consuming()
            logger.info("Stopped consuming messages")
        except Exception as e:
            logger.error("Error while consuming messages", error=str(e))
            raise
    
    def stop_consuming(self) -> None:
        """Stop consuming messages"""
        if self.channel:
            self.channel.stop_consuming()
    
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
