import pytest
from unittest.mock import AsyncMock, MagicMock
from intelligence_api.services.categorization_service import CategorizationService
from intelligence_api.repositories.mongodb_repository import MongoDBRepository
from intelligence_api.services.llm_processor import LLMProcessor


@pytest.mark.asyncio
class TestCategorizationService:
    @pytest.fixture
    def mock_mongodb_repo(self):
        repo = MagicMock(spec=MongoDBRepository)
        return repo

    @pytest.fixture
    def mock_llm_processor(self):
        processor = MagicMock(spec=LLMProcessor)
        return processor

    @pytest.fixture
    def service(self, mock_mongodb_repo, mock_llm_processor):
        return CategorizationService(mock_mongodb_repo, mock_llm_processor)

    async def test_categorize_articles_no_uncategorized(self, service, mock_mongodb_repo, mock_llm_processor):
        """Test when no uncategorized articles exist"""
        mock_mongodb_repo.get_uncategorized_articles.return_value = []

        result = await service.categorize_articles()

        assert result["status"] == "success"
        assert result["articles_categorized"] == 0
        assert "No new articles" in result["message"]
        mock_llm_processor.categorize_articles_batch.assert_not_called()

    async def test_categorize_articles_success(self, service, mock_mongodb_repo, mock_llm_processor):
        """Test successful categorization of articles"""
        # Mock uncategorized articles
        articles = [
            {"_id": "1", "title": "Test", "content": "Content"},
            {"_id": "2", "title": "Test2", "content": "Content2"}
        ]
        mock_mongodb_repo.get_uncategorized_articles.return_value = articles

        # Mock LLM batch results
        batch_results = [
            {"id": "1", "category": "Banditry"},
            {"id": "2", "category": "Kidnapping"}
        ]
        mock_llm_processor.categorize_articles_batch.return_value = batch_results

        # Mock DB updates
        mock_mongodb_repo.update_article_category.return_value = True

        result = await service.categorize_articles()

        assert result["status"] == "success"
        assert result["articles_categorized"] == 2
        assert "Successfully categorized 2 articles" in result["message"]
        mock_llm_processor.categorize_articles_batch.assert_called_once_with(articles)
        assert mock_mongodb_repo.update_article_category.call_count == 2

    async def test_categorize_articles_partial_success(self, service, mock_mongodb_repo, mock_llm_processor):
        """Test partial success in categorization"""
        articles = [{"_id": "1", "title": "Test", "content": "Content"}]
        mock_mongodb_repo.get_uncategorized_articles.return_value = articles

        batch_results = [{"id": "1", "category": "Banditry"}]
        mock_llm_processor.categorize_articles_batch.return_value = batch_results

        # First call succeeds, second fails
        mock_mongodb_repo.update_article_category.side_effect = [True, False]

        result = await service.categorize_articles()

        # Should still count as success since at least one succeeded
        assert result["status"] == "success"
        assert result["articles_categorized"] == 1

    async def test_categorize_articles_no_batch_results(self, service, mock_mongodb_repo, mock_llm_processor):
        """Test when LLM returns no results"""
        articles = [{"_id": "1", "title": "Test", "content": "Content"}]
        mock_mongodb_repo.get_uncategorized_articles.return_value = articles

        mock_llm_processor.categorize_articles_batch.return_value = []

        result = await service.categorize_articles()

        assert result["status"] == "warning"
        assert result["articles_categorized"] == 0
        assert "No categorization results" in result["message"]

    async def test_categorize_articles_exception(self, service, mock_mongodb_repo, mock_llm_processor):
        """Test exception during categorization"""
        mock_mongodb_repo.get_uncategorized_articles.side_effect = Exception("DB Error")

        result = await service.categorize_articles()

        assert result["status"] == "error"
        assert result["articles_categorized"] == 0
        assert "DB Error" in result["message"]

    def test_stop_background_categorizer(self, service):
        """Test stopping the background categorizer"""
        service._running = True
        service.stop_background_categorizer()
        assert service._running is False

    async def test_start_background_categorizer_stops_gracefully(self, service, mock_mongodb_repo, mock_llm_processor):
        """Test that background categorizer can be stopped"""
        # Mock to return no articles so it doesn't loop forever
        mock_mongodb_repo.get_uncategorized_articles.return_value = []
        mock_llm_processor.categorize_articles_batch.return_value = []

        # Start the task
        import asyncio
        task = asyncio.create_task(service.start_background_categorizer())

        # Let it run briefly
        await asyncio.sleep(0.1)

        # Stop it
        service.stop_background_categorizer()

        # Wait for task to complete
        await asyncio.wait_for(task, timeout=1.0)

        assert not service._running
