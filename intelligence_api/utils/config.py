import os
from typing import Optional


class Config:
    # Database configuration
    MONGODB_URL: str = os.getenv('MONGODB_URL', 'mongodb://admin:password@mongodb:27017/')
    MONGODB_DATABASE: str = os.getenv('MONGODB_DATABASE', 'nextier_signal')
    
    # RabbitMQ configuration
    RABBITMQ_URL: str = os.getenv('RABBITMQ_URL', 'amqp://admin:password@rabbitmq:5672/')
    RABBITMQ_QUEUE_ARTICLES: str = os.getenv('RABBITMQ_QUEUE_ARTICLES', 'scraped_articles')
    RABBITMQ_QUEUE_EVENTS: str = os.getenv('RABBITMQ_QUEUE_EVENTS', 'parsed_events')
    
    # LLM configuration
    OLLAMA_URL: str = os.getenv('OLLAMA_URL', 'http://host.docker.internal:11434/api/generate')
    OLLAMA_MODEL: str = os.getenv('OLLAMA_MODEL', 'llama3.2:latest')
    SYSTEM_PROMPT: str = os.getenv(
        'SYSTEM_PROMPT', 
        "You are a Nextier Conflict Analyst. Extract Event_Type, State, LGA, and Severity from this text. Return strictly valid JSON."
    )
    
    # Processing configuration
    POLL_INTERVAL: int = int(os.getenv('POLL_INTERVAL', '30'))
    MAX_CONCURRENT_PROCESSING: int = int(os.getenv('MAX_CONCURRENT_PROCESSING', '5'))
    
    # HTTP configuration
    REQUEST_TIMEOUT: int = int(os.getenv('REQUEST_TIMEOUT', '30'))
    MAX_CONNECTIONS: int = int(os.getenv('MAX_CONNECTIONS', '100'))
    MAX_KEEPALIVE_CONNECTIONS: int = int(os.getenv('MAX_KEEPALIVE_CONNECTIONS', '20'))
    
    # CORS configuration
    ALLOWED_ORIGINS: list = os.getenv('ALLOWED_ORIGINS', 'http://localhost:3000,http://localhost:8080,https://nextier.example.com').split(',')
    
    # Service configuration
    SERVICE_NAME: str = os.getenv('SERVICE_NAME', 'intelligence-api')
    LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')
    
    @classmethod
    def validate(cls) -> bool:
        """Validate configuration parameters"""
        required_vars = [
            'MONGODB_URL',
            'RABBITMQ_URL',
            'OLLAMA_URL'
        ]
        
        for var in required_vars:
            if not getattr(cls, var):
                raise ValueError(f"Required environment variable {var} is not set")
        
        return True
