from datetime import datetime
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from ..models import HealthResponse, AnalysisResponse, EventsResponse, ProcessingStatus, EventResponse, CategorizationStatsResponse, CategorizationAuditResponse
from ..services import LLMService, MessageBrokerService, ProcessingService, LLMProcessor, CategorizationService
from ..repositories import MongoDBRepository
from ..utils import get_logger, Config

logger = get_logger(__name__)
router = APIRouter()

# Global service instances
processing_service = None
categorization_service = None


def get_llm_processor() -> LLMProcessor:
    """Dependency injection for LLM processor"""
    return LLMProcessor()


def get_categorization_service(
    mongodb_repo: MongoDBRepository = Depends(get_mongodb_repository),
    llm_processor: LLMProcessor = Depends(get_llm_processor)
) -> CategorizationService:
    """Dependency injection for categorization service"""
    global categorization_service
    if categorization_service is None:
        categorization_service = CategorizationService(mongodb_repo, llm_processor)
    return categorization_service


def get_llm_service() -> LLMService:
    """Dependency injection for LLM service"""
    return LLMService()


def get_message_broker() -> MessageBrokerService:
    """Dependency injection for message broker"""
    return MessageBrokerService()


def get_mongodb_repository() -> MongoDBRepository:
    """Dependency injection for MongoDB repository"""
    return MongoDBRepository()


def get_processing_service(
    mongodb_repo: MongoDBRepository = Depends(get_mongodb_repository),
    llm_service: LLMService = Depends(get_llm_service),
    message_broker: MessageBrokerService = Depends(get_message_broker)
) -> ProcessingService:
    """Dependency injection for processing service"""
    global processing_service
    if processing_service is None:
        processing_service = ProcessingService(mongodb_repo, llm_service, message_broker)
    return processing_service


@router.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Welcome to Intelligence API Service"}


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


@router.get("/analyze", response_model=AnalysisResponse)
async def analyze_news(
    background_tasks: BackgroundTasks,
    processing_service: ProcessingService = Depends(get_processing_service)
):
    """Trigger immediate analysis of news articles"""
    try:
        # Run processing in background
        background_tasks.add_task(processing_service.process_news_articles)
        
        return AnalysisResponse(
            status="processing",
            events_processed=0,
            message="News analysis started in background"
        )
        
    except Exception as e:
        logger.error("Error triggering analysis", error=str(e))
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_news_sync(
    processing_service: ProcessingService = Depends(get_processing_service)
):
    """Synchronous analysis of news articles"""
    try:
        result = await processing_service.process_news_articles()
        
        return AnalysisResponse(
            status=result["status"],
            events_processed=result["events_created"],
            message=result["message"]
        )
        
    except Exception as e:
        logger.error("Error in synchronous analysis", error=str(e))
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.get("/events", response_model=EventsResponse)
async def get_events(
    limit: int = 100,
    mongodb_repo: MongoDBRepository = Depends(get_mongodb_repository)
):
    """Get all parsed events"""
    try:
        events = mongodb_repo.get_parsed_events(limit)
        
        # Convert to EventResponse models
        event_models = [EventResponse(**event) for event in events]
        
        return EventsResponse(events=event_models, count=len(event_models))
        
    except Exception as e:
        logger.error("Error getting events", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to retrieve events")


@router.get("/status", response_model=ProcessingStatus)
async def get_status(
    processing_service: ProcessingService = Depends(get_processing_service)
):
    """Get processing status"""
    try:
        status = await processing_service.get_processing_status()
        return ProcessingStatus(**status)
        
    except Exception as e:
        logger.error("Error getting status", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to get status")


@router.post("/start-processor")
async def start_background_processor(
    processing_service: ProcessingService = Depends(get_processing_service)
):
    """Start background processor"""
    try:
        # Start background processor in a task
        import asyncio
        asyncio.create_task(processing_service.start_background_processor())
        
        return {
            "status": "started",
            "message": "Background processor started",
            "poll_interval": Config.POLL_INTERVAL
        }
        
    except Exception as e:
        logger.error("Error starting background processor", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to start background processor")


@router.post("/stop-processor")
async def stop_background_processor(
    processing_service: ProcessingService = Depends(get_processing_service)
):
    """Stop background processor"""
    try:
        processing_service.stop_background_processor()
        
        return {
            "status": "stopped",
            "message": "Background processor stopped"
        }
        
    except Exception as e:
        logger.error("Error stopping background processor", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to stop background processor")


@router.get("/stats/categorization-audit", response_model=CategorizationAuditResponse)
async def get_categorization_audit_stats(
    mongodb_repo: MongoDBRepository = Depends(get_mongodb_repository)
):
    """Get categorization audit statistics for documented proof report"""
    try:
        audit_data = mongodb_repo.get_categorization_audit()
        return CategorizationAuditResponse(**audit_data)
        
    except Exception as e:
        logger.error("Error getting categorization audit stats", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to get categorization audit stats")


@router.post("/categorize", response_model=AnalysisResponse)
async def trigger_categorization(
    background_tasks: BackgroundTasks,
    categorization_service: CategorizationService = Depends(get_categorization_service)
):
    """Trigger immediate categorization of uncategorized articles"""
    try:
        background_tasks.add_task(categorization_service.categorize_articles)
        
        return AnalysisResponse(
            status="processing",
            events_processed=0,
            message="Categorization processing started in background"
        )
        
    except Exception as e:
        logger.error("Error triggering categorization", error=str(e))
        raise HTTPException(status_code=500, detail=f"Categorization trigger failed: {str(e)}")
