from fastapi import FastAPI

app = FastAPI()

@app.get("/health")
async def health():
    """Simple health check endpoint"""
    return {"status": "healthy", "service": "ui"}
