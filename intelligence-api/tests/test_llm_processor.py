import pytest
import json
from unittest.mock import AsyncMock, MagicMock
from httpx import AsyncClient
from intelligence_api.services.llm_processor import LLMProcessor, CATEGORIZATION_SYSTEM_PROMPT


@pytest.mark.asyncio
class TestLLMProcessor:
    @pytest.fixture
    def mock_client(self):
        client = AsyncMock(spec=AsyncClient)
        return client

    @pytest.fixture
    def processor(self, mock_client):
        processor = LLMProcessor()
        processor.client = mock_client
        return processor

    async def test_analyze_with_ollama_success_banditry(self, processor, mock_client):
        """Test successful categorization as Banditry"""
        mock_response = MagicMock()
        mock_response.json.return_value = {"response": '{"category": "Banditry"}'}
        mock_response.raise_for_status = MagicMock()
        mock_client.post.return_value = mock_response

        result = await processor.analyze_with_ollama("Armed men robbed a bank")

        assert result == "Banditry"
        mock_client.post.assert_called_once()
        args = mock_client.post.call_args
        assert args[0][0] == "http://localhost:11434/api/generate"
        payload = args[1]["json"]
        assert payload["model"] == "llama3.2"
        assert payload["format"] == "json"
        assert "Armed men robbed a bank" in payload["prompt"]
        assert CATEGORIZATION_SYSTEM_PROMPT in payload["prompt"]

    async def test_analyze_with_ollama_success_farmer_herder_clashes(self, processor, mock_client):
        """Test successful categorization as Farmer-Herder Clashes"""
        mock_response = MagicMock()
        mock_response.json.return_value = {"response": '{"category": "Farmer-Herder Clashes"}'}
        mock_response.raise_for_status = MagicMock()
        mock_client.post.return_value = mock_response

        result = await processor.analyze_with_ollama("Herder attacked farmer over grazing")

        assert result == "Farmer-Herder Clashes"

    async def test_analyze_with_ollama_invalid_category(self, processor, mock_client):
        """Test invalid category defaults to Unknown"""
        mock_response = MagicMock()
        mock_response.json.return_value = {"response": '{"category": "InvalidCategory"}'}
        mock_response.raise_for_status = MagicMock()
        mock_client.post.return_value = mock_response

        result = await processor.analyze_with_ollama("Some text")

        assert result == "Unknown"

    async def test_analyze_with_ollama_unknown_category(self, processor, mock_client):
        """Test explicit Unknown category"""
        mock_response = MagicMock()
        mock_response.json.return_value = {"response": '{"category": "Unknown"}'}
        mock_response.raise_for_status = MagicMock()
        mock_client.post.return_value = mock_response

        result = await processor.analyze_with_ollama("Unrelated news")

        assert result == "Unknown"

    async def test_analyze_with_ollama_json_parse_error(self, processor, mock_client):
        """Test JSON parse error returns Unknown"""
        mock_response = MagicMock()
        mock_response.json.return_value = {"response": "Invalid JSON response"}
        mock_response.raise_for_status = MagicMock()
        mock_client.post.return_value = mock_response

        result = await processor.analyze_with_ollama("Some text")

        assert result == "Unknown"

    async def test_analyze_with_ollama_http_error(self, processor, mock_client):
        """Test HTTP error returns Unknown"""
        from httpx import HTTPStatusError
        mock_client.post.side_effect = HTTPStatusError("Error", request=MagicMock(), response=MagicMock())

        result = await processor.analyze_with_ollama("Some text")

        assert result == "Unknown"

    async def test_analyze_with_ollama_connection_error(self, processor, mock_client):
        """Test connection error returns Unknown"""
        from httpx import ConnectError
        mock_client.post.side_effect = ConnectError("Connection failed")

        result = await processor.analyze_with_ollama("Some text")

        assert result == "Unknown"

    async def test_analyze_with_ollama_timeout_error(self, processor, mock_client):
        """Test timeout error returns Unknown"""
        from httpx import TimeoutException
        mock_client.post.side_effect = TimeoutException("Timeout")

        result = await processor.analyze_with_ollama("Some text")

        assert result == "Unknown"

    async def test_categorize_articles_batch_success(self, processor, mock_client):
        """Test batch categorization success"""
        # Mock successful responses for two articles
        mock_responses = [
            MagicMock(),
            MagicMock()
        ]
        mock_responses[0].json.return_value = {"response": '{"category": "Banditry"}'}
        mock_responses[0].raise_for_status = MagicMock()
        mock_responses[1].json.return_value = {"response": '{"category": "Kidnapping"}'}
        mock_responses[1].raise_for_status = MagicMock()
        mock_client.post.side_effect = mock_responses

        articles = [
            {"_id": "1", "title": "Robbery", "content": "Armed robbery"},
            {"_id": "2", "title": "Abduction", "content": "Kidnapped"}
        ]

        results = await processor.categorize_articles_batch(articles)

        assert len(results) == 2
        assert results[0] == {"id": "1", "category": "Banditry"}
        assert results[1] == {"id": "2", "category": "Kidnapping"}

    async def test_categorize_articles_batch_partial_failure(self, processor, mock_client):
        """Test batch categorization with some failures"""
        # Mock one success, one failure
        mock_success = MagicMock()
        mock_success.json.return_value = {"response": '{"category": "Banditry"}'}
        mock_success.raise_for_status = MagicMock()
        mock_client.post.side_effect = [mock_success, Exception("API Error")]

        articles = [
            {"_id": "1", "title": "Robbery", "content": "Armed robbery"},
            {"_id": "2", "title": "Abduction", "content": "Kidnapped"}
        ]

        results = await processor.categorize_articles_batch(articles)

        # Should return only successful result
        assert len(results) == 1
        assert results[0] == {"id": "1", "category": "Banditry"}

    def test_rule_based_categorize_banditry(self, processor):
        """Test rule-based categorization for Banditry keywords"""
        result = processor.rule_based_categorize("Armed bandits robbed a bank")
        assert result == {"category": "Banditry", "confidence": 70}

        result = processor.rule_based_categorize("Highway robbery incident")
        assert result == {"category": "Banditry", "confidence": 70}

    def test_rule_based_categorize_kidnapping(self, processor):
        """Test rule-based categorization for Kidnapping keywords"""
        result = processor.rule_based_categorize("Kidnappers abducted school children")
        assert result == {"category": "Kidnapping", "confidence": 75}

        result = processor.rule_based_categorize("Hostage situation with ransom demand")
        assert result == {"category": "Kidnapping", "confidence": 75}

    def test_rule_based_categorize_gunmen_violence(self, processor):
        """Test rule-based categorization for Gunmen Violence keywords"""
        result = processor.rule_based_categorize("Gunmen attacked the village")
        assert result == {"category": "Gunmen Violence", "confidence": 65}

        result = processor.rule_based_categorize("Drive-by shooting on highway")
        assert result == {"category": "Gunmen Violence", "confidence": 65}

    def test_rule_based_categorize_farmer_herder(self, processor):
        """Test rule-based categorization for Farmer-Herder Clashes keywords"""
        result = processor.rule_based_categorize("Herder-farmer conflict over grazing land")
        assert result == {"category": "Farmer-Herder Clashes", "confidence": 60}

        result = processor.rule_based_categorize("Cattle rustling dispute")
        assert result == {"category": "Farmer-Herder Clashes", "confidence": 60}

    def test_rule_based_categorize_unknown(self, processor):
        """Test rule-based categorization for unknown content"""
        result = processor.rule_based_categorize("Some unrelated news about politics")
        assert result == {"category": "Unknown", "confidence": 20}

    def test_rule_based_categorize_case_insensitive(self, processor):
        """Test rule-based categorization is case insensitive"""
        result = processor.rule_based_categorize("BANditS ROBBED a store")
        assert result == {"category": "Banditry", "confidence": 70}

    async def test_categorize_articles_batch_circuit_breaker_fallback(self, processor, mock_client):
        """Test batch categorization falls back to rule-based when circuit breaker is open"""
        from circuitbreaker import CircuitBreakerError
        
        # Mock circuit breaker error for all calls
        mock_client.post.side_effect = CircuitBreakerError("Circuit breaker open")

        articles = [
            {"_id": "1", "title": "Robbery", "content": "Armed bandits robbed a bank"},
            {"_id": "2", "title": "Abduction", "content": "Kidnappers took hostages"}
        ]

        results = await processor.categorize_articles_batch(articles)

        # Should return rule-based results
        assert len(results) == 2
        assert results[0] == {"id": "1", "category": "Banditry", "confidence": 70}
        assert results[1] == {"id": "2", "category": "Kidnapping", "confidence": 75}
