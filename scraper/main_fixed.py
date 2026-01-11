import os
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Add parent directory to path for imports
sys.path.insert(0, '/app')

# Import internal modules with absolute imports
from scraper.api import router
from scraper.utils import Config, configure_logging, get_logger
from scraper.services import ScrapingService, MessageBrokerService, AutomationScheduler
from scraper.repositories import MongoDBRepository

# Configure logging
configure_logging()
logger = get_logger(__name__)

# Initialize configuration
config = Config()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    logger.info("Starting Scraper Service")
    
    # Initialize services
    try:
        # Initialize MongoDB repository
        mongodb_repo = MongoDBRepository()
        app.state.mongodb_repo = mongodb_repo
        
        # Initialize message broker
        message_broker = MessageBrokerService()
        app.state.message_broker = message_broker
        
        # Initialize scraping service
        scraping_service = ScrapingService()
        app.state.scraping_service = scraping_service
        
        # Start automated background scheduler
        automation_scheduler = AutomationScheduler()
        automation_scheduler.start()
        app.state.automation_scheduler = automation_scheduler
        logger.info("🤖 Automated background scheduler started")
        
        logger.info("All services initialized successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize services: {e}")
        raise
    
    yield
    
    # Cleanup
    logger.info("Shutting down Scraper Service")
    try:
        if hasattr(app.state, 'automation_scheduler'):
            app.state.automation_scheduler.stop()
            logger.info("Automation scheduler stopped")
        if hasattr(app.state, 'scraping_service'):
            await app.state.scraping_service.close()
        if hasattr(app.state, 'message_broker'):
            app.state.message_broker.close()
        if hasattr(app.state, 'mongodb_repo'):
            app.state.mongodb_repo.close()
    except Exception as e:
        logger.error(f"Error during cleanup: {e}")

# Create FastAPI app
app = FastAPI(
    title="Scraper Service",
    description="News article scraping and processing service",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router, prefix="/api/v1")

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Scraper Service is running", "service": "scraper"}

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "scraper",
        "version": "1.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main_fixed:app", host="0.0.0.0", port=8000, reload=True)
