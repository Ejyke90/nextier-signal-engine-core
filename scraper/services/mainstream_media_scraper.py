from typing import List, Dict, Any, Optional
import asyncio
from bs4 import BeautifulSoup
from scraper.services.base_scraper import BaseScraper
from scraper.utils import get_logger, Config
from datetime import datetime

logger = get_logger(__name__)

class MainstreamMediaScraper(BaseScraper):
    """Specialized scraper for national dailies like Punch, Vanguard, TheCable using custom CSS selectors."""
    
    async def scrape(self, source: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Scrape articles from a mainstream media source using web scraping with custom CSS selectors.
        
        Args:
            source: Dictionary with 'name', 'web_url', and 'selectors'
        
        Returns:
            List of scraped articles
        """
        articles = []
        source_name = source['name']
        source_url = source.get('web_url')
        
        if not source_url:
            logger.warning(f"{source_name}: No web URL configured")
            return []
        
        try:
            logger.info(f"Attempting web scrape from {source_name}", url=source_url)
            
            html = await self.fetch_page(source_url, allow_failure=True)
            if not html:
                logger.warning(f"Failed to fetch page from {source_name}")
                return []
            
            soup = BeautifulSoup(html, 'lxml')
            
            # Try each selector until we find articles
            article_links = []
            for selector in source.get('selectors', []):
                elements = soup.select(selector)
                if elements:
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
                
                if title and len(title) > 10:
                    # Fetch full content if possible
                    content_html = await self.fetch_page(full_url, allow_failure=True)
                    content = f"Article from {source_name}"
                    features = {}
                    if content_html:
                        content_soup = BeautifulSoup(content_html, 'lxml')
                        content_text = content_soup.get_text(strip=True)
                        content = content_text if content_text else content
                        features = self.extract_features(content, source_name)
                    
                    article_data = {
                        "title": title,
                        "content": content,
                        "source": source_name,
                        "url": full_url,
                        "scraped_at": datetime.now().isoformat(),
                        "features": features
                    }
                    articles.append(article_data)
                    logger.info(f"Scraped article from {source_name}", title=title[:50])
            
            logger.info(f"✓ {source_name} (Web): {len(articles)} articles")
            return articles
            
        except Exception as e:
            logger.error(f"✗ {source_name} (Web): Exception occurred", error=str(e))
            return []
    
    def extract_features(self, content: str, source_name: str) -> Dict[str, Any]:
        """
        Extract structured features from raw content relevant to NNVCD.
        
        Args:
            content: Raw text or HTML content of the article
            source_name: Name of the source for context
        
        Returns:
            Dictionary with extracted features (conflict type, casualties, geography)
        """
        # Placeholder for feature extraction logic
        # This can be enhanced with NLP or keyword matching for NNVCD metrics
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
