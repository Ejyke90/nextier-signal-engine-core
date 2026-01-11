import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import internal modules
from scraper.api import router
from scraper.utils import Config, configure_logging, get_logger
from scraper.services import ScrapingService, MessageBrokerService, AutomationScheduler
from scraper.repositories import MongoDBRepository

# Configure logging
configure_logging(Config.LOG_LEVEL)
logger = get_logger(__name__)

# Validate configuration
try:
    Config.validate()
except ValueError as e:
    logger.error("Configuration validation failed", error=str(e))
    raise

# Global services
scraping_service = None
message_broker = None
mongodb_repo = None
automation_scheduler = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle"""
    global scraping_service, message_broker, mongodb_repo, automation_scheduler
    
    logger.info("Starting scraper service")
    
    # Initialize services
    try:
        scraping_service = ScrapingService()
        message_broker = MessageBrokerService()
        mongodb_repo = MongoDBRepository()
        logger.info("Services initialized successfully")
        
        # Start automated background scheduler
        automation_scheduler = AutomationScheduler()
        automation_scheduler.start()
        logger.info("🤖 Automated background scheduler started")
        
    except Exception as e:
        logger.error("Failed to initialize services", error=str(e))
        raise
    
    yield
    
    # Cleanup
    logger.info("Shutting down scraper service")
    try:
        if automation_scheduler:
            automation_scheduler.stop()
            logger.info("Automation scheduler stopped")
        if scraping_service:
            await scraping_service.close()
        if message_broker:
            message_broker.close()
        if mongodb_repo:
            mongodb_repo.close()
        logger.info("Services cleaned up successfully")
    except Exception as e:
        logger.error("Error during cleanup", error=str(e))


# Create FastAPI app
app = FastAPI(
    title="Scraper Service",
    version="2.0.0",
    description="News scraping service with MongoDB and RabbitMQ integration",
    lifespan=lifespan
)

# Add CORS middleware with specific origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=Config.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router, prefix="/api/v1", tags=["scraper"])

# Health check endpoint
@app.get("/health")
async def health():
    """Simple health check endpoint"""
    return {"status": "healthy", "service": Config.SERVICE_NAME}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level=Config.LOG_LEVEL.lower()
    )
