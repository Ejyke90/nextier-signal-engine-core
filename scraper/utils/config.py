import os
from typing import Optional


class Config:
    # Database configuration
    MONGODB_URL: str = os.getenv('MONGODB_URL', 'mongodb://admin:password@mongodb:27017/')
    MONGODB_DATABASE: str = os.getenv('MONGODB_DATABASE', 'nextier_signal')
    
    # RabbitMQ configuration
    RABBITMQ_URL: str = os.getenv('RABBITMQ_URL', 'amqp://admin:password@rabbitmq:5672/')
    RABBITMQ_QUEUE_ARTICLES: str = os.getenv('RABBITMQ_QUEUE_ARTICLES', 'scraped_articles')
    
    # Scraping configuration - RSS feeds (primary) with web scraping fallback
    NEWS_SOURCES: list = [
        {
            'name': 'Vanguard News',
            'rss_url': 'https://www.vanguardngr.com/feed/',
            'web_url': 'https://www.vanguardngr.com/',
            'selectors': ['article', '.entry-title a', '.post'],
            'type': 'rss'  # Prefer RSS
        },
        {
            'name': 'The Guardian Nigeria',
            'rss_url': 'https://guardian.ng/feed/',
            'web_url': 'https://guardian.ng/',
            'selectors': ['article', '.entry-title a'],
            'type': 'rss'
        },
        {
            'name': 'Premium Times',
            'rss_url': 'https://www.premiumtimesng.com/feed',
            'web_url': 'https://www.premiumtimesng.com/',
            'selectors': ['article', '.entry-title a'],
            'type': 'rss'
        },
        {
            'name': 'Punch Nigeria',
            'rss_url': 'https://punchng.com/feed/',
            'web_url': 'https://punchng.com/',
            'selectors': ['article', '.entry-title a'],
            'type': 'rss'
        },
        {
            'name': 'The Cable',
            'rss_url': None,  # No RSS available
            'web_url': 'https://www.thecable.ng/',
            'selectors': ['.post-title a', 'article', '.entry-title a'],
            'type': 'web'  # Web scraping only
        },
        {
            'name': 'Sahara Reporters',
            'rss_url': 'https://saharareporters.com/rss',
            'web_url': 'https://saharareporters.com/',
            'selectors': ['.views-field-title a', 'article h2 a', '.field-content a'],
            'type': 'rss'
        },
        {
            'name': 'Daily Post Nigeria',
            'rss_url': 'https://dailypost.ng/feed/',
            'web_url': 'https://dailypost.ng/',
            'selectors': ['article', '.entry-title a'],
            'type': 'rss'
        },
        {
            'name': 'Channels TV',
            'rss_url': 'https://www.channelstv.com/feed/',
            'web_url': 'https://www.channelstv.com/',
            'selectors': ['article', '.entry-title a'],
            'type': 'rss'
        },
        {
            'name': 'Leadership News',
            'rss_url': 'https://leadership.ng/feed/',
            'web_url': 'https://leadership.ng/',
            'selectors': ['article', '.entry-title a'],
            'type': 'rss'
        },
        {
            'name': 'Tribune Online',
            'rss_url': 'https://tribuneonlineng.com/feed/',
            'web_url': 'https://tribuneonlineng.com/',
            'selectors': ['article', '.entry-title a'],
            'type': 'rss'
        }
    ]
    
    # Legacy config for backward compatibility
    PREMIUM_TIMES_URL: str = os.getenv('PREMIUM_TIMES_URL', 'https://www.vanguardngr.com/category/news/')
    POLL_INTERVAL: int = int(os.getenv('POLL_INTERVAL', '30'))
    MAX_ARTICLES_PER_SCRAPE: int = int(os.getenv('MAX_ARTICLES_PER_SCRAPE', '10'))
    MAX_ARTICLES_PER_SOURCE: int = int(os.getenv('MAX_ARTICLES_PER_SOURCE', '5'))
    
    # HTTP configuration
    REQUEST_TIMEOUT: int = int(os.getenv('REQUEST_TIMEOUT', '10'))
    MAX_CONNECTIONS: int = int(os.getenv('MAX_CONNECTIONS', '100'))
    MAX_KEEPALIVE_CONNECTIONS: int = int(os.getenv('MAX_KEEPALIVE_CONNECTIONS', '20'))
    
    # CORS configuration
    ALLOWED_ORIGINS: list = os.getenv('ALLOWED_ORIGINS', 'http://localhost:3000,http://localhost:5173,http://localhost:8080,https://nextier.example.com').split(',')
    
    # Service configuration
    SERVICE_NAME: str = os.getenv('SERVICE_NAME', 'scraper')
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
