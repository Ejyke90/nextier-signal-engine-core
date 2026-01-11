import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime
from scraper.services.scraping_service import ScrapingService
from scraper.models import Article


class TestScrapingService:
    """Test cases for ScrapingService"""
    
    @pytest.fixture
    def scraping_service(self):
        """Create a ScrapingService instance for testing"""
        with patch('scraper.services.scraping_service.httpx.AsyncClient'):
            service = ScrapingService()
            return service
    
    @pytest.mark.asyncio
    async def test_fetch_page_success(self, scraping_service):
        """Test successful page fetch"""
        # Mock HTTP response
        mock_response = MagicMock()
        mock_response.text = "<html><body>Test content</body></html>"
        mock_response.raise_for_status = MagicMock()
        
        scraping_service.client.get = AsyncMock(return_value=mock_response)
        
        result = await scraping_service.fetch_page("https://example.com")
        
        assert result == "<html><body>Test content</body></html>"
        scraping_service.client.get.assert_called_once_with("https://example.com")
    
    @pytest.mark.asyncio
    async def test_fetch_page_timeout(self, scraping_service):
        """Test page fetch timeout"""
        from httpx import TimeoutException
        
        scraping_service.client.get = AsyncMock(side_effect=TimeoutException("Timeout"))
        
        with pytest.raises(Exception):  # Should raise HTTPException
            await scraping_service.fetch_page("https://example.com")
    
    @pytest.mark.asyncio
    async def test_scrape_article_success(self, scraping_service):
        """Test successful article scraping"""
        html_content = """
        <html>
            <head><title>Test Article</title></head>
            <body>
                <h1>Test Article Title</h1>
                <div class="entry-content">
                    <p>This is the first paragraph.</p>
                    <p>This is the second paragraph.</p>
                </div>
            </body>
        </html>
        """
        
        with patch.object(scraping_service, 'fetch_page', return_value=html_content):
            result = await scraping_service.scrape_article("https://example.com/article")
            
            assert result is not None
            assert result["title"] == "Test Article Title"
            assert "This is the first paragraph" in result["content"]
            assert "This is the second paragraph" in result["content"]
            assert result["source"] == "premiumtimesng.com"
            assert result["url"] == "https://example.com/article"
            assert "scraped_at" in result
    
    @pytest.mark.asyncio
    async def test_scrape_article_not_found(self, scraping_service):
        """Test article scraping when content not found"""
        html_content = "<html><body>No content here</body></html>"
        
        with patch.object(scraping_service, 'fetch_page', return_value=html_content):
            result = await scraping_service.scrape_article("https://example.com/article")
            
            assert result is None
    
    @pytest.mark.asyncio
    async def test_scrape_premium_times_latest_news(self, scraping_service):
        """Test scraping latest news from Premium Times"""
        # Mock main page
        main_html = """
        <html>
            <body>
                <div class="jeg_block_heading">
                    <a href="/article1">Article 1</a>
                    <a href="/article2">Article 2</a>
                </div>
            </body>
        </html>
        """
        
        # Mock article pages
        article_html = """
        <html>
            <body>
                <h1>Article Title</h1>
                <div class="entry-content">
                    <p>Article content here</p>
                </div>
            </body>
        </html>
        """
        
        with patch.object(scraping_service, 'fetch_page') as mock_fetch:
            mock_fetch.side_effect = [main_html, article_html, article_html]
            
            result = await scraping_service.scrape_premium_times_latest_news()
            
            assert len(result) == 2
            assert all("title" in article for article in result)
            assert all("content" in article for article in result)
    
    @pytest.mark.asyncio
    async def test_scrape_premium_times_no_articles(self, scraping_service):
        """Test scraping when no articles found"""
        html_content = "<html><body>No articles</body></html>"
        
        with patch.object(scraping_service, 'fetch_page', return_value=html_content):
            result = await scraping_service.scrape_premium_times_latest_news()
            
            assert result == []
    
    @pytest.mark.asyncio
    async def test_close_client(self, scraping_service):
        """Test closing HTTP client"""
        scraping_service.client.aclose = AsyncMock()
        
        await scraping_service.close()
        
        scraping_service.client.aclose.assert_called_once()


class TestArticleModel:
    """Test cases for Article model"""
    
    def test_article_model_valid(self):
        """Test valid Article model creation"""
        article = Article(
            title="Test Article",
            content="This is test content",
            source="test.com",
            url="https://test.com/article"
        )
        
        assert article.title == "Test Article"
        assert article.content == "This is test content"
        assert article.source == "test.com"
        assert str(article.url) == "https://test.com/article"
        assert article.scraped_at is not None
    
    def test_article_model_invalid_title(self):
        """Test Article model with invalid title"""
        with pytest.raises(ValueError):
            Article(
                title="",  # Too short
                content="This is test content",
                source="test.com",
                url="https://test.com/article"
            )
    
    def test_article_model_invalid_content(self):
        """Test Article model with invalid content"""
        with pytest.raises(ValueError):
            Article(
                title="Test Article",
                content="Too short",  # Too short
                source="test.com",
                url="https://test.com/article"
            )
