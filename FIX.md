# Code Review Fixes - Implementation Guide
## Nextier Signal Engine

**Review Date:** 2026-01-11  
**Status:** APPROVED WITH CONDITIONS  
**Priority:** Complete Critical & High items before production deployment

---

## 🔴 CRITICAL PRIORITY (Week 1)

### 1. Fix LLM Service and Remove Bypass

**File:** `intelligence_api/services/llm_service.py`

**Current Issue:** LLM completely bypassed at line 142-144

**Steps to Fix:**

1. **Update the system prompt in config:**

```python
# intelligence_api/utils/config.py

# Add this to Config class:
SYSTEM_PROMPT: str = """You are an expert at extracting conflict event data from Nigerian news articles.

Analyze the provided text and extract EXACTLY ONE conflict event.

Return a SINGLE JSON object (NOT an array) with these exact fields:
{
  "Event_Type": "attack",
  "State": "Lagos", 
  "LGA": "Ikeja",
  "Severity": "high"
}

Rules:
- Event_Type must be ONE of: attack, protest, clash, kidnapping, banditry, terrorism, communal, violence
- State must be a valid Nigerian state name
- LGA must be a Local Government Area name
- Severity must be ONE of: low, medium, high, critical

Return ONLY the JSON object, no additional text or arrays."""
```

2. **Remove the bypass in llm_service.py:**

```python
# intelligence_api/services/llm_service.py:139-155

async def process_articles_batch(self, articles: list) -> list:
    """Process multiple articles concurrently"""
    try:
        # REMOVE THESE 3 LINES:
        # logger.info("LLM processing bypassed - using simple extractor fallback")
        # return []
        
        # RESTORE ORIGINAL LOGIC:
        semaphore = asyncio.Semaphore(Config.MAX_CONCURRENT_PROCESSING)
        
        async def process_with_semaphore(article):
            async with semaphore:
                return await self.parse_article_with_llm(article)
        
        tasks = [process_with_semaphore(article) for article in articles]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out None and exceptions
        parsed_events = []
        for result in results:
            if isinstance(result, ParsedEvent):
                parsed_events.append(result.dict())
            elif isinstance(result, Exception):
                logger.warning("Article processing failed", error=str(result))
        
        logger.info("Processed articles batch", 
                   total=len(articles), 
                   successful=len(parsed_events))
        return parsed_events
```

3. **Update LLM response parsing to handle single objects:**

```python
# intelligence_api/services/llm_service.py:78-91

# REPLACE the validation section with:
parsed_data = json.loads(json_str)

# Handle both single object and array responses for backward compatibility
if isinstance(parsed_data, list):
    if len(parsed_data) > 0:
        parsed_data = parsed_data[0]  # Take first element
    else:
        logger.warning("LLM returned empty array")
        return None

# Validate required fields
required_fields = ["Event_Type", "State", "LGA", "Severity"]
if all(field in parsed_data for field in required_fields):
    return {
        "event_type": parsed_data.get("Event_Type", "unknown"),
        "state": parsed_data.get("State", "unknown") or "unknown",
        "lga": parsed_data.get("LGA", "unknown") or "unknown",
        "severity": parsed_data.get("Severity", "unknown").lower() or "unknown"
    }
```

4. **Test the fix:**

```bash
# Restart intelligence API
docker compose restart intelligence-api

# Wait for startup
sleep 10

# Trigger analysis
curl -X POST http://localhost:8001/api/v1/analyze

# Check logs for LLM processing
docker logs intelligence-api-service --tail 50 | grep -E "LLM|Processed articles"
```

**Estimated Effort:** 4 hours  
**Testing Required:** Yes - verify LLM returns valid events

---

## 🟠 HIGH PRIORITY (Week 1-2)

### 2. Standardize CORS Configuration

**Files:** 
- `scraper/utils/config.py:25`
- `intelligence_api/utils/config.py:33`
- `predictor/utils/config.py:25`

**Steps to Fix:**

1. **Create environment-specific configuration:**

```python
# In each service's utils/config.py, replace ALLOWED_ORIGINS with:

# CORS configuration - environment specific
ENVIRONMENT: str = os.getenv('ENVIRONMENT', 'development')

if ENVIRONMENT == 'production':
    ALLOWED_ORIGINS: list = os.getenv(
        'ALLOWED_ORIGINS',
        'https://nextier.example.com'
    ).split(',')
else:
    # Development - single origin
    ALLOWED_ORIGINS: list = ['http://localhost:5173']
```

2. **Update docker-compose.yml:**

```yaml
# Add to each service's environment section:
environment:
  - ENVIRONMENT=development
  - ALLOWED_ORIGINS=http://localhost:5173
```

3. **Create production .env.production:**

