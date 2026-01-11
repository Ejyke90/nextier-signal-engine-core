from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import asyncio
import httpx
from datetime import datetime
from bs4 import BeautifulSoup
from scraper.utils import get_logger, Config

logger = get_logger(__name__)

# Global semaphore for connection limiting
GLOBAL_SEMAPHORE = asyncio.Semaphore(Config.MAX_CONCURRENT_CONNECTIONS)

class BaseScraper(ABC):
    """Abstract base class for all scrapers, defining the interface and common functionality."""
    
    def __init__(self, client: Optional[httpx.AsyncClient] = None):
        """Initialize with an optional shared HTTP client."""
        self.client = client or httpx.AsyncClient(
            timeout=Config.REQUEST_TIMEOUT,
            limits=httpx.Limits(
                max_connections=Config.MAX_CONNECTIONS,
                max_keepalive_connections=Config.MAX_KEEPALIVE_CONNECTIONS
            ),
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            },
            follow_redirects=True
        )
    
    async def fetch_page(self, url: str, allow_failure: bool = True) -> Optional[str]:
        """
        Fetch a web page with semaphore limiting.
        
        Args:
            url: URL to fetch
            allow_failure: If True, return None on error instead of raising exception
        
        Returns:
            HTML content or None if failed and allow_failure=True
        """
        async with GLOBAL_SEMAPHORE:
            try:
                response = await self.client.get(url, timeout=15.0)
                response.raise_for_status()
                return response.text
            except Exception as e:
                logger.warning(f"Error fetching page from {url}: {str(e)}")
                return None if allow_failure else None
    
    @abstractmethod
    async def scrape(self, source: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Scrape articles from the given source.
        
        Args:
            source: Dictionary with source configuration (name, url, etc.)
        
        Returns:
            List of scraped articles
        """
        pass
    
    @abstractmethod
    def extract_features(self, content: str, source_name: str) -> Dict[str, Any]:
        """
        Extract structured features from raw content relevant to NNVCD.
        
        Args:
            content: Raw text or HTML content of the article
            source_name: Name of the source for context
        
        Returns:
            Dictionary with extracted features (conflict type, casualties, geography)
        """
        return {
            'conflict_type': 'Unknown',
            'casualties': {
                'fatalities': 0,
                'injured': 0,
                'kidnap_victims': 0,
                'gender_data': {'male': 0, 'female': 0, 'tbd': 0}
            },
            'geography': {
                'state': 'Unknown',
                'lga': 'Unknown',
                'community': 'Unknown'
            }
        }
    
    async def close(self) -> None:
        """Close the HTTP client if it exists."""
        if self.client:
            await self.client.aclose()
            logger.info(f"Closed HTTP client for {self.__class__.__name__}")
