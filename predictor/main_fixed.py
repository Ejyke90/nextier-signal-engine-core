import os
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Add parent directory to path for imports
sys.path.insert(0, '/app')

# Import internal modules with absolute imports
from predictor.api import router
from predictor.utils import Config, configure_logging, get_logger
from predictor.services import RiskService, MessageBrokerService, PredictionService
from predictor.repositories import MongoDBRepository

# Configure logging
configure_logging()
logger = get_logger(__name__)

# Initialize configuration
config = Config()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    logger.info("Starting Predictor Service")
    
    # Initialize services
    try:
        # Initialize MongoDB repository
        mongodb_repo = MongoDBRepository()
        app.state.mongodb_repo = mongodb_repo
        
        # Initialize message broker
        message_broker = MessageBrokerService()
        app.state.message_broker = message_broker
        
        # Initialize prediction services
        risk_service = RiskService()
        prediction_service = PredictionService()
        app.state.risk_service = risk_service
        app.state.prediction_service = prediction_service
        
        logger.info("All services initialized successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize services: {e}")
    
    yield
    
    # Cleanup
    logger.info("Shutting down Predictor Service")

# Create FastAPI app
app = FastAPI(
    title="Predictor Service",
    description="Risk prediction and analysis service",
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
    return {"message": "Predictor Service is running", "service": "predictor"}

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "predictor",
        "version": "1.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main_fixed:app", host="0.0.0.0", port=8002, reload=True)
