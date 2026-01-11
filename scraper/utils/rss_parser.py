"""
RSS Feed Parser Utility
Provides robust RSS feed parsing for Nigerian news sources
"""
import feedparser
from typing import List, Dict, Any, Optional
from datetime import datetime
from scraper.utils import get_logger

logger = get_logger(__name__)


class RSSParser:
    """Parse RSS feeds and extract article data"""
    
    @staticmethod
    def parse_feed(feed_url: str, max_articles: int = 10) -> List[Dict[str, Any]]:
        """
        Parse an RSS feed and extract articles
        
        Args:
            feed_url: URL of the RSS feed
            max_articles: Maximum number of articles to extract
            
        Returns:
            List of article dictionaries
        """
        try:
            logger.info(f"Parsing RSS feed", url=feed_url)
            
            # Parse the feed
            feed = feedparser.parse(feed_url)
            
            # Check if feed was successfully parsed
            if feed.bozo:
                logger.warning(f"RSS feed has parsing issues", url=feed_url, error=str(feed.bozo_exception))
            
            if not feed.entries:
                logger.warning(f"No entries found in RSS feed", url=feed_url)
                return []
            
            articles = []
            for entry in feed.entries[:max_articles]:
                article = RSSParser._extract_article_from_entry(entry, feed_url)
                if article:
                    articles.append(article)
            
            logger.info(f"Successfully parsed RSS feed", url=feed_url, articles_count=len(articles))
            return articles
            
        except Exception as e:
            logger.error(f"Error parsing RSS feed", url=feed_url, error=str(e))
            return []
    
    @staticmethod
    def _extract_article_from_entry(entry: Any, feed_url: str) -> Optional[Dict[str, Any]]:
        """
        Extract article data from RSS feed entry
        
        Args:
            entry: feedparser entry object
            feed_url: Source feed URL for attribution
            
        Returns:
            Article dictionary or None if extraction fails
        """
        try:
            # Extract title
            title = entry.get('title', '').strip()
            if not title:
                return None
            
            # Extract link/URL
            url = entry.get('link', '').strip()
            if not url:
                return None
            
            # Extract content/summary
            content = ''
            if hasattr(entry, 'content') and entry.content:
                # Some feeds provide full content
                content = entry.content[0].get('value', '')
            elif hasattr(entry, 'summary'):
                # Most feeds provide summary
                content = entry.get('summary', '')
            elif hasattr(entry, 'description'):
                # Fallback to description
                content = entry.get('description', '')
            
            # Clean HTML tags from content if present
            if content:
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(content, 'html.parser')
                content = soup.get_text(strip=True)
            
            # Extract published date
            published_at = None
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                try:
                    published_at = datetime(*entry.published_parsed[:6]).isoformat()
                except:
                    pass
            
            if not published_at:
                published_at = datetime.now().isoformat()
            
            # Extract source from feed
            source = 'Unknown'
            if hasattr(entry, 'source') and hasattr(entry.source, 'title'):
                source = entry.source.title
            else:
                # Try to extract from feed_url
                from urllib.parse import urlparse
                parsed = urlparse(feed_url)
                source = parsed.netloc.replace('www.', '').replace('.com', '').replace('.ng', '').title()
            
            # Build article dictionary
            article = {
                'title': title,
                'content': content if content else f"Article from {source}",
                'url': url,
                'source': source,
                'scraped_at': datetime.now().isoformat(),
                'published_at': published_at
            }
            
            # Add optional fields if available
            if hasattr(entry, 'author'):
                article['author'] = entry.author
            
            if hasattr(entry, 'tags'):
                article['tags'] = [tag.term for tag in entry.tags]
            
            return article
            
        except Exception as e:
            logger.error(f"Error extracting article from RSS entry", error=str(e))
            return None
    
    @staticmethod
    def test_feed(feed_url: str) -> Dict[str, Any]:
        """
        Test an RSS feed and return diagnostic information
        
        Args:
            feed_url: URL of the RSS feed to test
            
        Returns:
            Dictionary with test results
        """
        try:
            feed = feedparser.parse(feed_url)
            
            result = {
                'url': feed_url,
                'success': not feed.bozo,
                'entries_count': len(feed.entries),
                'feed_title': feed.feed.get('title', 'Unknown'),
                'feed_description': feed.feed.get('description', 'N/A'),
                'error': str(feed.bozo_exception) if feed.bozo else None
            }
            
            if feed.entries:
                sample_entry = feed.entries[0]
                result['sample_title'] = sample_entry.get('title', 'N/A')
                result['sample_link'] = sample_entry.get('link', 'N/A')
            
            return result
            
        except Exception as e:
            return {
                'url': feed_url,
                'success': False,
                'error': str(e)
            }
