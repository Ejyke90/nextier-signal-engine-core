import os
from typing import Optional


class Config:
    # Database configuration
    MONGODB_URL: str = os.getenv('MONGODB_URL', 'mongodb://admin:password@mongodb:27017/')
    MONGODB_DATABASE: str = os.getenv('MONGODB_DATABASE', 'nextier_signal')
    
    # RabbitMQ configuration
    RABBITMQ_URL: str = os.getenv('RABBITMQ_URL', 'amqp://admin:password@rabbitmq:5672/')
    RABBITMQ_QUEUE_ARTICLES: str = os.getenv('RABBITMQ_QUEUE_ARTICLES', 'scraped_articles')
    
    # Scraping configuration
    PREMIUM_TIMES_URL: str = os.getenv('PREMIUM_TIMES_URL', 'https://premiumtimesng.com/')
    POLL_INTERVAL: int = int(os.getenv('POLL_INTERVAL', '30'))
    MAX_ARTICLES_PER_SCRAPE: int = int(os.getenv('MAX_ARTICLES_PER_SCRAPE', '10'))
    
    # HTTP configuration
    REQUEST_TIMEOUT: int = int(os.getenv('REQUEST_TIMEOUT', '10'))
    MAX_CONNECTIONS: int = int(os.getenv('MAX_CONNECTIONS', '100'))
    MAX_KEEPALIVE_CONNECTIONS: int = int(os.getenv('MAX_KEEPALIVE_CONNECTIONS', '20'))
    
    # CORS configuration
    ALLOWED_ORIGINS: list = os.getenv('ALLOWED_ORIGINS', 'http://localhost:3000,http://localhost:8080,https://nextier.example.com').split(',')
    
    # Service configuration
    SERVICE_NAME: str = os.getenv('SERVICE_NAME', 'scraper')
    LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')
    
    @classmethod
    def validate(cls) -> bool:
        """Validate configuration parameters"""
        required_vars = [
            'MONGODB_URL',
            'RABBITMQ_URL',
            'PREMIUM_TIMES_URL'
        ]
        
        for var in required_vars:
            if not getattr(cls, var):
                raise ValueError(f"Required environment variable {var} is not set")
        
        return True
