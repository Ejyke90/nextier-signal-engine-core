from datetime import datetime
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from ..models import (
    HealthResponse, PredictionResponse, RiskSignalsResponse, PredictionStatus, 
    RiskSignalResponse, SimulationParameters, SimulationResponse, GeoJSONFeature
)
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
        
        # Convert to RiskSignalResponse models with default values for missing fields
        signal_models = []
        for signal in signals:
            # Provide defaults for missing fields to handle old signals
            signal_data = {
                "trigger_reason": signal.get("trigger_reason", "Standard risk calculation"),
                "flood_inundation_index": signal.get("flood_inundation_index"),
                "precipitation_anomaly": signal.get("precipitation_anomaly"),
                "vegetation_health_index": signal.get("vegetation_health_index"),
                "mining_proximity_km": signal.get("mining_proximity_km"),
                "mining_site_name": signal.get("mining_site_name"),
                "high_funding_potential": signal.get("high_funding_potential", False),
                "informal_taxation_rate": signal.get("informal_taxation_rate"),
                "border_activity": signal.get("border_activity"),
                "lakurawa_presence": signal.get("lakurawa_presence", False),
                "border_permeability_score": signal.get("border_permeability_score"),
                "group_affiliation": signal.get("group_affiliation"),
                "sophisticated_ied_usage": signal.get("sophisticated_ied_usage", False),
                "climate_vulnerability": signal.get("climate_vulnerability"),
                "mining_density": signal.get("mining_density"),
                "migration_pressure": signal.get("migration_pressure"),
                "poverty_rate": signal.get("poverty_rate"),
                "high_escalation_potential": signal.get("high_escalation_potential", False),
                "is_farmer_herder_conflict": signal.get("is_farmer_herder_conflict", False),
                "surge_detected": signal.get("surge_detected", False),
                "surge_percentage_increase": signal.get("surge_percentage_increase"),
                # Climate-Conflict Correlation Fields
                "climate_zone_region": signal.get("climate_zone_region"),
                "climate_recession_index": signal.get("climate_recession_index"),
                "climate_impact_zone": signal.get("climate_impact_zone"),
                "climate_conflict_correlation": signal.get("climate_conflict_correlation"),
                "conflict_driver": signal.get("conflict_driver"),
                "calculated_at": signal.get("calculated_at", datetime.now().isoformat())
            }
            
            # Merge with original signal data
            signal_data.update(signal)
            
            try:
                signal_models.append(RiskSignalResponse(**signal_data))
            except Exception as model_error:
                logger.warning(f"Skipping invalid signal: {model_error}")
                continue
        
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


