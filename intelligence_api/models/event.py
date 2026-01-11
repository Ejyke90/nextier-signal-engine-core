from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class ParsedEvent(BaseModel):
    event_type: str = Field(..., min_length=1, max_length=50)
    state: str = Field(..., min_length=1, max_length=50)
    lga: str = Field(..., min_length=1, max_length=50)
    severity: str = Field(..., regex=r'^(low|medium|high|critical)$')
    source_title: str = Field(..., min_length=3, max_length=200)
    source_url: str = Field(..., min_length=10)
    parsed_at: str = Field(default_factory=lambda: datetime.now().isoformat())


class EventCreate(BaseModel):
    event_type: str = Field(..., min_length=1, max_length=50)
    state: str = Field(..., min_length=1, max_length=50)
    lga: str = Field(..., min_length=1, max_length=50)
    severity: str = Field(..., regex=r'^(low|medium|high|critical)$')
    source_title: str = Field(..., min_length=3, max_length=200)
    source_url: str = Field(..., min_length=10)


class EventResponse(BaseModel):
    id: Optional[str] = None
    event_type: str
    state: str
    lga: str
    severity: str
    source_title: str
    source_url: str
    parsed_at: str


class HealthResponse(BaseModel):
    status: str
    service: str
    checks: Optional[dict] = None
    timestamp: Optional[str] = None


class AnalysisResponse(BaseModel):
    status: str
    events_processed: int
    message: str


class EventsResponse(BaseModel):
    events: list[EventResponse]
    count: int


class ProcessingStatus(BaseModel):
    raw_articles_count: int
    parsed_events_count: int
    unprocessed_count: int
    last_poll: str
    poll_interval_seconds: int
