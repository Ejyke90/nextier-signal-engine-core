import pytest
import json
from unittest.mock import AsyncMock, MagicMock, patch
from intelligence_api.services.llm_service import LLMService
from intelligence_api.models import ParsedEvent


class TestLLMService:
    """Test cases for LLMService"""
    
    @pytest.fixture
    def llm_service(self):
        """Create LLMService instance for testing"""
        with patch('intelligence_api.services.llm_service.httpx.AsyncClient'):
            service = LLMService()
            return service
    
    @pytest.mark.asyncio
    async def test_call_ollama_llm_success(self, llm_service):
        """Test successful LLM call"""
        # Mock HTTP response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "response": '{"Event_Type": "clash", "State": "Lagos", "LGA": "Ikeja", "Severity": "high"}'
        }
        mock_response.raise_for_status = MagicMock()
        
        llm_service.client.post = AsyncMock(return_value=mock_response)
        
        result = await llm_service.call_ollama_llm("Test article content")
        
        assert result is not None
        assert result["event_type"] == "clash"
        assert result["state"] == "Lagos"
        assert result["lga"] == "Ikeja"
        assert result["severity"] == "high"
    
    @pytest.mark.asyncio
    async def test_call_ollama_llm_json_with_code_blocks(self, llm_service):
        """Test LLM call with JSON in code blocks"""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "response": '```json\n{"Event_Type": "conflict", "State": "Abuja", "LGA": "Maitama", "Severity": "medium"}\n```'
        }
        mock_response.raise_for_status = MagicMock()
        
        llm_service.client.post = AsyncMock(return_value=mock_response)
        
        result = await llm_service.call_ollama_llm("Test article content")
        
        assert result is not None
        assert result["event_type"] == "conflict"
        assert result["state"] == "Abuja"
        assert result["lga"] == "Maitama"
        assert result["severity"] == "medium"
    
    @pytest.mark.asyncio
    async def test_call_ollama_llm_missing_fields(self, llm_service):
        """Test LLM call with missing required fields"""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "response": '{"Event_Type": "clash", "State": "Lagos"}'  # Missing LGA and Severity
        }
        mock_response.raise_for_status = MagicMock()
        
        llm_service.client.post = AsyncMock(return_value=mock_response)
        
        result = await llm_service.call_ollama_llm("Test article content")
        
        assert result is None
    
    @pytest.mark.asyncio
    async def test_call_ollama_llm_invalid_json(self, llm_service):
        """Test LLM call with invalid JSON response"""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "response": "This is not valid JSON"
        }
        mock_response.raise_for_status = MagicMock()
        
        llm_service.client.post = AsyncMock(return_value=mock_response)
        
        result = await llm_service.call_ollama_llm("Test article content")
        
        assert result is None
    
    @pytest.mark.asyncio
    async def test_call_ollama_llm_timeout(self, llm_service):
        """Test LLM call timeout"""
        from httpx import TimeoutException
        
        llm_service.client.post = AsyncMock(side_effect=TimeoutException("Timeout"))
        
        result = await llm_service.call_ollama_llm("Test article content")
        
        assert result is None
    
    @pytest.mark.asyncio
    async def test_parse_article_with_llm_success(self, llm_service):
        """Test successful article parsing"""
        article = {
            "title": "Test Article",
            "content": "There was a clash in Lagos, Ikeja with high severity",
            "url": "https://example.com/article"
        }
        
        mock_parsed_data = {
            "event_type": "clash",
            "state": "Lagos",
            "lga": "Ikeja",
            "severity": "high"
        }
        
        with patch.object(llm_service, 'call_ollama_llm', return_value=mock_parsed_data):
            result = await llm_service.parse_article_with_llm(article)
            
            assert result is not None
            assert isinstance(result, ParsedEvent)
            assert result.event_type == "clash"
            assert result.state == "Lagos"
            assert result.lga == "Ikeja"
            assert result.severity == "high"
            assert result.source_title == "Test Article"
            assert result.source_url == "https://example.com/article"
    
    @pytest.mark.asyncio
    async def test_parse_article_with_llm_failure(self, llm_service):
        """Test article parsing failure"""
        article = {
            "title": "Test Article",
            "content": "Some content",
            "url": "https://example.com/article"
        }
        
        with patch.object(llm_service, 'call_ollama_llm', return_value=None):
            result = await llm_service.parse_article_with_llm(article)
            
            assert result is None
    
    @pytest.mark.asyncio
    async def test_process_articles_batch(self, llm_service):
        """Test processing multiple articles in batch"""
        articles = [
            {"title": "Article 1", "content": "Content 1", "url": "https://example.com/1"},
            {"title": "Article 2", "content": "Content 2", "url": "https://example.com/2"},
            {"title": "Article 3", "content": "Content 3", "url": "https://example.com/3"}
        ]
        
        # Mock successful parsing for first two articles, failure for third
        async def mock_parse_article(article):
            if article["url"] == "https://example.com/3":
                return None
            return ParsedEvent(
                event_type="clash",
                state="Lagos",
                lga="Ikeja",
                severity="high",
                source_title=article["title"],
                source_url=article["url"]
            )
        
        with patch.object(llm_service, 'parse_article_with_llm', side_effect=mock_parse_article):
            result = await llm_service.process_articles_batch(articles)
            
            assert len(result) == 2
            assert all("event_type" in event for event in result)
    
    @pytest.mark.asyncio
    async def test_close_client(self, llm_service):
        """Test closing HTTP client"""
        llm_service.client.aclose = AsyncMock()
        
        await llm_service.close()
        
        llm_service.client.aclose.assert_called_once()


class TestParsedEventModel:
    """Test cases for ParsedEvent model"""
    
    def test_parsed_event_model_valid(self):
        """Test valid ParsedEvent model creation"""
        event = ParsedEvent(
            event_type="clash",
            state="Lagos",
            lga="Ikeja",
            severity="high",
            source_title="Test Article",
            source_url="https://test.com/article"
        )
        
        assert event.event_type == "clash"
        assert event.state == "Lagos"
        assert event.lga == "Ikeja"
        assert event.severity == "high"
        assert event.source_title == "Test Article"
        assert event.source_url == "https://test.com/article"
        assert event.parsed_at is not None
    
    def test_parsed_event_model_invalid_severity(self):
        """Test ParsedEvent model with invalid severity"""
        with pytest.raises(ValueError):
            ParsedEvent(
                event_type="clash",
                state="Lagos",
                lga="Ikeja",
                severity="invalid",  # Invalid severity
                source_title="Test Article",
                source_url="https://test.com/article"
            )
    
    def test_parsed_event_model_empty_fields(self):
        """Test ParsedEvent model with empty required fields"""
        with pytest.raises(ValueError):
            ParsedEvent(
                event_type="",  # Empty event type
                state="Lagos",
                lga="Ikeja",
                severity="high",
                source_title="Test Article",
                source_url="https://test.com/article"
            )
