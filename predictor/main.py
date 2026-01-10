from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Predictor Service", version="1.0.0")


class HealthResponse(BaseModel):
    status: str
    service: str


@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Welcome to Predictor Service"}


@app.get("/health", response_model=HealthResponse)
async def health():
    """Health check endpoint"""
    return HealthResponse(status="healthy", service="predictor")


@app.get("/predict")
async def predict():
    """Prediction endpoint - placeholder for prediction functionality"""
    return {"message": "Prediction functionality to be implemented"}
