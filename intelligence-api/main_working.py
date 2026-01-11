import sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Add parent directory to path for imports
sys.path.insert(0, '/app')

app = FastAPI(
    title="Intelligence API Service",
    description="AI-powered event extraction and analysis service",
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
    return {"message": "Intelligence API Service is running", "service": "intelligence-api"}

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "intelligence-api", "version": "1.0.0"}

@app.get("/api/v1/status")
async def get_status():
    return {"parsed_events_count": 5, "status": "active"}

@app.post("/api/v1/analyze")
async def analyze():
    return {"message": "Analysis started", "status": "processing"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main_working:app", host="0.0.0.0", port=8001, reload=True)
