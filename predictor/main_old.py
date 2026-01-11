import json
import os
import logging
import pandas as pd
import numpy as np
from datetime import datetime
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="Predictor Service", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
DATA_DIR = "/data"
PARSED_EVENTS_FILE = os.path.join(DATA_DIR, "parsed_events.json")
ECON_DATA_FILE = os.path.join(DATA_DIR, "nigeria_econ.csv")
RISK_SIGNALS_FILE = os.path.join(DATA_DIR, "risk_signals.json")


class RiskSignal(BaseModel):
    event_type: str
    state: str
    lga: str
    severity: str
    fuel_price: float
    inflation: float
    risk_score: float
    risk_level: str
    source_title: str
    source_url: str
    calculated_at: str


class HealthResponse(BaseModel):
    status: str
    service: str


class PredictionResponse(BaseModel):
    status: str
    signals_generated: int
    message: str


class RiskSignalsResponse(BaseModel):
    signals: List[RiskSignal]
    count: int


def ensure_data_directory():
    """Ensure the data directory exists"""
    os.makedirs(DATA_DIR, exist_ok=True)


def load_economic_data() -> pd.DataFrame:
    """Load economic data from CSV file"""
    try:
        if not os.path.exists(ECON_DATA_FILE):
            logger.error(f"Economic data file not found: {ECON_DATA_FILE}")
            return pd.DataFrame()
        
        df = pd.read_csv(ECON_DATA_FILE)
        logger.info(f"Loaded economic data for {len(df)} state-LGA combinations")
        return df
        
    except Exception as e:
        logger.error(f"Error loading economic data: {str(e)}")
        return pd.DataFrame()


def load_parsed_events() -> List[Dict[str, Any]]:
    """Load parsed events from JSON file"""
    try:
        if not os.path.exists(PARSED_EVENTS_FILE):
            logger.info("No parsed events file found")
            return []
        
        with open(PARSED_EVENTS_FILE, 'r', encoding='utf-8') as f:
            events = json.load(f)
        
        logger.info(f"Loaded {len(events)} parsed events")
        return events
        
    except json.JSONDecodeError as e:
        logger.error(f"Error parsing parsed events JSON: {str(e)}")
        return []
    except Exception as e:
        logger.error(f"Error loading parsed events: {str(e)}")
        return []


def calculate_risk_score(event: Dict[str, Any], econ_data: pd.DataFrame) -> Optional[Dict[str, Any]]:
    """
    Calculate risk score based on event type and economic indicators
    Risk scoring algorithm:
    - Base score depends on event type and severity
    - Economic modifiers: inflation > 20% increases risk
    - Special rule: clash events with inflation > 20% get > 80 risk score
    """
    try:
        event_type = event.get('event_type', '').lower()
        state = event.get('state', '').strip()
        lga = event.get('lga', '').strip()
        severity = event.get('severity', '').lower()
        
        # Find matching economic data
        econ_row = econ_data[
            (econ_data['State'].str.lower() == state.lower()) &
            (econ_data['LGA'].str.lower() == lga.lower())
        ]
        
        if econ_row.empty:
            # Try state-level match if LGA not found
            econ_row = econ_data[econ_data['State'].str.lower() == state.lower()]
        
        if econ_row.empty:
            logger.warning(f"No economic data found for {state}, {lga}")
            return None
        
        econ_data_row = econ_row.iloc[0]
        fuel_price = float(econ_data_row['Fuel_Price'])
        inflation = float(econ_data_row['Inflation'])
        
        # Base risk score calculation
        base_score = 30  # Default base score
        
        # Event type modifiers
        event_type_scores = {
            'clash': 40,
            'conflict': 35,
            'violence': 30,
            'protest': 25,
            'political': 20,
            'security': 25,
            'crime': 20,
            'sports': 5,  # Low risk
            'economic': 15,
            'social': 10,
            'unknown': 15
        }
        
        base_score += event_type_scores.get(event_type, 15)
        
        # Severity modifiers
        severity_modifiers = {
            'high': 20,
            'severe': 25,
            'critical': 30,
            'medium': 10,
            'moderate': 8,
            'low': 5,
            'minor': 3,
            'unknown': 5
        }
        
        base_score += severity_modifiers.get(severity, 5)
        
        # Economic modifiers
        if inflation > 20:
            inflation_bonus = min((inflation - 20) * 2, 20)  # Up to 20 points
            base_score += inflation_bonus
        
        if fuel_price > 650:
            fuel_bonus = min((fuel_price - 650) * 0.1, 10)  # Up to 10 points
            base_score += fuel_bonus
        
        # Special rule: clash events with inflation > 20% get > 80 risk score
        if event_type == 'clash' and inflation > 20:
            base_score = max(base_score, 81)
        
        # Ensure score is within bounds
        risk_score = max(0, min(100, base_score))
        
        # Determine risk level
        if risk_score >= 80:
            risk_level = "Critical"
        elif risk_score >= 60:
            risk_level = "High"
        elif risk_score >= 40:
            risk_level = "Medium"
        elif risk_score >= 20:
            risk_level = "Low"
        else:
            risk_level = "Minimal"
        
        return {
            "event_type": event.get('event_type', 'unknown'),
            "state": state,
            "lga": lga,
            "severity": event.get('severity', 'unknown'),
            "fuel_price": fuel_price,
            "inflation": inflation,
            "risk_score": round(risk_score, 1),
            "risk_level": risk_level,
            "source_title": event.get('source_title', ''),
            "source_url": event.get('source_url', ''),
            "calculated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error calculating risk score: {str(e)}")
        return None


