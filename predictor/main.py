import os
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from predictor.api import router as api_router
from predictor.api.risk_overview_endpoint import router as risk_overview_router
from predictor.utils import Config, configure_logging, get_logger
from predictor.services import RiskService, MessageBrokerService, PredictionService
from predictor.repositories import MongoDBRepository

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
risk_service = None
message_broker = None
mongodb_repo = None
prediction_service = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle"""
    global risk_service, message_broker, mongodb_repo, prediction_service
    
    logger.info("Starting predictor service")
    
    # Initialize services
    try:
        risk_service = RiskService()
        message_broker = MessageBrokerService()
        mongodb_repo = MongoDBRepository()
        prediction_service = PredictionService(mongodb_repo, risk_service, message_broker)
        
        # Initialize economic data if available
        try:
            mongodb_repo.initialize_economic_data("/data/nigeria_econ.csv")
        except Exception as e:
            logger.warning("Could not initialize economic data from CSV", error=str(e))
        
        # Start background processor
        asyncio.create_task(prediction_service.start_background_processor())
        
        logger.info("Services initialized successfully")
    except Exception as e:
        logger.error("Failed to initialize services", error=str(e))
        raise
    
    yield
    
    # Cleanup
    logger.info("Shutting down predictor service")
    try:
        if prediction_service:
            prediction_service.stop_background_processor()
        if message_broker:
            message_broker.close()
        if mongodb_repo:
            mongodb_repo.close()
        logger.info("Services cleaned up successfully")
    except Exception as e:
        logger.error("Error during cleanup", error=str(e))


# Create FastAPI app
app = FastAPI(
    title="Predictor Service",
    version="2.0.0",
    description="Risk prediction service with economic data analysis, MongoDB, and RabbitMQ integration",
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
app.include_router(api_router, prefix="/api/v1")
app.include_router(risk_overview_router, prefix="/api/v1", tags=["predictor"])

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
        port=8002,
        reload=True,
        log_level=Config.LOG_LEVEL.lower()
    )