@router.post("/simulate", response_model=SimulationResponse)
async def simulate_risk_scenarios(
    params: SimulationParameters,
    mongodb_repo: MongoDBRepository = Depends(get_mongodb_repository),
    risk_service: RiskService = Depends(get_risk_service)
):
    """
    Real-time risk simulation endpoint.
    
    Accepts dynamic slider values and returns fresh GeoJSON with updated risk scores.
    
    Args:
        params: SimulationParameters with fuel_price_index, inflation_rate, chatter_intensity
    
    Returns:
        SimulationResponse with GeoJSON FeatureCollection and metadata
    """
    try:
        logger.info(
            "Starting risk simulation",
            fuel_price_index=params.fuel_price_index,
            inflation_rate=params.inflation_rate,
            chatter_intensity=params.chatter_intensity
        )
        
        # Get parsed events from MongoDB
        events = mongodb_repo.get_parsed_events(limit=1000)
        
        if not events:
            logger.warning("No parsed events found for simulation")
            return SimulationResponse(
                features=[],
                metadata={
                    "total_events": 0,
                    "critical_count": 0,
                    "high_count": 0,
                    "message": "No events available for simulation"
                },
                simulation_params=params
            )
        
        # Get economic data (needed for some calculations, though we override with slider values)
        econ_data = mongodb_repo.get_economic_data()
        
        # Calculate dynamic risk scores for all events
        features = []
        critical_count = 0
        high_count = 0
        medium_count = 0
        low_count = 0
        
        # For categorization simulation
        category_counts = {
            'Banditry': 0,
            'Kidnapping': 0,
            'Gunmen Violence': 0,
            'Farmer-Herder Clashes': 0
        }
        category_confidences = {
            'Banditry': 94,
            'Kidnapping': 87,
            'Gunmen Violence': 91,
            'Farmer-Herder Clashes': 89
        }
        
        for event in events:
            result = risk_service.calculate_risk_score_dynamic(
                event=event,
                econ_data=econ_data,
                fuel_price_index=params.fuel_price_index,
                inflation_rate=params.inflation_rate,
                chatter_intensity=params.chatter_intensity
            )
            
            if result:
                # Count by status
                if result['status'] == 'CRITICAL':
                    critical_count += 1
                    category_counts['Banditry'] += 1
                elif result['status'] == 'HIGH':
                    high_count += 1
                    category_counts['Kidnapping'] += 1
                elif result['status'] == 'MEDIUM':
                    medium_count += 1
                    category_counts['Gunmen Violence'] += 1
                elif result['status'] == 'LOW':
                    low_count += 1
                    category_counts['Farmer-Herder Clashes'] += 1
                
                # Create GeoJSON Feature
                feature = GeoJSONFeature(
                    type="Feature",
                    geometry={
                        "type": "Point",
                        "coordinates": [result['longitude'], result['latitude']]
                    },
                    properties={
                        "risk_score": result['risk_score'],
                        "risk_level": result['risk_level'],
                        "status": result['status'],
                        "event_type": result['event_type'],
                        "state": result['state'],
                        "lga": result['lga'],
                        "severity": result['severity'],
                        "source_title": result['source_title'],
                        "source_url": result['source_url'],
                        "trigger_reason": result['trigger_reason'],
                        "heatmap_weight": result['heatmap_weight'],
                        "heatmap_radius_km": result['heatmap_radius_km'],
                        "is_urban": result['is_urban'],
                        "calculated_at": result['calculated_at']
                    }
                )
                features.append(feature)
        
        # Build simulated categorization
        simulated_categories = []
        for category, count in category_counts.items():
            if count > 0:
                simulated_categories.append({
                    'category': category,
                    'count': count,
                    'confidence': category_confidences[category]
                })
        
        # Sort by count descending
        simulated_categories.sort(key=lambda x: x['count'], reverse=True)
        
        logger.info(
            "Simulation completed",
            total_features=len(features),
            critical=critical_count,
            high=high_count,
            medium=medium_count,
            low=low_count,
            simulated_categories=len(simulated_categories)
        )
        
        # Build metadata
        metadata = {
            "total_events": len(features),
            "critical_count": critical_count,
            "high_count": high_count,
            "medium_count": medium_count,
            "low_count": low_count,
            "simulated_categories": simulated_categories,
            "timestamp": datetime.now().isoformat(),
            "simulation_active": True
        }
        
        return SimulationResponse(
            features=features,
            metadata=metadata,
            simulation_params=params
        )
        
    except Exception as e:
        logger.error("Error in risk simulation", error=str(e))
        raise HTTPException(status_code=500, detail=f"Simulation failed: {str(e)}")


