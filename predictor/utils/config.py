import os
from typing import Optional


class Config:
    # Database configuration
    MONGODB_URL: str = os.getenv('MONGODB_URL', 'mongodb://admin:password@mongodb:27017/')
    MONGODB_DATABASE: str = os.getenv('MONGODB_DATABASE', 'nextier_signal')
    
    # RabbitMQ configuration
    RABBITMQ_URL: str = os.getenv('RABBITMQ_URL', 'amqp://admin:password@rabbitmq:5672/')
    RABBITMQ_QUEUE_EVENTS: str = os.getenv('RABBITMQ_QUEUE_EVENTS', 'parsed_events')
    RABBITMQ_QUEUE_SIGNALS: str = os.getenv('RABBITMQ_QUEUE_SIGNALS', 'risk_signals')
    
    # Processing configuration
    POLL_INTERVAL: int = int(os.getenv('POLL_INTERVAL', '30'))
    MAX_CONCURRENT_PROCESSING: int = int(os.getenv('MAX_CONCURRENT_PROCESSING', '5'))
    
    # Risk scoring configuration
    BASE_RISK_SCORE: int = int(os.getenv('BASE_RISK_SCORE', '30'))
    INFLATION_THRESHOLD: float = float(os.getenv('INFLATION_THRESHOLD', '20.0'))
    FUEL_PRICE_THRESHOLD: float = float(os.getenv('FUEL_PRICE_THRESHOLD', '650.0'))
    
    # CORS configuration
    ALLOWED_ORIGINS: list = os.getenv('ALLOWED_ORIGINS', 'http://localhost:3000,http://localhost:8080,https://nextier.example.com').split(',')
    
    # Service configuration
    SERVICE_NAME: str = os.getenv('SERVICE_NAME', 'predictor')
    LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')
    
    @classmethod
    def validate(cls) -> bool:
        """Validate configuration parameters"""
        required_vars = [
            'MONGODB_URL',
            'RABBITMQ_URL'
        ]
        
        for var in required_vars:
            if not getattr(cls, var):
                raise ValueError(f"Required environment variable {var} is not set")
        
        return True
