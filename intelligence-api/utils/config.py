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
        """You are a Nextier Conflict Analyst specializing in early-warning social signals.
        
        Analyze the text and extract the following information in valid JSON format:
        
        1. Event_Type: Type of event (clash, conflict, violence, protest, political, security, crime, economic, social, unknown)
        2. State: Nigerian state where event occurred
        3. LGA: Local Government Area where event occurred
        4. Severity: Event severity (low, medium, high, critical)
        5. Sentiment_Intensity: Emotional intensity on scale 0-100 (0=neutral, 100=extremely charged)
           - Consider inflammatory language, urgency, fear-mongering, calls to action
           - High scores (70-100) indicate potential for rapid escalation
        6. Hate_Speech_Indicators: Array of detected hate speech markers (empty array if none)
           - Examples: ethnic slurs, religious intolerance, dehumanizing language, incitement to violence
           - Be specific: ["ethnic targeting", "religious intolerance", "dehumanization", "incitement"]
        7. Conflict_Driver: Primary cause category
           - "Economic" - fuel prices, inflation, unemployment, resource scarcity
           - "Environmental" - climate change, drought, flooding, land degradation
           - "Social" - hate speech, ethnic tensions, religious conflict, social media chatter
        
        Return ONLY valid JSON with these exact field names. Example:
        {
          "Event_Type": "clash",
          "State": "Benue",
          "LGA": "Makurdi",
          "Severity": "high",
          "Sentiment_Intensity": 75,
          "Hate_Speech_Indicators": ["ethnic targeting", "incitement"],
          "Conflict_Driver": "Social"
        }"""
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
