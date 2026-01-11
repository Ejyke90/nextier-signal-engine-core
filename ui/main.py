from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import os

app = FastAPI(title="UI Service", version="1.0.0")

# Static files directory
STATIC_DIR = "."

class HealthResponse(BaseModel):
    status: str
    service: str

@app.get("/")
async def root():
    """Serve the main UI"""
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))

@app.get("/health", response_model=HealthResponse)
async def health():
    """Health check endpoint"""
    return HealthResponse(status="healthy", service="ui")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
