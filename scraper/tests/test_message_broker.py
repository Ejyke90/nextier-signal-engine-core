import pytest
import json
from unittest.mock import MagicMock, patch
from scraper.services.message_broker import MessageBrokerService


class TestMessageBrokerService:
    """Test cases for MessageBrokerService"""
    
    @pytest.fixture
    def mock_connection(self):
        """Mock RabbitMQ connection"""
        with patch('scraper.services.message_broker.pika.BlockingConnection') as mock_conn:
            mock_connection = MagicMock()
            mock_connection.is_open = True
            mock_conn.return_value = mock_connection
            
            # Mock channel
            mock_channel = MagicMock()
            mock_connection.channel.return_value = mock_channel
            
            yield mock_connection, mock_channel
    
    @pytest.fixture
    def message_broker(self, mock_connection):
        """Create MessageBrokerService instance for testing"""
        with patch('scraper.services.message_broker.pika.BlockingConnection'):
            broker = MessageBrokerService()
            return broker
    
    def test_connect_success(self, message_broker, mock_connection):
        """Test successful RabbitMQ connection"""
        mock_connection, mock_channel = mock_connection
        
        assert message_broker.connection is not None
        assert message_broker.channel is not None
        
        # Verify queue declaration
        assert mock_channel.queue_declare.called
    
    def test_publish_articles_success(self, message_broker, mock_connection):
        """Test successful article publishing"""
        mock_connection, mock_channel = mock_connection
        
        articles = [
            {
                "title": "Test Article",
                "content": "Test content",
                "source": "test.com",
                "url": "https://test.com/article1"
            },
            {
                "title": "Test Article 2",
                "content": "Test content 2",
                "source": "test.com",
                "url": "https://test.com/article2"
            }
        ]
        
        result = message_broker.publish_articles(articles)
        
        assert result is True
        assert mock_channel.basic_publish.call_count == 2
        
        # Verify message format
        calls = mock_channel.basic_publish.call_args_list
        for call in calls:
            args, kwargs = call
            assert kwargs['routing_key'] == 'scraped_articles'
            assert 'body' in kwargs
            assert kwargs['properties'].delivery_mode == 2  # Persistent
    
    def test_publish_articles_failure(self, message_broker, mock_connection):
        """Test article publishing failure"""
        mock_connection, mock_channel = mock_connection
        
        # Mock AMQPError
        from pika.exceptions import AMQPError
        mock_channel.basic_publish.side_effect = AMQPError("Connection error")
        
        articles = [{"title": "Test", "content": "Content"}]
        
        result = message_broker.publish_articles(articles)
        
        assert result is False
    
    def test_health_check_success(self, message_broker, mock_connection):
        """Test successful health check"""
        mock_connection, mock_channel = mock_connection
        mock_connection.is_open = True
        
        result = message_broker.health_check()
        
        assert result is True
    
    def test_health_check_failure(self, message_broker, mock_connection):
        """Test health check failure"""
        mock_connection, mock_channel = mock_connection
        mock_connection.is_open = False
        
        result = message_broker.health_check()
        
        assert result is False
    
    def test_close_connection(self, message_broker, mock_connection):
        """Test closing RabbitMQ connection"""
        mock_connection, mock_channel = mock_connection
        mock_connection.is_open = True
        
        message_broker.close()
        
        mock_connection.close.assert_called_once()
    
    def test_close_connection_already_closed(self, message_broker, mock_connection):
        """Test closing already closed connection"""
        mock_connection, mock_channel = mock_connection
        mock_connection.is_open = False
        
        message_broker.close()
        
        # Should not attempt to close already closed connection
        mock_connection.close.assert_not_called()
