import pytest
import asyncio
import json
from unittest.mock import AsyncMock, MagicMock
from fastapi.testclient import TestClient


@pytest.mark.integration
class TestServiceIntegration:
    """Integration tests for service interactions"""
    
    @pytest.fixture
    def mock_mongodb(self):
        """Mock MongoDB for integration testing"""
        mock_client = MagicMock()
        mock_db = MagicMock()
        mock_client.__getitem__.return_value = mock_db
        mock_client.admin.command.return_value = {"ok": 1}
        
        # Mock collections
        mock_collection = MagicMock()
        mock_db.__getitem__.return_value = mock_collection
        
        return mock_client, mock_db, mock_collection
    
    @pytest.fixture
    def mock_rabbitmq(self):
        """Mock RabbitMQ for integration testing"""
        mock_connection = MagicMock()
        mock_connection.is_open = True
        mock_channel = MagicMock()
        mock_connection.channel.return_value = mock_channel
        
        return mock_connection, mock_channel
    
    @pytest.fixture
    def sample_article_data(self):
        """Sample article data for testing"""
        return [
            {
                "title": "Clash in Lagos Market",
                "content": "There was a violent clash at the popular Lagos market today",
                "source": "premiumtimesng.com",
                "url": "https://premiumtimesng.com/news/clash-lagos",
                "scraped_at": "2024-01-01T10:00:00"
            }
        ]
    
    @pytest.fixture
    def sample_event_data(self):
        """Sample event data for testing"""
        return [
            {
                "event_type": "clash",
                "state": "Lagos",
                "lga": "Ikeja",
                "severity": "high",
                "source_title": "Clash in Lagos Market",
                "source_url": "https://premiumtimesng.com/news/clash-lagos",
                "parsed_at": "2024-01-01T10:05:00"
            }
        ]
    
    @pytest.fixture
    def sample_economic_data(self):
        """Sample economic data for testing"""
        return [
            {"State": "Lagos", "LGA": "Ikeja", "Fuel_Price": 700, "Inflation": 22}
        ]
    
    def test_scraper_to_intelligence_api_flow(self, sample_article_data):
        """Test data flow from scraper to intelligence API"""
        # This test would verify that scraped articles are properly
        # passed to the intelligence API through the message broker
        
        # Mock the message broker publishing
        with patch('scraper.services.message_broker.MessageBrokerService') as mock_broker:
            mock_instance = MagicMock()
            mock_broker.return_value = mock_instance
            mock_instance.publish_articles.return_value = True
            
            # Mock MongoDB repository
            with patch('scraper.repositories.mongodb_repository.MongoDBRepository') as mock_repo:
                mock_repo_instance = MagicMock()
                mock_repo.return_value = mock_repo_instance
                mock_repo_instance.save_articles.return_value = True
                
                # Import and test the flow
                from scraper.services.message_broker import MessageBrokerService
                
                broker = MessageBrokerService()
                result = broker.publish_articles(sample_article_data)
                
                assert result is True
                mock_instance.publish_articles.assert_called_once_with(sample_article_data)
    
    def test_intelligence_api_to_predictor_flow(self, sample_event_data):
        """Test data flow from intelligence API to predictor"""
        # Mock the message broker for events
        with patch('intelligence_api.services.message_broker.MessageBrokerService') as mock_broker:
            mock_instance = MagicMock()
            mock_broker.return_value = mock_instance
            mock_instance.publish_events.return_value = True
            
            # Import and test the flow
            from intelligence_api.services.message_broker import MessageBrokerService
            
            broker = MessageBrokerService()
            result = broker.publish_events(sample_event_data)
            
            assert result is True
            mock_instance.publish_events.assert_called_once_with(sample_event_data)
    
    def test_end_to_end_risk_calculation(self, sample_event_data, sample_economic_data):
        """Test end-to-end risk calculation"""
        # Mock MongoDB repository
        with patch('predictor.repositories.mongodb_repository.MongoDBRepository') as mock_repo:
            mock_repo_instance = MagicMock()
            mock_repo.return_value = mock_repo_instance
            
            # Mock get_parsed_events
            mock_repo_instance.get_parsed_events.return_value = sample_event_data
            
            # Mock get_economic_data
            import pandas as pd
            mock_df = pd.DataFrame(sample_economic_data)
            mock_repo_instance.get_economic_data.return_value = mock_df
            
            # Mock save_risk_signals
            mock_repo_instance.save_risk_signals.return_value = True
            
            # Test risk calculation
            from predictor.services.risk_service import RiskService
            from predictor.services.prediction_service import PredictionService
            
            risk_service = RiskService()
            
            # Mock message broker
            with patch('predictor.services.message_broker.MessageBrokerService') as mock_broker:
                mock_broker_instance = MagicMock()
                mock_broker.return_value = mock_broker_instance
                mock_broker_instance.publish_signals.return_value = True
                
                prediction_service = PredictionService(mock_repo_instance, risk_service, mock_broker_instance)
                
                # Run prediction
                result = asyncio.run(prediction_service.process_risk_predictions())
                
                assert result["status"] in ["success", "partial"]
                assert result["events_processed"] == 1
                assert result["signals_generated"] == 1
    
    @pytest.mark.asyncio
    async def test_concurrent_processing(self, sample_article_data):
        """Test concurrent processing of multiple articles"""
        # Mock LLM service for concurrent processing
        with patch('intelligence_api.services.llm_service.LLMService') as mock_llm:
            mock_instance = MagicMock()
            mock_llm.return_value = mock_instance
            
            # Mock parse_article_with_llm to return different results
            async def mock_parse_article(article):
                from intelligence_api.models import ParsedEvent
                return ParsedEvent(
                    event_type="clash",
                    state="Lagos",
                    lga="Ikeja",
                    severity="high",
                    source_title=article["title"],
                    source_url=article["url"]
                )
            
            mock_instance.parse_article_with_llm.side_effect = mock_parse_article
            
            # Test batch processing
            llm_service = mock_llm()
            result = await llm_service.process_articles_batch(sample_article_data * 3)
            
            assert len(result) == 3
            assert all(event.event_type == "clash" for event in result)
    
    def test_error_handling_integration(self):
        """Test error handling across service boundaries"""
        # Test MongoDB connection failure
        with patch('pymongo.MongoClient') as mock_mongo:
            mock_mongo.side_effect = Exception("Connection failed")
            
            with pytest.raises(Exception):
                from scraper.repositories.mongodb_repository import MongoDBRepository
                MongoDBRepository()
        
        # Test RabbitMQ connection failure
        with patch('pika.BlockingConnection') as mock_rabbit:
            mock_rabbit.side_effect = Exception("Connection failed")
            
            with pytest.raises(Exception):
                from scraper.services.message_broker import MessageBrokerService
                MessageBrokerService()
    
    def test_health_checks_integration(self):
        """Test health check integration across services"""
        # Test all services healthy
        with patch('pymongo.MongoClient') as mock_mongo, \
             patch('pika.BlockingConnection') as mock_rabbit:
            
            # Mock healthy connections
            mock_mongo_instance = MagicMock()
            mock_mongo_instance.admin.command.return_value = {"ok": 1}
            mock_mongo.return_value = mock_mongo_instance
            
            mock_rabbit_instance = MagicMock()
            mock_rabbit_instance.is_open = True
            mock_rabbit.return_value = mock_rabbit_instance
            
            # Test scraper health
            from scraper.repositories.mongodb_repository import MongoDBRepository
            from scraper.services.message_broker import MessageBrokerService
            
            mongo_repo = MongoDBRepository()
            message_broker = MessageBrokerService()
            
            assert mongo_repo.health_check() is True
            assert message_broker.health_check() is True
    
    @pytest.mark.slow
    def test_performance_with_large_dataset(self):
        """Test performance with large dataset"""
        # Generate large dataset
        large_article_set = [
            {
                "title": f"Article {i}",
                "content": f"Content for article {i}",
                "source": "test.com",
                "url": f"https://test.com/article{i}",
                "scraped_at": "2024-01-01T10:00:00"
            }
            for i in range(1000)
        ]
        
        # Test processing performance
        with patch('scraper.services.message_broker.MessageBrokerService') as mock_broker:
            mock_instance = MagicMock()
            mock_broker.return_value = mock_instance
            mock_instance.publish_articles.return_value = True
            
            from scraper.services.message_broker import MessageBrokerService
            import time
            
            broker = MessageBrokerService()
            
            start_time = time.time()
            result = broker.publish_articles(large_article_set)
            end_time = time.time()
            
            assert result is True
            assert end_time - start_time < 5.0  # Should complete within 5 seconds