```bash
# .env.production
ENVIRONMENT=production
ALLOWED_ORIGINS=https://nextier.example.com,https://app.nextier.example.com
```

**Estimated Effort:** 2 hours  
**Testing Required:** Test both dev and prod configs

---

### 3. Add Input Validation to Simple Extractor

**File:** `intelligence_api/services/simple_extractor.py`

**Steps to Fix:**

```python
# intelligence_api/services/simple_extractor.py:135-150

def simple_extract_event(article: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Extract event data from article using simple rules
    
    Args:
        article: Article dictionary with title and content
    
    Returns:
        Event dictionary or None if not conflict-related or invalid
    """
    try:
        # VALIDATE INPUT TYPE
        if not isinstance(article, dict):
            logger.warning("Invalid article type", type=type(article).__name__)
            return None
        
        # VALIDATE REQUIRED FIELDS
        title = article.get('title', '')
        content = article.get('content', '')
        url = article.get('url', '')
        
        if not title or not isinstance(title, str):
            logger.warning("Missing or invalid title", url=url)
            return None
            
        if not content or not isinstance(content, str):
            logger.warning("Missing or invalid content", url=url)
            return None
        
        # VALIDATE MINIMUM LENGTH
        if len(title) < 10:
            logger.debug("Title too short", title_length=len(title), url=url)
            return None
            
        if len(content) < 50:
            logger.debug("Content too short", content_length=len(content), url=url)
            return None
        
        combined_text = f"{title} {content}"
        
        # REST OF EXISTING LOGIC...
```

**Estimated Effort:** 1 hour  
**Testing Required:** Unit tests for edge cases

---

### 4. Fix MongoDB Collection Boolean Comparisons

**Files:** All repository files

**Steps to Fix:**

1. **Search for all instances:**

```bash
cd /Users/ejikeudeze/AI_Projects/nextier-signal-engine-core
grep -r "if not self\\..*collection" --include="*.py" intelligence_api/ predictor/ scraper/
```

2. **Fix each instance:**

```python
# WRONG:
if not self.collection:
    return []

# CORRECT:
if self.collection is None:
    return []
```

3. **Files to check:**
   - `intelligence_api/repositories/mongodb_repository.py`
   - `predictor/repositories/mongodb_repository.py`
   - `scraper/repositories/mongodb_repository.py`

**Estimated Effort:** 30 minutes  
**Testing Required:** Verify MongoDB operations still work

---

## 🟡 MEDIUM PRIORITY (Week 2-3)

### 5. Standardize Error Handling Pattern

**All service files**

**Steps to Fix:**

1. **Create common result class:**

```python
# Create new file: common/models/service_result.py

from typing import Optional, Any, Generic, TypeVar
from pydantic import BaseModel

T = TypeVar('T')

class ServiceResult(BaseModel, Generic[T]):
    """Standardized service operation result"""
    success: bool
    data: Optional[T] = None
    error: Optional[str] = None
    error_code: Optional[str] = None
    
    @classmethod
    def ok(cls, data: T) -> 'ServiceResult[T]':
        """Create successful result"""
        return cls(success=True, data=data)
    
    @classmethod
    def fail(cls, error: str, error_code: str = None) -> 'ServiceResult[T]':
        """Create failed result"""
        return cls(success=False, error=error, error_code=error_code)
```

2. **Update service methods to use ServiceResult:**

```python
# Example: scraper/services/scraping_service.py

async def fetch_page(self, url: str) -> ServiceResult[str]:
    """Fetch a web page with standardized error handling"""
    try:
        response = await self.client.get(url, timeout=15.0)
        response.raise_for_status()
        return ServiceResult.ok(response.text)
    except httpx.TimeoutException:
        return ServiceResult.fail("Request timeout", "TIMEOUT")
    except httpx.HTTPStatusError as e:
        return ServiceResult.fail(f"HTTP {e.response.status_code}", "HTTP_ERROR")
```

**Estimated Effort:** 8 hours (refactor multiple services)  
**Testing Required:** Integration tests for all services

---

### 6. Extract Common Entrypoint Logic

**Files:** `*/entrypoint.sh`

**Steps to Fix:**

1. **Create shared script:**

