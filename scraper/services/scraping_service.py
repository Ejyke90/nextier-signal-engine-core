import json
import httpx
import asyncio
from datetime import datetime
from typing import List, Dict, Any, Optional
from bs4 import BeautifulSoup
from fastapi import HTTPException
from scraper.utils import get_logger, Config
from scraper.utils.rss_parser import RSSParser
from scraper.models import Article
from scraper.services.base_scraper import BaseScraper
from scraper.services.mainstream_media_scraper import MainstreamMediaScraper
from scraper.services.rss_intelligence_scraper import RSSIntelligenceScraper
from scraper.services.verification_layer import VerificationLayer
from scraper.services.deduplication import DeduplicationService

logger = get_logger(__name__)

# Global semaphore to limit concurrent connections and prevent IP blacklisting
GLOBAL_SEMAPHORE = asyncio.Semaphore(Config.MAX_CONCURRENT_CONNECTIONS if hasattr(Config, 'MAX_CONCURRENT_CONNECTIONS') else 10)


class ScrapingService:
    def __init__(self):
        self.client = None
        self.deduplication_service = DeduplicationService()
        self.scrapers = {
            'rss': RSSIntelligenceScraper(),
            'web': MainstreamMediaScraper(),
            'verification': VerificationLayer()
        }
        self._create_client()
    
    def _create_client(self) -> None:
        """Create HTTP client with connection pooling and redirect following"""
        self.client = httpx.AsyncClient(
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
        Fetch a web page with graceful error handling and semaphore limiting
        
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
            except httpx.TimeoutException:
                logger.warning("Request timeout", url=url)
                if allow_failure:
                    return None
                raise HTTPException(status_code=504, detail="Request timeout")
            except httpx.ConnectError:
                logger.warning("Connection error", url=url)
                if allow_failure:
                    return None
                raise HTTPException(status_code=503, detail="Connection error")
            except httpx.HTTPStatusError as e:
                logger.warning("HTTP error", url=url, status_code=e.response.status_code)
                if allow_failure:
                    return None
                raise HTTPException(status_code=e.response.status_code, detail=f"HTTP error: {e}")
            except Exception as e:
                logger.warning("Unexpected error fetching page", url=url, error=str(e))
                if allow_failure:
                    return None
                raise HTTPException(status_code=500, detail=f"Request failed: {str(e)}")
    
    async def scrape_from_source(self, source: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Scrape from a single source using the appropriate scraper based on type
        
        Args:
            source: Dictionary with source configuration
        
        Returns:
            List of scraped articles
        """
        source_type = source.get('type', 'rss')
        scraper = self.scrapers.get(source_type, self.scrapers['web'])
        
        try:
            articles = await scraper.scrape(source)
            return articles
        except Exception as e:
            logger.error(f"Error scraping from {source['name']}", error=str(e))
            return []
    
    async def scrape_multiple_sources(self) -> List[Dict[str, Any]]:
        """
        Scrape from multiple news sources with RSS priority and fallback tolerance
        
        Returns:
            Combined list of articles from all successful sources
        """
        all_articles = []
        successful_sources = []
        failed_sources = []
        rss_count = 0
        web_count = 0
        
        logger.info("Starting multi-source scraping", total_sources=len(Config.NEWS_SOURCES))
        
        tasks = []
        for source in Config.NEWS_SOURCES:
            tasks.append(self.scrape_from_source(source))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for source, result in zip(Config.NEWS_SOURCES, results):
            source_name = source['name']
            if isinstance(result, Exception):
                failed_sources.append(source_name)
                logger.error(f"✗ {source_name}: Unexpected error", error=str(result))
                continue
            
            articles = result
            if articles:
                all_articles.extend(articles)
                successful_sources.append(source_name)
                
                # Track method used
                if source.get('type') == 'rss' and source.get('rss_url'):
                    rss_count += 1
                else:
                    web_count += 1
            else:
                failed_sources.append(source_name)
        
        logger.info(
            "Multi-source scraping complete",
            total_articles=len(all_articles),
            successful_sources=len(successful_sources),
            failed_sources=len(failed_sources),
            rss_sources=rss_count,
            web_sources=web_count,
            sources_succeeded=successful_sources,
            sources_failed=failed_sources
        )
        
        # Deduplicate and score articles for veracity
        if all_articles:
            deduplicated_articles = self.deduplication_service.deduplicate_and_score(all_articles)
            logger.info(f"Post-deduplication: {len(deduplicated_articles)} unique articles")
            return deduplicated_articles
        else:
            logger.warning("All news sources failed to return articles")
            return []
    
    async def scrape_premium_times_latest_news(self) -> List[Dict[str, Any]]:
        """
        Legacy method - now uses multi-source scraping with RSS priority
        Kept for backward compatibility with existing endpoint
        """
        return await self.scrape_multiple_sources()
    
    async def close(self) -> None:
        """Close HTTP clients for all scrapers"""
        if self.client:
            await self.client.aclose()
            logger.info("Closed main HTTP client")
        for name, scraper in self.scrapers.items():
            await scraper.close()
            logger.info(f"Closed {name} scraper client")
