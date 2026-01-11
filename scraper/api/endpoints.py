from datetime import datetime
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Request
from scraper.models import HealthResponse, ScrapeResponse
from scraper.services import ScrapingService, MessageBrokerService, AutomationScheduler
from scraper.repositories import MongoDBRepository
from scraper.utils import get_logger, Config

logger = get_logger(__name__)
router = APIRouter()


def get_scraping_service() -> ScrapingService:
    """Dependency injection for scraping service"""
    return ScrapingService()


def get_message_broker() -> MessageBrokerService:
    """Dependency injection for message broker"""
    return MessageBrokerService()


def get_mongodb_repository() -> MongoDBRepository:
    """Dependency injection for MongoDB repository"""
    return MongoDBRepository()


@router.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Welcome to Scraper Service"}


@router.get("/health", response_model=HealthResponse)
async def health(
    mongodb_repo: MongoDBRepository = Depends(get_mongodb_repository),
    message_broker: MessageBrokerService = Depends(get_message_broker)
):
    """Enhanced health check endpoint"""
    status = "healthy"
    checks = {}
    
    # Check MongoDB connection
    try:
        mongodb_healthy = mongodb_repo.health_check()
        checks["mongodb"] = "connected" if mongodb_healthy else "disconnected"
        if not mongodb_healthy:
            status = "degraded"
    except Exception as e:
        status = "degraded"
        checks["mongodb"] = str(e)
    
    # Check RabbitMQ connection
    try:
        rabbitmq_healthy = message_broker.health_check()
        checks["rabbitmq"] = "connected" if rabbitmq_healthy else "disconnected"
        if not rabbitmq_healthy:
            status = "degraded"
    except Exception as e:
        status = "degraded"
        checks["rabbitmq"] = str(e)
    
    return HealthResponse(
        status=status,
        service=Config.SERVICE_NAME,
        checks=checks,
        timestamp=datetime.now().isoformat()
    )


@router.get("/scrape", response_model=ScrapeResponse)
async def scrape_news(
    scraping_service: ScrapingService = Depends(get_scraping_service),
    mongodb_repo: MongoDBRepository = Depends(get_mongodb_repository),
    message_broker: MessageBrokerService = Depends(get_message_broker)
):
    """Scrape latest news from Premium Times"""
    try:
        articles = await scraping_service.scrape_premium_times_latest_news()
        
        if not articles:
            return ScrapeResponse(
                status="warning",
                articles_scraped=0,
                message="No articles were scraped"
            )
        
        # Save to MongoDB
        db_success = mongodb_repo.save_articles(articles)
        
        # Publish to message broker
        mq_success = message_broker.publish_articles(articles)
        
        if db_success and mq_success:
            return ScrapeResponse(
                status="success",
                articles_scraped=len(articles),
                message=f"Successfully scraped, saved, and published {len(articles)} articles"
            )
        else:
            return ScrapeResponse(
                status="partial",
                articles_scraped=len(articles),
                message=f"Scraped {len(articles)} articles but some operations failed"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Unexpected error in scrape_news", error=str(e))
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/articles")
async def get_articles(
    limit: int = 100,
    mongodb_repo: MongoDBRepository = Depends(get_mongodb_repository)
):
    """Get all scraped articles"""
    try:
        articles = mongodb_repo.get_articles(limit)
        return {"articles": articles, "count": len(articles)}
        
    except Exception as e:
        logger.error("Error reading articles", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to read articles")


@router.get("/scheduler/status")
async def get_scheduler_status(request: Request):
    """Get automation scheduler status for UI heartbeat indicator"""
    try:
        # Access scheduler from app state
        if hasattr(request.app.state, 'automation_scheduler'):
            automation_scheduler = request.app.state.automation_scheduler
            status = automation_scheduler.get_status()
            return {
                "status": "active",
                **status
            }
        else:
            return {
                "status": "inactive",
                "message": "Scheduler not initialized"
            }
    except Exception as e:
        logger.error("Error getting scheduler status", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to get scheduler status")


@router.get("/automation/logs")
async def get_automation_logs(limit: int = 20):
    """Get automation logs for system health monitoring"""
    try:
        import json
        from pathlib import Path
        
        log_path = Path("/data/automation_logs.json")
        
        if not log_path.exists():
            return {
                "logs": [],
                "message": "No automation logs available yet"
            }
        
        logs = json.loads(log_path.read_text())
        
        # Return most recent logs
        recent_logs = logs[-limit:] if len(logs) > limit else logs
        recent_logs.reverse()  # Most recent first
        
        return {
            "logs": recent_logs,
            "total_count": len(logs)
        }
        
    except Exception as e:
        logger.error("Error reading automation logs", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to read automation logs")
