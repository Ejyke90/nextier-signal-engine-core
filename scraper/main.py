from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Scraper Service", version="1.0.0")


class HealthResponse(BaseModel):
    status: str
    service: str


@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Welcome to Scraper Service"}


@app.get("/health", response_model=HealthResponse)
async def health():
    """Health check endpoint"""
    return HealthResponse(status="healthy", service="scraper")


@app.get("/scrape")
async def scrape():
    """Scrape endpoint - placeholder for scraping functionality"""
    return {"message": "Scraping functionality to be implemented"}
