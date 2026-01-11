import sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Add parent directory to path for imports
sys.path.insert(0, '/app')

app = FastAPI(
    title="Predictor Service",
    description="Risk prediction and analysis service",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Predictor Service is running", "service": "predictor"}

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "predictor", "version": "1.0.0"}

@app.get("/api/v1/status")
async def get_status():
    return {"risk_signals_count": 7, "status": "active"}

@app.get("/api/v1/signals")
async def get_signals():
    return {
        "signals": [
            {
                "event_type": "attack",
                "state": "Borno",
                "lga": "Gwoza",
                "severity": "high",
                "risk_score": 85,
                "risk_level": "Critical",
                "fuel_price": 700,
                "inflation": 25.8,
                "calculated_at": "2026-01-11T01:00:00Z"
            },
            {
                "event_type": "clash",
                "state": "Benue",
                "lga": "Guma",
                "severity": "critical",
                "risk_score": 90,
                "risk_level": "Critical",
                "fuel_price": 680,
                "inflation": 26.2,
                "calculated_at": "2026-01-11T01:00:00Z"
            },
            {
                "event_type": "kidnapping",
                "state": "Kaduna",
                "lga": "Chikun",
                "severity": "high",
                "risk_score": 75,
                "risk_level": "High",
                "fuel_price": 670,
                "inflation": 24.7,
                "calculated_at": "2026-01-11T01:00:00Z"
            },
            {
                "event_type": "protest",
                "state": "Lagos",
                "lga": "Ikeja",
                "severity": "medium",
                "risk_score": 65,
                "risk_level": "High",
                "fuel_price": 650,
                "inflation": 22.5,
                "calculated_at": "2026-01-11T01:00:00Z"
            },
            {
                "event_type": "vandalism",
                "state": "Rivers",
                "lga": "Khana",
                "severity": "medium",
                "risk_score": 55,
                "risk_level": "Medium",
                "fuel_price": 660,
                "inflation": 23.9,
                "calculated_at": "2026-01-11T01:00:00Z"
            }
        ]
    }

@app.post("/api/v1/predict")
async def predict():
    return {"message": "Risk calculation started", "status": "processing"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main_working:app", host="0.0.0.0", port=8002, reload=True)

@app.post("/api/v1/stress-test")
async def stress_test(data: dict):
    """Apply economic stress test with custom parameters"""
    fuel_price = data.get('fuel_price', 650)
    inflation_rate = data.get('inflation_rate', 25)
    
    # Simulate stress test impact on risk calculations
    stress_multiplier = 1.0
    if fuel_price > 800:
        stress_multiplier += 0.3
    if inflation_rate > 30:
        stress_multiplier += 0.4
    
    return {
        "message": "Stress test applied successfully",
        "parameters": {
            "fuel_price": fuel_price,
            "inflation_rate": inflation_rate,
            "stress_multiplier": stress_multiplier
        },
        "status": "applied"
    }
