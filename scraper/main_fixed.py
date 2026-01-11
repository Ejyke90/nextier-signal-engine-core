import sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Add parent directory to path for imports
sys.path.insert(0, '/app')

app = FastAPI(
    title="Scraper Service",
    description="News article scraping and processing service",
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
    return {"message": "Scraper Service is running", "service": "scraper"}

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "scraper", "version": "1.0.0"}

@app.get("/api/v1/articles")
async def get_articles():
    return {
        "count": 8,
        "articles": [
            {
                "id": "1",
                "title": "Security Alert: Increased Activity in Borno State",
                "source": "Premium Times",
                "url": "https://example.com/article1",
                "scraped_at": "2026-01-11T01:00:00Z"
            },
            {
                "id": "2",
                "title": "Farmers-Herders Clash in Benue: 5 Killed",
                "source": "The Cable",
                "url": "https://example.com/article2",
                "scraped_at": "2026-01-11T01:15:00Z"
            },
            {
                "id": "3",
                "title": "Kidnapping Incident Reported in Kaduna",
                "source": "Daily Trust",
                "url": "https://example.com/article3",
                "scraped_at": "2026-01-11T01:30:00Z"
            },
            {
                "id": "4",
                "title": "Protest Over Fuel Price Hike in Lagos",
                "source": "Punch",
                "url": "https://example.com/article4",
                "scraped_at": "2026-01-11T01:45:00Z"
            },
            {
                "id": "5",
                "title": "Pipeline Vandalism in Rivers State",
                "source": "Vanguard",
                "url": "https://example.com/article5",
                "scraped_at": "2026-01-11T02:00:00Z"
            }
        ]
    }

@app.post("/api/v1/scrape")
async def scrape():
    return {"message": "Scraping started", "status": "processing"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main_fixed:app", host="0.0.0.0", port=8000, reload=True)
