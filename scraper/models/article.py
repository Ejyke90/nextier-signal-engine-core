from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, HttpUrl


class Article(BaseModel):
    title: str = Field(..., min_length=3, max_length=200)
    content: str = Field(..., min_length=10)
    source: str = Field(..., min_length=3, max_length=50)
    url: HttpUrl
    scraped_at: str = Field(default_factory=lambda: datetime.now().isoformat())


class ArticleCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=200)
    content: str = Field(..., min_length=10)
    source: str = Field(..., min_length=3, max_length=50)
    url: HttpUrl


class ArticleResponse(BaseModel):
    id: Optional[str] = None
    title: str
    content: str
    source: str
    url: str
    scraped_at: str


class HealthResponse(BaseModel):
    status: str
    service: str
    checks: Optional[dict] = None
    timestamp: Optional[str] = None


class ScrapeResponse(BaseModel):
    status: str
    articles_scraped: int
    message: str
