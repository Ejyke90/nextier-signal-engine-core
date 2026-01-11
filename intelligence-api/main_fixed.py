import os
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Add parent directory to path for imports
sys.path.insert(0, '/app')

# Import internal modules with absolute imports
from intelligence_api.api import router
from intelligence_api.utils import Config, configure_logging, get_logger
from intelligence_api.services import LLMService, MessageBrokerService
from intelligence_api.repositories import MongoDBRepository

# Configure logging
configure_logging()
logger = get_logger(__name__)

# Initialize configuration
config = Config()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    logger.info("Starting Intelligence API Service")
    
    # Initialize services
    try:
        # Initialize MongoDB repository
        mongodb_repo = MongoDBRepository()
        app.state.mongodb_repo = mongodb_repo
        
        # Initialize message broker
        message_broker = MessageBrokerService()
        app.state.message_broker = message_broker
        
        # Initialize LLM service
        llm_service = LLMService()
        app.state.llm_service = llm_service
        
        logger.info("All services initialized successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize services: {e}")
    
    yield
    
    # Cleanup
    logger.info("Shutting down Intelligence API Service")

# Create FastAPI app
app = FastAPI(
    title="Intelligence API Service",
    description="AI-powered event extraction and analysis service",
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
    return {"message": "Intelligence API Service is running", "service": "intelligence-api"}

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "intelligence-api",
        "version": "1.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main_fixed:app", host="0.0.0.0", port=8001, reload=True)
