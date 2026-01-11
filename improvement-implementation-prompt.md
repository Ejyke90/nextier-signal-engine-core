# Nextier Signal Engine Core Improvement Implementation Prompt

## Project Overview
You are tasked with implementing improvements to the Nextier Signal Engine Core, a Python-based microservices application that processes news articles to generate risk signals. The system consists of three main services:

1. **Scraper Service**: Collects news articles from sources
2. **Intelligence API**: Processes articles with LLM to extract events
3. **Predictor Service**: Calculates risk scores based on events and economic data

The services currently communicate through shared files in a Docker volume and have several architectural, security, and performance limitations.

## Implementation Tasks

### 1. Architecture Modernization

#### 1.1 Service Communication
- Replace file-based communication with a message broker
```python
# IMPLEMENT: Add RabbitMQ or Kafka client to each service
# Example for RabbitMQ in scraper service:
import pika

def publish_scraped_articles(articles):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
    channel = connection.channel()
    channel.queue_declare(queue='scraped_articles')
    
    for article in articles:
        channel.basic_publish(
            exchange='',
            routing_key='scraped_articles',
            body=json.dumps(article)
        )
    
    connection.close()
```

#### 1.2 Database Integration
- Replace JSON files with MongoDB for document storage
```python
# IMPLEMENT: Add MongoDB client to each service
# Example for storing articles:
from pymongo import MongoClient

def save_articles_to_db(articles):
    client = MongoClient('mongodb://mongodb:27017/')
    db = client.nextier_signal
    collection = db.raw_articles
    
    # Insert new articles, avoiding duplicates
    for article in articles:
        collection.update_one(
            {'url': article['url']},
            {'$setOnInsert': article},
            upsert=True
        )
```

#### 1.3 Configuration Management
- Move hardcoded values to environment variables
```python
# IMPLEMENT: Use environment variables for configuration
import os

# Replace hardcoded values
OLLAMA_URL = os.getenv('OLLAMA_URL', 'http://host.docker.internal:11434/api/generate')
POLL_INTERVAL = int(os.getenv('POLL_INTERVAL', '30'))
```

### 2. Code Quality Improvements

#### 2.1 Modular Structure
- Refactor monolithic files into modules
```
# IMPLEMENT: Create this directory structure for each service
/service_name
  /api - FastAPI routes
  /models - Pydantic models
  /services - Business logic
  /repositories - Data access
  /utils - Shared utilities
  main.py - Entry point
```

#### 2.2 Dependency Injection
- Implement DI pattern for better testability
```python
# IMPLEMENT: Use dependency injection
from fastapi import Depends

def get_article_service():
    # Create and return service with its dependencies
    return ArticleService(ArticleRepository())

@app.get("/articles")
async def get_articles(service: ArticleService = Depends(get_article_service)):
    return await service.get_all_articles()
```

### 3. Error Handling & Resilience

#### 3.1 Circuit Breakers
- Implement circuit breakers for external calls
```python
# IMPLEMENT: Add circuit breaker for LLM calls
from circuitbreaker import circuit

@circuit(failure_threshold=5, recovery_timeout=30)
async def call_ollama_llm(text: str):
    # Existing LLM call logic
```

#### 3.2 Retry Mechanisms
- Add exponential backoff for transient failures
```python
# IMPLEMENT: Add retry logic
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
async def fetch_with_retry(url):
    # HTTP request logic
```

### 4. Security Enhancements

#### 4.1 Input Validation
- Strengthen validation on all endpoints
```python
# IMPLEMENT: Enhanced validation
from pydantic import BaseModel, Field, HttpUrl

class ArticleCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=200)
    content: str = Field(..., min_length=10)
    source: str = Field(..., min_length=3, max_length=50)
    url: HttpUrl
```

#### 4.2 CORS Configuration
- Restrict CORS to specific origins
```python
# IMPLEMENT: Specific CORS origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://nextier.example.com", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
```

### 5. Performance Optimization