@router.get("/stats/ingestion-volume")
async def get_ingestion_volume(
    mongodb_repo: MongoDBRepository = Depends(get_mongodb_repository)
):
    """Get total count of scraped articles (ingestion volume)"""
    try:
        count = mongodb_repo.get_articles_count()
        return {"ingestion_volume": count}
    except Exception as e:
        logger.error("Error getting ingestion volume", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to get ingestion volume")


@router.get("/stats/intelligence-depth")
async def get_intelligence_depth(
    mongodb_repo: MongoDBRepository = Depends(get_mongodb_repository)
):
    """Get count of unique analyzed events (intelligence depth)"""
    try:
        # Get count of risk signals (which are unique due to upsert)
        count = mongodb_repo.risk_signals_collection.count_documents({})
        return {"intelligence_depth": count}
    except Exception as e:
        logger.error("Error getting intelligence depth", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to get intelligence depth")


@router.get("/categorization-stats")
async def get_categorization_stats(
    mongodb_repo: MongoDBRepository = Depends(get_mongodb_repository)
):
    """Get categorization statistics grouped by conflict type from parsed events"""
    try:
        # Get all parsed events
        events = mongodb_repo.get_parsed_events(limit=10000)  # Large limit to get all
        
        if not events:
            return {"categories": []}
        
        # Group by category
        category_stats = {}
        for event in events:
            category = event.get('category', 'Unknown')
            confidence = event.get('confidence', 0)
            
            if category not in category_stats:
                category_stats[category] = {
                    'count': 0,
                    'total_confidence': 0,
                    'confidence_count': 0
                }
            
            category_stats[category]['count'] += 1
            if confidence > 0:
                category_stats[category]['total_confidence'] += confidence
                category_stats[category]['confidence_count'] += 1
        
        # Calculate average confidence and format response
        categories = []
        for category, stats in category_stats.items():
            avg_confidence = 0
            if stats['confidence_count'] > 0:
                avg_confidence = round(stats['total_confidence'] / stats['confidence_count'], 1)
            
            categories.append({
                'category': category,
                'count': stats['count'],
                'confidence': avg_confidence
            })
        
        # Sort by count descending
        categories.sort(key=lambda x: x['count'], reverse=True)
        
        logger.info(f"Retrieved categorization stats for {len(categories)} categories")
        return {"categories": categories}
        
    except Exception as e:
        logger.error("Error getting categorization stats", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to get categorization stats")


@router.get("/api/v1/stats/categorization-audit")
async def categorization_audit():
    logger.info("Fetching categorization audit stats")
    # Placeholder for actual logic to check uncategorized articles
    return {"remaining_articles": 0, "message": "All articles categorized"}


@router.post("/api/v1/categorize")
async def trigger_categorization():
    logger.info("Triggering categorization process")
    # Placeholder for triggering categorization process
    return {"message": "Categorization process triggered successfully"}


@router.get("/stats/categorization-audit")
async def get_categorization_audit(
    repo: MongoDBRepository = Depends(get_mongodb_repository)
):
    """
    Retrieve statistics about remaining uncategorized articles.
    """
    try:
        total_articles = await repo.get_articles_count()
        categorized_articles = await repo.get_categorized_articles_count()
        remaining_articles = total_articles - categorized_articles
        logger.info(f"Retrieved categorization audit: {remaining_articles} articles remaining")
        return {"remaining_articles": remaining_articles, "total_articles": total_articles, "categorized_articles": categorized_articles}
    except Exception as e:
        logger.error(f"Error fetching categorization audit: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching categorization audit: {str(e)}")


@router.post("/categorize")
async def trigger_categorization(
    repo: MongoDBRepository = Depends(get_mongodb_repository),
    broker: MessageBrokerService = Depends(get_message_broker)
):
    """
    Trigger the categorization process for uncategorized articles.
    """
    try:
        uncategorized_articles = await repo.get_uncategorized_articles()
        if not uncategorized_articles:
            return {"message": "No uncategorized articles found to process"}
        
        for article in uncategorized_articles:
            await broker.publish_event("parsed_events", {
                "id": str(article["_id"]),
                "title": article.get("title", ""),
                "content": article.get("content", ""),
                "source": article.get("source", ""),
                "url": article.get("url", ""),
                "published_date": article.get("published_date", "").isoformat() if article.get("published_date") else None
            })
        
        logger.info(f"Triggered categorization for {len(uncategorized_articles)} articles")
        return {"message": f"Triggered categorization for {len(uncategorized_articles)} articles"}
    except Exception as e:
        logger.error(f"Error triggering categorization: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error triggering categorization: {str(e)}")
