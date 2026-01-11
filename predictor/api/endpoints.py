from datetime import datetime
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from ..models import HealthResponse, PredictionResponse, RiskSignalsResponse, PredictionStatus, RiskSignalResponse
from ..services import RiskService, MessageBrokerService, PredictionService
from ..repositories import MongoDBRepository
from ..utils import get_logger, Config

logger = get_logger(__name__)
router = APIRouter()

# Global prediction service instance
prediction_service = None


def get_risk_service() -> RiskService:
    """Dependency injection for risk service"""
    return RiskService()


def get_message_broker() -> MessageBrokerService:
    """Dependency injection for message broker"""
    return MessageBrokerService()


def get_mongodb_repository() -> MongoDBRepository:
    """Dependency injection for MongoDB repository"""
    return MongoDBRepository()


def get_prediction_service(
    mongodb_repo: MongoDBRepository = Depends(get_mongodb_repository),
    risk_service: RiskService = Depends(get_risk_service),
    message_broker: MessageBrokerService = Depends(get_message_broker)
) -> PredictionService:
    """Dependency injection for prediction service"""
    global prediction_service
    if prediction_service is None:
        prediction_service = PredictionService(mongodb_repo, risk_service, message_broker)
    return prediction_service


@router.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Welcome to Predictor Service"}


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
    
    # Check economic data availability
    try:
        econ_data = mongodb_repo.get_economic_data()
        checks["economic_data"] = "available" if not econ_data.empty else "unavailable"
        if econ_data.empty:
            status = "degraded"
    except Exception as e:
        status = "degraded"
        checks["economic_data"] = str(e)
    
    return HealthResponse(
        status=status,
        service=Config.SERVICE_NAME,
        checks=checks,
        timestamp=datetime.now().isoformat()
    )


@router.get("/predict", response_model=PredictionResponse)
async def predict_risks(
    background_tasks: BackgroundTasks,
    prediction_service: PredictionService = Depends(get_prediction_service)
):
    """Trigger risk prediction analysis"""
    try:
        # Run processing in background
        background_tasks.add_task(prediction_service.process_risk_predictions)
        
        return PredictionResponse(
            status="processing",
            signals_generated=0,
            message="Risk prediction started in background"
        )
        
    except Exception as e:
        logger.error("Error triggering prediction", error=str(e))
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


@router.post("/predict", response_model=PredictionResponse)
async def predict_risks_sync(
    prediction_service: PredictionService = Depends(get_prediction_service)
):
    """Synchronous risk prediction analysis"""
    try:
        result = await prediction_service.process_risk_predictions()
        
        return PredictionResponse(
            status=result["status"],
            signals_generated=result["signals_generated"],
            message=result["message"]
        )
        
    except Exception as e:
        logger.error("Error in synchronous prediction", error=str(e))
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


@router.get("/signals", response_model=RiskSignalsResponse)
async def get_risk_signals(
    limit: int = 100,
    mongodb_repo: MongoDBRepository = Depends(get_mongodb_repository)
):
    """Get all risk signals"""
    try:
        signals = mongodb_repo.get_risk_signals(limit)
        
        # Convert to RiskSignalResponse models
        signal_models = [RiskSignalResponse(**signal) for signal in signals]
        
        return RiskSignalsResponse(signals=signal_models, count=len(signal_models))
        
    except Exception as e:
        logger.error("Error getting risk signals", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to retrieve risk signals")


@router.get("/status", response_model=PredictionStatus)
async def get_status(
    prediction_service: PredictionService = Depends(get_prediction_service)
):
    """Get prediction status"""
    try:
        status = await prediction_service.get_prediction_status()
        return PredictionStatus(**status)
        
    except Exception as e:
        logger.error("Error getting status", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to get status")


@router.post("/start-processor")
async def start_background_processor(
    prediction_service: PredictionService = Depends(get_prediction_service)
):
    """Start background processor"""
    try:
        # Start background processor in a task
        import asyncio
        asyncio.create_task(prediction_service.start_background_processor())
        
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
    prediction_service: PredictionService = Depends(get_prediction_service)
):
    """Stop background processor"""
    try:
        prediction_service.stop_background_processor()
        
        return {
            "status": "stopped",
            "message": "Background processor stopped"
        }
        
    except Exception as e:
        logger.error("Error stopping background processor", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to stop background processor")


@router.post("/initialize-economic-data")
async def initialize_economic_data(
    csv_file_path: str = "/data/nigeria_econ.csv",
    mongodb_repo: MongoDBRepository = Depends(get_mongodb_repository)
):
    """Initialize economic data from CSV file"""
    try:
        success = mongodb_repo.initialize_economic_data(csv_file_path)
        
        if success:
            return {
                "status": "success",
                "message": "Economic data initialized successfully"
            }
        else:
            return {
                "status": "error",
                "message": "Failed to initialize economic data"
            }
        
    except Exception as e:
        logger.error("Error initializing economic data", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to initialize economic data")
