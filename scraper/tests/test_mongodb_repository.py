import pytest
from unittest.mock import MagicMock, patch
from scraper.repositories.mongodb_repository import MongoDBRepository
from scraper.models import Article


class TestMongoDBRepository:
    """Test cases for MongoDBRepository"""
    
    @pytest.fixture
    def mock_client(self):
        """Mock MongoDB client"""
        with patch('scraper.repositories.mongodb_repository.MongoClient') as mock_mongo:
            mock_client = MagicMock()
            mock_mongo.return_value = mock_client
            
            # Mock database and collections
            mock_db = MagicMock()
            mock_client.__getitem__.return_value = mock_db
            mock_client.admin = MagicMock()
            mock_client.admin.command.return_value = {"ok": 1}
            
            mock_collection = MagicMock()
            mock_db.__getitem__.return_value = mock_collection
            
            yield mock_client, mock_db, mock_collection
    
    @pytest.fixture
    def repository(self, mock_client):
        """Create MongoDBRepository instance for testing"""
        with patch('scraper.repositories.mongodb_repository.MongoClient'):
            repo = MongoDBRepository()
            return repo
    
    def test_connect_success(self, repository):
        """Test successful MongoDB connection"""
        assert repository.client is not None
        assert repository.db is not None
        assert repository.collection is not None
    
    def test_save_articles_success(self, repository, mock_client):
        """Test successful article saving"""
        mock_client, mock_db, mock_collection = mock_client
        
        # Mock update_one result
        mock_result = MagicMock()
        mock_result.upserted_id = "test_id"
        mock_collection.update_one.return_value = mock_result
        
        articles = [
            {
                "title": "Test Article",
                "content": "Test content",
                "source": "test.com",
                "url": "https://test.com/article1",
                "scraped_at": "2024-01-01T00:00:00"
            },
            {
                "title": "Test Article 2",
                "content": "Test content 2",
                "source": "test.com",
                "url": "https://test.com/article2",
                "scraped_at": "2024-01-01T00:00:00"
            }
        ]
        
        result = repository.save_articles(articles)
        
        assert result is True
        assert mock_collection.update_one.call_count == 2
    
    def test_save_articles_failure(self, repository, mock_client):
        """Test article saving failure"""
        mock_client, mock_db, mock_collection = mock_client
        
        # Mock PyMongoError
        from pymongo.errors import PyMongoError
        mock_collection.update_one.side_effect = PyMongoError("Connection error")
        
        articles = [{"title": "Test", "content": "Content", "source": "test.com", "url": "https://test.com"}]
        
        result = repository.save_articles(articles)
        
        assert result is False
    
    def test_get_articles_success(self, repository, mock_client):
        """Test successful article retrieval"""
        mock_client, mock_db, mock_collection = mock_client
        
        # Mock find result
        mock_cursor = MagicMock()
        mock_collection.find.return_value = mock_cursor
        mock_cursor.sort.return_value = mock_cursor
        mock_cursor.limit.return_value = mock_cursor
        mock_cursor.__iter__.return_value = iter([
            {"_id": "507f1f77bcf86cd799439011", "title": "Test Article", "content": "Content"}
        ])
        
        result = repository.get_articles()
        
        assert len(result) == 1
        assert result[0]["title"] == "Test Article"
        assert result[0]["_id"] == "507f1f77bcf86cd799439011"
    
    def test_get_article_by_url_success(self, repository, mock_client):
        """Test successful article retrieval by URL"""
        mock_client, mock_db, mock_collection = mock_client
        
        # Mock find_one result
        mock_collection.find_one.return_value = {
            "_id": "507f1f77bcf86cd799439011",
            "title": "Test Article",
            "url": "https://test.com/article"
        }
        
        result = repository.get_article_by_url("https://test.com/article")
        
        assert result is not None
        assert result["title"] == "Test Article"
        assert result["_id"] == "507f1f77bcf86cd799439011"
    
    def test_health_check_success(self, repository, mock_client):
        """Test successful health check"""
        mock_client, mock_db, mock_collection = mock_client
        mock_client.admin.command.return_value = {"ok": 1}
        
        result = repository.health_check()
        
        assert result is True
    
    def test_health_check_failure(self, repository, mock_client):
        """Test health check failure"""
        mock_client, mock_db, mock_collection = mock_client
        mock_client.admin.command.side_effect = Exception("Connection error")
        
        result = repository.health_check()
        
        assert result is False
    
    def test_close_connection(self, repository, mock_client):
        """Test closing MongoDB connection"""
        mock_client, mock_db, mock_collection = mock_client
        
        repository.close()
        
        mock_client.close.assert_called_once()
