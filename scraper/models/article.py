from datetime import datetime
from typing import Optional, Dict, List, Any
from pydantic import BaseModel, Field, HttpUrl


class Article(BaseModel):
    """Model representing an article scraped for NNVCD with detailed conflict metrics."""
    
    title: str = Field(..., min_length=3, max_length=200)
    content: str = Field(..., min_length=10)
    source: str = Field(..., min_length=3, max_length=50)
    url: HttpUrl
    scraped_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    published_at: Optional[str] = None
    author: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    
    # NNVCD-specific features
    features: Dict[str, Any] = Field(default_factory=lambda: {
        'conflict_type': 'Unknown',  # e.g., Banditry, Gunmen Violence, Terrorism, Farmer-Herder
        'casualties': {
            'fatalities': 0,
            'injured': 0,
            'kidnap_victims': 0,
            'gender_data': {'male': 0, 'female': 0, 'tbd': 0}
        },
        'geography': {
            'state': 'Unknown',
            'lga': 'Unknown',
            'community': 'Unknown'
        },
        'verification_needed': False  # Flag for field monitor verification
    })
    
    # Deduplication and veracity fields
    fingerprint: Optional[str] = None  # SHA-256 hash for deduplication
    veracity_score: float = Field(default_factory=lambda: 0.0)  # Score based on multi-source reporting
    source_count: int = Field(default_factory=lambda: 1)  # Number of sources reporting this incident
    
    @property
    def is_verified(self) -> bool:
        """Check if article should display verified badge (veracity_score > 0.8)"""
        return self.veracity_score > 0.8


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
    published_at: Optional[str] = None
    author: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    features: Dict[str, Any] = Field(default_factory=dict)
    fingerprint: Optional[str] = None
    veracity_score: float = Field(default_factory=lambda: 0.0)
    source_count: int = Field(default_factory=lambda: 1)
    is_verified: bool = Field(default=False)  # True if veracity_score > 0.8


class HealthResponse(BaseModel):
    status: str
    service: str
    checks: Optional[dict] = None
    timestamp: Optional[str] = None


class ScrapeResponse(BaseModel):
    status: str
    articles_scraped: int
    message: str