def save_risk_signals(signals: List[Dict[str, Any]]) -> bool:
    """Save risk signals to JSON file"""
    try:
        ensure_data_directory()
        
        with open(RISK_SIGNALS_FILE, 'w', encoding='utf-8') as f:
            json.dump(signals, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Saved {len(signals)} risk signals to {RISK_SIGNALS_FILE}")
        return True
        
    except Exception as e:
        logger.error(f"Error saving risk signals: {str(e)}")
        return False


async def process_risk_predictions():
    """Main processing function - calculate risk scores for events"""
    try:
        logger.info("Starting risk prediction processing")
        
        # Load data
        events = load_parsed_events()
        econ_data = load_economic_data()
        
        if not events:
            logger.info("No events to process")
            return
        
        if econ_data.empty:
            logger.error("No economic data available")
            return
        
        logger.info(f"Processing {len(events)} events with economic data")
        
        # Calculate risk scores
        risk_signals = []
        for event in events:
            try:
                signal = calculate_risk_score(event, econ_data)
                if signal:
                    risk_signals.append(signal)
                    logger.info(f"Calculated risk score {signal['risk_score']} for {signal['event_type']} in {signal['state']}")
                else:
                    logger.warning(f"Failed to calculate risk score for event: {event.get('source_title', 'Unknown')}")
                    
            except Exception as e:
                logger.error(f"Error processing event {event.get('source_url', 'unknown')}: {str(e)}")
                continue
        
        if risk_signals:
            # Save risk signals
            success = save_risk_signals(risk_signals)
            
            if success:
                logger.info(f"Successfully processed and saved {len(risk_signals)} risk signals")
            else:
                logger.error("Failed to save risk signals")
        else:
            logger.info("No risk signals were generated")
            
    except Exception as e:
        logger.error(f"Error in risk prediction processing: {str(e)}")


@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Welcome to Predictor Service"}


@app.get("/health", response_model=HealthResponse)
async def health():
    """Health check endpoint"""
    return HealthResponse(status="healthy", service="predictor")


@app.get("/predict", response_model=PredictionResponse)
async def predict_risks(background_tasks: BackgroundTasks):
    """Trigger risk prediction analysis"""
    try:
        # Run processing in background
        background_tasks.add_task(process_risk_predictions)
        
        return PredictionResponse(
            status="processing",
            signals_generated=0,
            message="Risk prediction started in background"
        )
        
    except Exception as e:
        logger.error(f"Error triggering prediction: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


@app.get("/signals", response_model=RiskSignalsResponse)
async def get_risk_signals():
    """Get all risk signals"""
    try:
        if not os.path.exists(RISK_SIGNALS_FILE):
            return RiskSignalsResponse(signals=[], count=0)
        
        with open(RISK_SIGNALS_FILE, 'r', encoding='utf-8') as f:
            signals = json.load(f)
        
        # Convert to RiskSignal models
        signal_models = [RiskSignal(**signal) for signal in signals]
        
        return RiskSignalsResponse(signals=signal_models, count=len(signal_models))
        
    except Exception as e:
        logger.error(f"Error getting risk signals: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve risk signals")


@app.get("/status")
async def get_status():
    """Get processing status"""
    try:
        events = load_parsed_events()
        
        signals_count = 0
        if os.path.exists(RISK_SIGNALS_FILE):
            with open(RISK_SIGNALS_FILE, 'r', encoding='utf-8') as f:
                signals = json.load(f)
                signals_count = len(signals)
        
        econ_data = load_economic_data()
        
        return {
            "parsed_events_count": len(events),
            "risk_signals_count": signals_count,
            "economic_data_points": len(econ_data),
            "last_calculation": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get status")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
