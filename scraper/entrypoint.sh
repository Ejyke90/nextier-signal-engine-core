#!/bin/bash
set -e

echo "Starting Scraper Service..."

# Set Python path to include the project root
export PYTHONPATH="/app:$PYTHONPATH"

# Change to scraper directory
cd /app/scraper

# Create __init__.py files if they don't exist
touch __init__.py
touch api/__init__.py
touch models/__init__.py
touch services/__init__.py
touch repositories/__init__.py
touch utils/__init__.py

# Create a temporary main_fixed.py with corrected imports
cat > main_fixed.py << 'EOF'
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
from scraper.services import ScrapingService, MessageBrokerService
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
        scraping_service = ScrapingService(mongodb_repo, message_broker)
        app.state.scraping_service = scraping_service
        
        logger.info("All services initialized successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize services: {e}")
    
    yield
    
    # Cleanup
    logger.info("Shutting down Scraper Service")

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
EOF

echo "Starting FastAPI application with fixed imports..."
exec uvicorn main_fixed:app --host 0.0.0.0 --port 8000 --reload