```bash
# scripts/fix_docker_imports.sh
#!/bin/bash
set -e

SERVICE_NAME=$1
SERVICE_DIR=$2

echo "Fixing imports for ${SERVICE_NAME}..."

# Create __init__.py files
touch ${SERVICE_DIR}/__init__.py
touch ${SERVICE_DIR}/api/__init__.py
touch ${SERVICE_DIR}/models/__init__.py
touch ${SERVICE_DIR}/services/__init__.py
touch ${SERVICE_DIR}/repositories/__init__.py
touch ${SERVICE_DIR}/utils/__init__.py

# Fix main.py imports
sed -i "s/from api import/from ${SERVICE_NAME}.api import/g" ${SERVICE_DIR}/main.py
sed -i "s/from utils import/from ${SERVICE_NAME}.utils import/g" ${SERVICE_DIR}/main.py
sed -i "s/from services import/from ${SERVICE_NAME}.services import/g" ${SERVICE_DIR}/main.py
sed -i "s/from repositories import/from ${SERVICE_NAME}.repositories import/g" ${SERVICE_DIR}/main.py
sed -i "s/from models import/from ${SERVICE_NAME}.models import/g" ${SERVICE_DIR}/main.py

# Fix module imports
find ${SERVICE_DIR}/api -name "*.py" -exec sed -i "s/from models import/from ${SERVICE_NAME}.models import/g" {} \;
find ${SERVICE_DIR}/api -name "*.py" -exec sed -i "s/from services import/from ${SERVICE_NAME}.services import/g" {} \;

echo "Import fixes complete for ${SERVICE_NAME}"
```

2. **Update each entrypoint.sh:**

```bash
#!/bin/bash
set -e

echo "Starting Scraper Service..."
export PYTHONPATH="/app:$PYTHONPATH"
cd /app

# Use shared script
/app/scripts/fix_docker_imports.sh scraper scraper

echo "Starting FastAPI application..."
exec uvicorn scraper.main:app --host 0.0.0.0 --port 8000 --reload
```

**Estimated Effort:** 3 hours  
**Testing Required:** Verify all services start correctly

---

### 7. Add Retry Logic to RSS Parser

**File:** `scraper/utils/rss_parser.py`

**Steps to Fix:**

```python
# scraper/utils/rss_parser.py

from tenacity import retry, stop_after_attempt, wait_exponential, RetryError

class RSSParser:
    """Parse RSS feeds and extract article data"""
    
    @staticmethod
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True
    )
    def parse_feed(feed_url: str, max_articles: int = 10) -> List[Dict[str, Any]]:
        """
        Parse an RSS feed and extract articles with retry logic
        
        Args:
            feed_url: URL of the RSS feed
            max_articles: Maximum number of articles to extract
            
        Returns:
            List of article dictionaries
            
        Raises:
            RetryError: If all retry attempts fail
        """
        try:
            logger.info(f"Parsing RSS feed (with retry)", url=feed_url)
            
            # Parse the feed
            feed = feedparser.parse(feed_url)
            
            # Check if feed was successfully parsed
            if feed.bozo:
                error_msg = str(feed.bozo_exception) if hasattr(feed, 'bozo_exception') else "Unknown error"
                logger.warning(f"RSS feed has parsing issues", url=feed_url, error=error_msg)
                # Raise to trigger retry
                raise Exception(f"RSS parse error: {error_msg}")
            
            # REST OF EXISTING LOGIC...
```

**Estimated Effort:** 1 hour  
**Testing Required:** Test with unreliable RSS feeds

---

### 8. Externalize Hardcoded Limits

**File:** `intelligence_api/services/processing_service.py`

**Steps to Fix:**

```python
# intelligence_api/utils/config.py

# Add to Config class:
MAX_EVENTS_QUERY_LIMIT: int = int(os.getenv('MAX_EVENTS_QUERY_LIMIT', '1000'))
MAX_CONCURRENT_PROCESSING: int = int(os.getenv('MAX_CONCURRENT_PROCESSING', '5'))
```

```python
# intelligence_api/services/processing_service.py:30,79

# REPLACE:
total_events = len(self.mongodb_repo.get_parsed_events(limit=1000))

# WITH:
total_events = len(self.mongodb_repo.get_parsed_events(limit=Config.MAX_EVENTS_QUERY_LIMIT))
```

**Estimated Effort:** 30 minutes  
**Testing Required:** Verify configuration is respected

---

## 🟢 LOW PRIORITY (Week 3-4)

### 9. Improve Structured Logging

**All service files**

**Steps to Fix:**

```python
# Add to all logger calls:

# BEFORE:
logger.info("Retrieved unprocessed articles", count=len(unprocessed))

# AFTER:
logger.info(
    "Retrieved unprocessed articles",
    count=len(unprocessed),
    collection="articles",
    service="intelligence_api",
    timestamp=datetime.now().isoformat()
)
```

**Estimated Effort:** 2 hours  
**Testing Required:** Verify log aggregation works

---

### 10. Add Integration Tests

**Create:** `tests/integration/test_pipeline.py`

