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
    
    def _connect(self) -> None:
        """Connect to RabbitMQ"""
        try:
            parameters = pika.URLParameters(Config.RABBITMQ_URL)
            self.connection = pika.BlockingConnection(parameters)
            self.channel = self.connection.channel()
            
            # Declare queues
            self.channel.queue_declare(queue=Config.RABBITMQ_QUEUE_EVENTS, durable=True)
            self.channel.queue_declare(queue=Config.RABBITMQ_QUEUE_SIGNALS, durable=True)
            
            logger.info("Connected to RabbitMQ", 
                       events_queue=Config.RABBITMQ_QUEUE_EVENTS,
                       signals_queue=Config.RABBITMQ_QUEUE_SIGNALS)
        except Exception as e:
            logger.error("Failed to connect to RabbitMQ", error=str(e))
            raise
    
    def consume_events(self, callback) -> None:
        """Consume parsed events from message broker"""
        try:
            def wrapper(ch, method, properties, body):
                try:
                    event = json.loads(body)
                    callback(event)
                    ch.basic_ack(delivery_tag=method.delivery_tag)
                except Exception as e:
                    logger.error("Error processing message", error=str(e))
                    ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
            
            self.channel.basic_qos(prefetch_count=1)
            self.channel.basic_consume(
                queue=Config.RABBITMQ_QUEUE_EVENTS,
                on_message_callback=wrapper
            )
            
            logger.info("Started consuming events", queue=Config.RABBITMQ_QUEUE_EVENTS)
            
        except AMQPError as e:
            logger.error("Failed to setup event consumer", error=str(e))
            raise
    
    def publish_signals(self, signals: List[Dict[str, Any]]) -> bool:
        """Publish risk signals to message broker"""
        try:
            for signal in signals:
                message = json.dumps(signal)
                self.channel.basic_publish(
                    exchange='',
                    routing_key=Config.RABBITMQ_QUEUE_SIGNALS,
                    body=message,
                    properties=pika.BasicProperties(
                        delivery_mode=2,  # Make message persistent
                    )
                )
            
            logger.info("Published risk signals to message broker", count=len(signals))
            return True
        except AMQPError as e:
            logger.error("Failed to publish risk signals to message broker", error=str(e))
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
