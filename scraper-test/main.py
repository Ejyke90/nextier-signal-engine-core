import json
import os
import logging
from datetime import datetime
from typing import List, Dict, Any
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
from bs4 import BeautifulSoup
from requests.exceptions import RequestException, Timeout, ConnectionError

app = FastAPI(title="Scraper Service", version="1.0.0")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
PREMIUM_TIMES_URL = "https://premiumtimesng.com/"
DATA_DIR = "/data"
RAW_NEWS_FILE = os.path.join(DATA_DIR, "raw_news.json")


class NewsArticle(BaseModel):
    title: str
    content: str
    source: str
    scraped_at: str


class HealthResponse(BaseModel):
    status: str
    service: str


class ScrapeResponse(BaseModel):
    status: str
    articles_scraped: int
    message: str


def ensure_data_directory():
    """Ensure the data directory exists"""
    os.makedirs(DATA_DIR, exist_ok=True)


def scrape_premium_times_latest_news() -> List[Dict[str, Any]]:
    """
    Scrape the 'Latest News' section of premiumtimesng.com
    Extract title and full text of articles
    """
    articles = []
    
    try:
        logger.info(f"Fetching {PREMIUM_TIMES_URL}")
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(PREMIUM_TIMES_URL, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'lxml')
        
        # Look for latest news section - try multiple selectors
        latest_news_selectors = [
            '.jeg_block_heading',  # Common for JNews theme
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
            # Fallback: find all article links
            article_links = soup.find_all('a', href=True)
            logger.warning("Could not find specific latest news section, using fallback method")
        else:
            # Find article links within the section
            article_links = latest_news_section.find_all('a', href=True)
        
        # Process article links
        processed_urls = set()
        for link in article_links[:10]:  # Limit to first 10 articles
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
                logger.info(f"Scraping article: {full_url}")
                article_data = scrape_article(full_url)
                if article_data:
                    articles.append(article_data)
                    logger.info(f"Successfully scraped: {article_data['title'][:50]}...")
                    
            except Exception as e:
                logger.error(f"Error scraping article {full_url}: {str(e)}")
                continue
        
        logger.info(f"Successfully scraped {len(articles)} articles")
        return articles
        
    except Timeout:
        logger.error("Timeout occurred while fetching Premium Times")
        raise HTTPException(status_code=504, detail="Request timeout")
    except ConnectionError:
        logger.error("Connection error while fetching Premium Times")
        raise HTTPException(status_code=503, detail="Connection error")
    except RequestException as e:
        logger.error(f"Request error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Request failed: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error during scraping: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Scraping failed: {str(e)}")


def scrape_article(url: str) -> Dict[str, Any]:
    """Scrape a single article for title and content"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'lxml')
        
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
                # Get all paragraphs within the content element
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
        logger.error(f"Error scraping article {url}: {str(e)}")
        return None


def save_articles_to_json(articles: List[Dict[str, Any]]) -> bool:
    """Save articles to JSON file"""
    try:
        ensure_data_directory()
        
        # Load existing articles if file exists
        existing_articles = []
        if os.path.exists(RAW_NEWS_FILE):
            try:
                with open(RAW_NEWS_FILE, 'r', encoding='utf-8') as f:
                    existing_articles = json.load(f)
            except json.JSONDecodeError:
                logger.warning("Existing JSON file is corrupted, starting fresh")
                existing_articles = []
        
        # Combine existing and new articles, avoiding duplicates by URL
        all_articles = existing_articles.copy()
        existing_urls = {article.get('url', '') for article in existing_articles}
        
        for article in articles:
            if article.get('url', '') not in existing_urls:
                all_articles.append(article)
        
        # Save to file
        with open(RAW_NEWS_FILE, 'w', encoding='utf-8') as f:
            json.dump(all_articles, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Saved {len(all_articles)} articles to {RAW_NEWS_FILE}")
        return True
        
    except Exception as e:
        logger.error(f"Error saving articles: {str(e)}")
        return False


@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Welcome to Scraper Service"}


@app.get("/health", response_model=HealthResponse)
async def health():
    """Health check endpoint"""
    return HealthResponse(status="healthy", service="scraper")


@app.get("/scrape", response_model=ScrapeResponse)
async def scrape_news():
    """Scrape latest news from Premium Times"""
    try:
        articles = scrape_premium_times_latest_news()
        
        if not articles:
            return ScrapeResponse(
                status="warning",
                articles_scraped=0,
                message="No articles were scraped"
            )
        
        success = save_articles_to_json(articles)
        
        if success:
            return ScrapeResponse(
                status="success",
                articles_scraped=len(articles),
                message=f"Successfully scraped and saved {len(articles)} articles"
            )
        else:
            return ScrapeResponse(
                status="error",
                articles_scraped=len(articles),
                message="Articles scraped but failed to save"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in scrape_news: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.get("/articles")
async def get_articles():
    """Get all scraped articles"""
    try:
        if not os.path.exists(RAW_NEWS_FILE):
            return {"articles": [], "count": 0}
        
        with open(RAW_NEWS_FILE, 'r', encoding='utf-8') as f:
            articles = json.load(f)
        
        return {"articles": articles, "count": len(articles)}
        
    except Exception as e:
        logger.error(f"Error reading articles: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to read articles")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
