from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import os
import urllib.request
import json

# Static files directory - serve from dist folder
DIST_DIR = "dist"
STATIC_DIR = os.path.join(DIST_DIR, "assets")

class HealthResponse(BaseModel):
    status: str
    service: str

app = FastAPI(title="UI Service", version="1.0.0")

# Mount static directories FIRST, before defining any routes
# This ensures they take precedence over the catch-all route
if os.path.exists(STATIC_DIR):
    app.mount("/assets", StaticFiles(directory=STATIC_DIR), name="assets")

if os.path.exists("/data"):
    app.mount("/data", StaticFiles(directory="/data"), name="data")

@app.get("/health", response_model=HealthResponse)
async def health():
    """Health check endpoint"""
    return HealthResponse(status="healthy", service="ui")

@app.get("/api/v1/risk-overview")
async def proxy_risk_overview():
    """Proxy risk overview requests to predictor service"""
    try:
        with urllib.request.urlopen("http://predictor-service:8002/api/v1/risk-overview", timeout=10) as response:
            if response.status == 200:
                data = json.loads(response.read().decode('utf-8'))
                return data
            else:
                return {"error": f"Predictor service returned {response.status}"}, 502
    except urllib.error.URLError as e:
        return {"error": f"Failed to connect to predictor service: {str(e)}"}, 503
    except Exception as e:
        return {"error": f"Proxy error: {str(e)}"}, 500

@app.get("/api/v1/signals")
async def proxy_signals():
    """Proxy signals requests to predictor service"""
    try:
        with urllib.request.urlopen("http://predictor-service:8002/api/v1/signals", timeout=10) as response:
            if response.status == 200:
                data = json.loads(response.read().decode('utf-8'))
                return data
            else:
                return {"error": f"Predictor service returned {response.status}"}, 502
    except urllib.error.URLError as e:
        return {"error": f"Failed to connect to predictor service: {str(e)}"}, 503
    except Exception as e:
        return {"error": f"Proxy error: {str(e)}"}, 500

@app.get("/{full_path:path}")
async def serve_spa(full_path: str):
    """Serve the React SPA - all routes return index.html for client-side routing"""
    index_path = os.path.join(DIST_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"error": "UI not built. Run 'npm run build' in the ui directory."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
