import json
import httpx
import asyncio
from datetime import datetime
from typing import List, Dict, Any, Optional
from bs4 import BeautifulSoup
from circuitbreaker import circuit
from tenacity import retry, stop_after_attempt, wait_exponential
from fastapi import HTTPException
from scraper.utils import get_logger, Config
from scraper.models import Article

logger = get_logger(__name__)


class ScrapingService:
    def __init__(self):
        self.client = None
        self._create_client()
    
    def _create_client(self) -> None:
        """Create HTTP client with connection pooling"""
        self.client = httpx.AsyncClient(
            timeout=Config.REQUEST_TIMEOUT,
            limits=httpx.Limits(
                max_connections=Config.MAX_CONNECTIONS,
                max_keepalive_connections=Config.MAX_KEEPALIVE_CONNECTIONS
            ),
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
        )
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    @circuit(failure_threshold=5, recovery_timeout=30)
    async def fetch_page(self, url: str) -> str:
        """Fetch a web page with retry and circuit breaker"""
        try:
            response = await self.client.get(url)
            response.raise_for_status()
            return response.text
        except httpx.TimeoutException:
            logger.error("Request timeout", url=url)
            raise HTTPException(status_code=504, detail="Request timeout")
        except httpx.ConnectError:
            logger.error("Connection error", url=url)
            raise HTTPException(status_code=503, detail="Connection error")
        except httpx.HTTPStatusError as e:
            logger.error("HTTP error", url=url, status_code=e.response.status_code)
            raise HTTPException(status_code=e.response.status_code, detail=f"HTTP error: {e}")
        except Exception as e:
            logger.error("Unexpected error fetching page", url=url, error=str(e))
            raise HTTPException(status_code=500, detail=f"Request failed: {str(e)}")
    
    async def scrape_premium_times_latest_news(self) -> List[Dict[str, Any]]:
        """Scrape the 'Latest News' section of premiumtimesng.com"""
        try:
            logger.info("Starting scrape", source=Config.PREMIUM_TIMES_URL)
            
            html = await self.fetch_page(Config.PREMIUM_TIMES_URL)
            soup = BeautifulSoup(html, 'lxml')
            
            # Look for latest news section
            latest_news_selectors = [
                '.jeg_block_heading',
                '.latest-news',
                '#latest-news',
                '.news-list',
                '.jeg_posts',
                'article',
                '.post'
            ]
            
            latest_news_section = None
            for selector in latest_news_selectors:
                section = soup.select_one(selector)
                if section:
                    latest_news_section = section
                    break
            
            if not latest_news_section:
                article_links = soup.find_all('a', href=True)
                logger.warning("Could not find specific latest news section, using fallback method")
            else:
                article_links = latest_news_section.find_all('a', href=True)
            
            # Process article links
            processed_urls = set()
            articles = []
            
            for link in article_links[:Config.MAX_ARTICLES_PER_SCRAPE]:
                href = link.get('href')
                if not href or href in processed_urls:
                    continue
                
                # Ensure we have a full URL
                if href.startswith('/'):
                    full_url = f"https://premiumtimesng.com{href}"
                elif not href.startswith('http'):
                    continue
                else:
                    full_url = href
                
                processed_urls.add(full_url)
                
                try:
                    article_data = await self.scrape_article(full_url)
                    if article_data:
                        articles.append(article_data)
                        logger.info("Successfully scraped article", 
                                  title=article_data['title'][:50], 
                                  url=full_url)
                        
                except Exception as e:
                    logger.error("Error scraping article", url=full_url, error=str(e))
                    continue
            
            logger.info("Completed scrape", articles_count=len(articles))
            return articles
            
        except Exception as e:
            logger.error("Error during scraping", error=str(e))
            raise
    
    async def scrape_article(self, url: str) -> Optional[Dict[str, Any]]:
        """Scrape a single article for title and content"""
        try:
            html = await self.fetch_page(url)
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
                    "source": "premiumtimesng.com",
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
