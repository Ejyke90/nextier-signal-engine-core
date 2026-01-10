import os
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api import router
from .utils import Config, configure_logging, get_logger
from .services import LLMService, MessageBrokerService, ProcessingService
from .repositories import MongoDBRepository

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
llm_service = None
message_broker = None
mongodb_repo = None
processing_service = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle"""
    global llm_service, message_broker, mongodb_repo, processing_service
    
    logger.info("Starting intelligence API service")
    
    # Initialize services
    try:
        llm_service = LLMService()
        message_broker = MessageBrokerService()
        mongodb_repo = MongoDBRepository()
        processing_service = ProcessingService(mongodb_repo, llm_service, message_broker)
        
        # Start background processor
        asyncio.create_task(processing_service.start_background_processor())
        
        logger.info("Services initialized successfully")
    except Exception as e:
        logger.error("Failed to initialize services", error=str(e))
        raise
    
    yield
    
    # Cleanup
    logger.info("Shutting down intelligence API service")
    try:
        if processing_service:
            processing_service.stop_background_processor()
        if llm_service:
            await llm_service.close()
        if message_broker:
            message_broker.close()
        if mongodb_repo:
            mongodb_repo.close()
        logger.info("Services cleaned up successfully")
    except Exception as e:
        logger.error("Error during cleanup", error=str(e))


# Create FastAPI app
app = FastAPI(
    title="Intelligence API Service",
    version="2.0.0",
    description="News intelligence service with LLM processing, MongoDB, and RabbitMQ integration",
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
app.include_router(router, prefix="/api/v1", tags=["intelligence"])

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
        port=8001,
        reload=True,
        log_level=Config.LOG_LEVEL.lower()
    )