#### 5.1 Connection Pooling
- Implement connection pooling for HTTP clients
```python
# IMPLEMENT: HTTP connection pooling
async def create_http_client():
    return httpx.AsyncClient(
        timeout=30.0,
        limits=httpx.Limits(max_connections=100, max_keepalive_connections=20)
    )
```

#### 5.2 Caching
- Add caching for expensive operations
```python
# IMPLEMENT: Add caching for LLM responses
from functools import lru_cache

@lru_cache(maxsize=100)
def get_cached_llm_response(text_hash):
    # Retrieve from cache or compute
```

### 6. Testing Implementation

#### 6.1 Unit Tests
- Add unit tests for core business logic
```python
# IMPLEMENT: Unit tests with pytest
import pytest

def test_calculate_risk_score():
    # Test risk calculation logic
    event = {"event_type": "clash", "severity": "high", "state": "Lagos", "lga": "Ikeja"}
    econ_data = pd.DataFrame([{"State": "Lagos", "LGA": "Ikeja", "Fuel_Price": 700, "Inflation": 22}])
    
    result = calculate_risk_score(event, econ_data)
    
    assert result is not None
    assert result["risk_score"] > 80  # Based on the special rule
    assert result["risk_level"] == "Critical"
```

#### 6.2 Integration Tests
- Add integration tests for service interactions
```python
# IMPLEMENT: Integration tests
async def test_end_to_end_processing():
    # Test the full pipeline from scraping to risk calculation
```

### 7. DevOps & Observability

#### 7.1 Structured Logging
- Enhance logging with structured data
```python
# IMPLEMENT: Structured logging
import structlog

logger = structlog.get_logger()

logger.info("Processing article", 
    article_id=article.get("id"), 
    source=article.get("source"),
    processing_time=processing_time
)
```

#### 7.2 Health Checks
- Implement detailed health checks
```python
# IMPLEMENT: Enhanced health checks
@app.get("/health")
async def health():
    status = "healthy"
    checks = {}
    
    # Check database connection
    try:
        # DB connection check
        checks["database"] = "connected"
    except Exception as e:
        status = "degraded"
        checks["database"] = str(e)
    
    # Check message broker
    try:
        # Message broker check
        checks["message_broker"] = "connected"
    except Exception as e:
        status = "degraded"
        checks["message_broker"] = str(e)
    
    return {
        "status": status,
        "service": "intelligence-api",
        "checks": checks,
        "timestamp": datetime.now().isoformat()
    }
```

## Implementation Guidelines

1. **Prioritize Changes**: Start with the most critical improvements (architecture, security) before moving to optimizations.

2. **Incremental Approach**: Implement changes incrementally, ensuring each service remains functional.

3. **Backward Compatibility**: Maintain backward compatibility during the transition period.

4. **Testing**: Write tests before implementing changes where possible (TDD approach).

5. **Documentation**: Update documentation as you implement changes.

6. **Docker Configuration**: Update Docker Compose file to include new services (MongoDB, RabbitMQ).

## Docker Compose Updates

```yaml
# IMPLEMENT: Add these services to docker-compose.yml
version: '3.8'

services:
  # Existing services...
  
  mongodb:
    image: mongo:6.0
    container_name: mongodb
    ports:
      - "27017:27017"
    volumes:
      - mongodb_data:/data/db
    networks:
      - signal-engine-network

  rabbitmq:
    image: rabbitmq:3-management
    container_name: rabbitmq
    ports:
      - "5672:5672"
      - "15672:15672"
    networks:
      - signal-engine-network

volumes:
  mongodb_data:
```

## Completion Criteria

The implementation will be considered complete when:

1. All services communicate through the message broker instead of files
2. Data is stored in MongoDB instead of JSON files
3. Configuration is externalized
4. Code is modularized according to the proposed structure
5. Error handling includes circuit breakers and retry mechanisms
6. Security improvements are implemented
7. Performance optimizations are in place
8. Tests are added for critical components
9. Logging and observability are enhanced
10. Docker Compose is updated to include new services

Proceed with implementation, focusing on maintaining the core functionality while improving the architecture, security, and performance of the system.