```python
import pytest
import httpx
import asyncio

@pytest.mark.asyncio
async def test_full_pipeline():
    """Test complete scraper -> intelligence -> predictor pipeline"""
    
    # 1. Trigger scraping
    async with httpx.AsyncClient() as client:
        scrape_response = await client.get("http://localhost:8000/api/v1/scrape")
        assert scrape_response.status_code == 200
        scrape_data = scrape_response.json()
        assert scrape_data["articles_scraped"] > 0
    
    # 2. Wait for processing
    await asyncio.sleep(5)
    
    # 3. Verify events created
    async with httpx.AsyncClient() as client:
        events_response = await client.get("http://localhost:8001/api/v1/events")
        assert events_response.status_code == 200
        events_data = events_response.json()
        assert events_data["count"] > 0
    
    # 4. Verify risk signals generated
    async with httpx.AsyncClient() as client:
        signals_response = await client.get("http://localhost:8002/api/v1/signals")
        assert signals_response.status_code == 200
        signals_data = signals_response.json()
        assert signals_data["count"] > 0

@pytest.mark.asyncio
async def test_stress_test_endpoint():
    """Test stress test simulation"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8002/api/v1/simulate",
            json={
                "fuel_price_index": 95,
                "inflation_rate": 85,
                "chatter_intensity": 90
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["metadata"]["total_events"] > 0
```

**Estimated Effort:** 4 hours  
**Testing Required:** Run in CI/CD pipeline

---

## 📋 IMPLEMENTATION CHECKLIST

### Week 1 (Critical & High Priority)
- [ ] Fix LLM prompt and remove bypass
- [ ] Test LLM with real articles
- [ ] Standardize CORS configuration
- [ ] Add input validation to simple extractor
- [ ] Fix MongoDB collection comparisons
- [ ] Deploy to development environment
- [ ] Verify all endpoints working

### Week 2 (Medium Priority - Part 1)
- [ ] Create ServiceResult class
- [ ] Refactor scraper service error handling
- [ ] Refactor intelligence API error handling
- [ ] Refactor predictor service error handling
- [ ] Extract common entrypoint logic
- [ ] Test all services restart correctly

### Week 3 (Medium Priority - Part 2)
- [ ] Add retry logic to RSS parser
- [ ] Externalize hardcoded limits
- [ ] Improve structured logging
- [ ] Add integration tests
- [ ] Run full test suite
- [ ] Performance testing

### Week 4 (Low Priority & Polish)
- [ ] Security audit
- [ ] Add rate limiting
- [ ] Add request size limits
- [ ] Documentation updates
- [ ] Code coverage report
- [ ] Production deployment prep

---

## 🧪 TESTING STRATEGY

### Unit Tests
```bash
# Run unit tests for each service
cd scraper && pytest tests/unit/
cd intelligence_api && pytest tests/unit/
cd predictor && pytest tests/unit/
```

### Integration Tests
```bash
# Start all services
docker compose up -d

# Run integration tests
pytest tests/integration/ -v

# Check results
docker compose logs
```

### Manual Testing
```bash
# 1. Test scraping
curl -X GET http://localhost:8000/api/v1/scrape

# 2. Test analysis
curl -X POST http://localhost:8001/api/v1/analyze

# 3. Test prediction
curl -X POST http://localhost:8002/api/v1/predict

# 4. Test simulation
curl -X POST http://localhost:8002/api/v1/simulate \
  -H "Content-Type: application/json" \
  -d '{"fuel_price_index": 95, "inflation_rate": 85, "chatter_intensity": 90}'

# 5. Verify UI
open http://localhost:5173
```

---

## 📊 SUCCESS METRICS

- [ ] LLM processing success rate > 80%
- [ ] All integration tests passing
- [ ] Code coverage > 70%
- [ ] No critical security vulnerabilities
- [ ] API response time < 2s (p95)
- [ ] Zero unhandled exceptions in logs
- [ ] All services restart successfully

---

## 🚀 DEPLOYMENT PLAN

### Development
1. Implement fixes in feature branches
2. Run full test suite
3. Code review
4. Merge to development
5. Deploy to dev environment
6. Smoke test

### Staging
1. Merge development to staging
2. Run integration tests
3. Performance testing
4. Security scan
5. UAT (User Acceptance Testing)

### Production
1. Create release branch
2. Final security audit
3. Backup database
4. Deploy during maintenance window
5. Monitor logs and metrics
6. Rollback plan ready

---

## 📞 SUPPORT

**Questions?** Contact the development team:
- Technical Lead: [Your Name]
- DevOps: [DevOps Team]
- Security: [Security Team]

**Documentation:**
- Architecture: `ARCHITECTURE.md`
- API Docs: `http://localhost:8000/docs`
- Deployment: `DEPLOYMENT.md`

---

**Last Updated:** 2026-01-11  
**Next Review:** After Week 1 implementation
