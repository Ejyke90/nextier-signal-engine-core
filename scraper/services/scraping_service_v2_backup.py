import json
import httpx
import asyncio
from datetime import datetime
from typing import List, Dict, Any, Optional
from bs4 import BeautifulSoup
from tenacity import retry, stop_after_attempt, wait_exponential, RetryError
from fastapi import HTTPException
from scraper.utils import get_logger, Config
from scraper.models import Article

logger = get_logger(__name__)


class ScrapingService:
    def __init__(self):
        self.client = None
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
            follow_redirects=True  # Enable redirect following
        )
    
    async def fetch_page(self, url: str, allow_failure: bool = True) -> Optional[str]:
        """
        Fetch a web page with graceful error handling
        
        Args:
            url: URL to fetch
            allow_failure: If True, return None on error instead of raising exception
        
        Returns:
            HTML content or None if failed and allow_failure=True
        """
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
        Scrape articles from a single news source
        
        Args:
            source: Dictionary with 'name', 'url', and 'selectors'
        
        Returns:
            List of scraped articles
        """
        articles = []
        source_name = source['name']
        source_url = source['url']
        
        try:
            logger.info(f"Attempting to scrape from {source_name}", url=source_url)
            
            html = await self.fetch_page(source_url, allow_failure=True)
            if not html:
                logger.warning(f"Failed to fetch page from {source_name}")
                return []
            
            soup = BeautifulSoup(html, 'lxml')
            
            # Try each selector until we find articles
            article_links = []
            for selector in source['selectors']:
                elements = soup.select(selector)
                if elements:
                    # Extract links from elements
                    for elem in elements[:Config.MAX_ARTICLES_PER_SOURCE]:
                        if elem.name == 'a':
                            article_links.append(elem)
                        else:
                            link = elem.find('a', href=True)
                            if link:
                                article_links.append(link)
                    
                    if article_links:
                        logger.info(f"Found {len(article_links)} articles using selector '{selector}'")
                        break
            
            if not article_links:
                logger.warning(f"No articles found from {source_name}")
                return []
            
            # Process article links
            processed_urls = set()
            
            for link in article_links[:Config.MAX_ARTICLES_PER_SOURCE]:
                href = link.get('href')
                if not href or href in processed_urls:
                    continue
                
                # Ensure we have a full URL
                if href.startswith('/'):
                    # Extract base URL from source_url
                    from urllib.parse import urlparse
                    parsed = urlparse(source_url)
                    base_url = f"{parsed.scheme}://{parsed.netloc}"
                    full_url = f"{base_url}{href}"
                elif not href.startswith('http'):
                    continue
                else:
                    full_url = href
                
                processed_urls.add(full_url)
                
                # Get article title from link text
                title = link.get_text(strip=True)
                
                if title and len(title) > 10:  # Basic validation
                    article_data = {
                        "title": title,
                        "content": f"Article from {source_name}",  # Placeholder - can be enhanced
                        "source": source_name,
                        "url": full_url,
                        "scraped_at": datetime.now().isoformat()
                    }
                    articles.append(article_data)
                    logger.info(f"Scraped article from {source_name}", title=title[:50])
            
            logger.info(f"Successfully scraped {len(articles)} articles from {source_name}")
            return articles
            
        except Exception as e:
            logger.error(f"Error scraping from {source_name}", error=str(e))
            return []
    
    async def scrape_multiple_sources(self) -> List[Dict[str, Any]]:
        """
        Scrape from multiple news sources with fallback tolerance
        
        Returns:
            Combined list of articles from all successful sources
        """
        all_articles = []
        successful_sources = []
        failed_sources = []
        
        logger.info("Starting multi-source scraping", total_sources=len(Config.NEWS_SOURCES))
        
        for source in Config.NEWS_SOURCES:
            try:
                articles = await self.scrape_from_source(source)
                if articles:
                    all_articles.extend(articles)
                    successful_sources.append(source['name'])
                    logger.info(f"✓ {source['name']}: {len(articles)} articles")
                else:
                    failed_sources.append(source['name'])
                    logger.warning(f"✗ {source['name']}: No articles scraped")
            except Exception as e:
                failed_sources.append(source['name'])
                logger.error(f"✗ {source['name']}: Exception occurred", error=str(e))
                continue  # Continue to next source
        
        logger.info(
            "Multi-source scraping complete",
            total_articles=len(all_articles),
            successful_sources=len(successful_sources),
            failed_sources=len(failed_sources),
            sources_succeeded=successful_sources,
            sources_failed=failed_sources
        )
        
        # If we got at least some articles, consider it a success
        if all_articles:
            return all_articles
        else:
            # All sources failed - return empty list but don't raise exception
            logger.warning("All news sources failed to return articles")
            return []
    
    async def scrape_premium_times_latest_news(self) -> List[Dict[str, Any]]:
        """
        Legacy method - now uses multi-source scraping
        Kept for backward compatibility with existing endpoint
        """
        return await self.scrape_multiple_sources()
    
    async def scrape_article(self, url: str) -> Optional[Dict[str, Any]]:
        """Scrape a single article for title and content"""
        try:
            html = await self.fetch_page(url, allow_failure=True)
            if not html:
                return None
            
            soup = BeautifulSoup(html, 'lxml')
            
            # Extract title
            title_selectors = ['h1', '.entry-title', '.post-title', '.article-title', 'title']
            title = ""
            for selector in title_selectors:
                title_elem = soup.select_one(selector)
                if title_elem:
                    title = title_elem.get_text(strip=True)
                    break
            
            # Extract content
            content_selectors = [
                '.entry-content',
                '.post-content',
                '.article-content',
                '.content',
                'article p',
                '.jeg_post_content'
            ]
            
            content = ""
            for selector in content_selectors:
                content_elem = soup.select_one(selector)
                if content_elem:
                    paragraphs = content_elem.find_all('p')
                    if paragraphs:
                        content = ' '.join([p.get_text(strip=True) for p in paragraphs])
                    else:
                        content = content_elem.get_text(strip=True)
                    break
            
            # Fallback: get all paragraphs if no specific content found
            if not content:
                paragraphs = soup.find_all('p')
                content = ' '.join([p.get_text(strip=True) for p in paragraphs])
            
            if title and content:
                return {
                    "title": title,
                    "content": content,
                    "source": "article",
                    "url": url,
                    "scraped_at": datetime.now().isoformat()
                }
            
            return None
            
        except Exception as e:
            logger.error("Error scraping article", url=url, error=str(e))
            return None
    
    async def close(self) -> None:
        """Close HTTP client"""
        if self.client:
            await self.client.aclose()
            logger.info("Closed HTTP client")
