import asyncio
from datetime import datetime
from typing import Dict, Any, List
from ..utils import get_logger, Config
from ..repositories import MongoDBRepository
from ..services import RiskService, MessageBrokerService

logger = get_logger(__name__)


class PredictionService:
    def __init__(self, mongodb_repo: MongoDBRepository, risk_service: RiskService, message_broker: MessageBrokerService):
        self.mongodb_repo = mongodb_repo
        self.risk_service = risk_service
        self.message_broker = message_broker
        self._running = False
        self._events_buffer = []
    
    async def process_risk_predictions(self) -> Dict[str, Any]:
        """Main processing function - calculate risk scores for events"""
        try:
            logger.info("Starting risk prediction processing")
            
            # Load data
            events = self.mongodb_repo.get_parsed_events()
            econ_data = self.mongodb_repo.get_economic_data()
            
            if not events:
                logger.info("No events to process")
                return {
                    "status": "success",
                    "events_processed": 0,
                    "signals_generated": 0,
                    "message": "No events to process"
                }
            
            if econ_data.empty:
                logger.error("No economic data available")
                return {
                    "status": "error",
                    "events_processed": 0,
                    "signals_generated": 0,
                    "message": "No economic data available"
                }
            
            logger.info("Processing events", count=len(events))
            
            # Calculate risk scores
            risk_signals = self.risk_service.calculate_risk_scores_batch(events, econ_data)
            
            if risk_signals:
                # Convert to dict for MongoDB
                signals_data = [signal.dict() for signal in risk_signals]
                
                # Save to MongoDB
                db_success = self.mongodb_repo.save_risk_signals(signals_data)
                
                # Publish to message broker
                mq_success = self.message_broker.publish_signals(signals_data)
                
                if db_success and mq_success:
                    logger.info("Successfully processed and published risk signals", count=len(risk_signals))
                    return {
                        "status": "success",
                        "events_processed": len(events),
                        "signals_generated": len(risk_signals),
                        "message": f"Successfully processed {len(risk_signals)} risk signals"
                    }
                else:
                    logger.warning("Partial success - some operations failed")
                    return {
                        "status": "partial",
                        "events_processed": len(events),
                        "signals_generated": len(risk_signals),
                        "message": "Risk signals processed but some operations failed"
                    }
            else:
                logger.warning("No risk signals were generated")
                return {
                    "status": "warning",
                    "events_processed": len(events),
                    "signals_generated": 0,
                    "message": "No risk signals were generated"
                }
                
        except Exception as e:
            logger.error("Error in risk prediction processing", error=str(e))
            return {
                "status": "error",
                "events_processed": 0,
                "signals_generated": 0,
                "message": f"Processing failed: {str(e)}"
            }
    
    def process_event_from_queue(self, event: Dict[str, Any]) -> None:
        """Process a single event from message queue"""
        try:
            self._events_buffer.append(event)
            
            # Process buffer when it reaches a certain size or periodically
            if len(self._events_buffer) >= 10:
                asyncio.create_task(self._process_event_buffer())
                
        except Exception as e:
            logger.error("Error processing event from queue", error=str(e))
    
    async def _process_event_buffer(self) -> None:
        """Process buffered events"""
        try:
            if not self._events_buffer:
                return
            
            events_to_process = self._events_buffer.copy()
            self._events_buffer.clear()
            
            econ_data = self.mongodb_repo.get_economic_data()
            
            if econ_data.empty:
                logger.warning("No economic data available for processing")
                return
            
            # Calculate risk scores
            risk_signals = self.risk_service.calculate_risk_scores_batch(events_to_process, econ_data)
            
            if risk_signals:
                signals_data = [signal.dict() for signal in risk_signals]
                
                # Save to MongoDB
                self.mongodb_repo.save_risk_signals(signals_data)
                
                # Publish to message broker
                self.message_broker.publish_signals(signals_data)
                
                logger.info("Processed buffered events", 
                           events=len(events_to_process), 
                           signals=len(risk_signals))
            
        except Exception as e:
            logger.error("Error processing event buffer", error=str(e))
    
    async def start_background_processor(self) -> None:
        """Start background processing loop"""
        self._running = True
        logger.info("Starting background processor")
        
        while self._running:
            try:
                # Process any remaining buffered events
                await self._process_event_buffer()
                
                # Run full prediction cycle
                await self.process_risk_predictions()
                
                await asyncio.sleep(Config.POLL_INTERVAL)
            except Exception as e:
                logger.error("Error in background processor", error=str(e))
                await asyncio.sleep(Config.POLL_INTERVAL)
    
    def stop_background_processor(self) -> None:
        """Stop background processing loop"""
        self._running = False
        logger.info("Stopping background processor")
    
    async def get_prediction_status(self) -> Dict[str, Any]:
        """Get current prediction status"""
        try:
            status = self.mongodb_repo.get_prediction_status()
            status.update({
                "last_calculation": datetime.now().isoformat(),
                "background_processor_running": self._running,
                "buffered_events": len(self._events_buffer)
            })
            return status
        except Exception as e:
            logger.error("Error getting prediction status", error=str(e))
            return {
                "parsed_events_count": 0,
                "risk_signals_count": 0,
                "economic_data_points": 0,
                "last_calculation": datetime.now().isoformat(),
                "background_processor_running": self._running,
                "buffered_events": 0
            }
