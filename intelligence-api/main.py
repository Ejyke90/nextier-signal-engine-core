from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Intelligence API Service", version="1.0.0")


class HealthResponse(BaseModel):
    status: str
    service: str


@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Welcome to Intelligence API Service"}


@app.get("/health", response_model=HealthResponse)
async def health():
    """Health check endpoint"""
    return HealthResponse(status="healthy", service="intelligence-api")


@app.get("/analyze")
async def analyze():
    """Analysis endpoint - placeholder for intelligence functionality"""
    return {"message": "Analysis functionality to be implemented"}
