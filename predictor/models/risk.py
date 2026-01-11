from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class RiskSignal(BaseModel):
    event_type: str = Field(..., min_length=1, max_length=50)
    state: str = Field(..., min_length=1, max_length=50)
    lga: str = Field(..., min_length=1, max_length=50)
    severity: str = Field(..., pattern=r'^(low|medium|high|critical)$')
    fuel_price: float = Field(..., ge=0)
    inflation: float = Field(..., ge=0)
    risk_score: float = Field(..., ge=0, le=100)
    risk_level: str = Field(..., pattern=r'^(Minimal|Low|Medium|High|Critical)$')
    source_title: str = Field(..., min_length=3, max_length=200)
    source_url: str = Field(..., min_length=10)
    trigger_reason: str = Field(default="Standard risk calculation")
    
    # Climate indicators
    flood_inundation_index: Optional[float] = Field(default=None, ge=0, le=100)
    precipitation_anomaly: Optional[float] = Field(default=None)
    vegetation_health_index: Optional[float] = Field(default=None, ge=0, le=1)
    
    # Mining/Economic indicators
    mining_proximity_km: Optional[float] = Field(default=None, ge=0)
    mining_site_name: Optional[str] = Field(default=None)
    high_funding_potential: bool = Field(default=False)
    informal_taxation_rate: Optional[float] = Field(default=None, ge=0, le=1)
    
    # Border/Transnational indicators
    border_activity: Optional[str] = Field(default=None)
    lakurawa_presence: bool = Field(default=False)
    border_permeability_score: Optional[float] = Field(default=None, ge=0, le=1)
    group_affiliation: Optional[str] = Field(default=None)
    sophisticated_ied_usage: bool = Field(default=False)
    
    calculated_at: str = Field(default_factory=lambda: datetime.now().isoformat())


class RiskSignalCreate(BaseModel):
    event_type: str = Field(..., min_length=1, max_length=50)
    state: str = Field(..., min_length=1, max_length=50)
    lga: str = Field(..., min_length=1, max_length=50)
    severity: str = Field(..., pattern=r'^(low|medium|high|critical)$')
    fuel_price: float = Field(..., ge=0)
    inflation: float = Field(..., ge=0)
    risk_score: float = Field(..., ge=0, le=100)
    risk_level: str = Field(..., pattern=r'^(Minimal|Low|Medium|High|Critical)$')
    source_title: str = Field(..., min_length=3, max_length=200)
    source_url: str = Field(..., min_length=10)


class RiskSignalResponse(BaseModel):
    id: Optional[str] = None
    event_type: str
    state: str
    lga: str
    severity: str
    fuel_price: float
    inflation: float
    risk_score: float
    risk_level: str
    source_title: str
    source_url: str
    trigger_reason: str
    
    # Climate indicators
    flood_inundation_index: Optional[float] = None
    precipitation_anomaly: Optional[float] = None
    vegetation_health_index: Optional[float] = None
    
    # Mining/Economic indicators
    mining_proximity_km: Optional[float] = None
    mining_site_name: Optional[str] = None
    high_funding_potential: bool = False
    informal_taxation_rate: Optional[float] = None
    
    # Border/Transnational indicators
    border_activity: Optional[str] = None
    lakurawa_presence: bool = False
    border_permeability_score: Optional[float] = None
    group_affiliation: Optional[str] = None
    sophisticated_ied_usage: bool = False
    
    calculated_at: str


class HealthResponse(BaseModel):
    status: str
    service: str
    checks: Optional[dict] = None
    timestamp: Optional[str] = None


class PredictionResponse(BaseModel):
    status: str
    signals_generated: int
    message: str


class RiskSignalsResponse(BaseModel):
    signals: list[RiskSignalResponse]
    count: int


class PredictionStatus(BaseModel):
    parsed_events_count: int
    risk_signals_count: int
    economic_data_points: int
    last_calculation: str
    background_processor_running: bool


class SimulationParameters(BaseModel):
    """Dynamic simulation parameters from UI sliders"""
    fuel_price_index: float = Field(..., ge=0, le=100, description="Fuel price crisis index (0-100)")
    inflation_rate: float = Field(..., ge=0, le=100, description="Inflation rate percentage (0-100)")
    chatter_intensity: float = Field(..., ge=0, le=100, description="Social media chatter intensity (0-100)")


class GeoJSONFeature(BaseModel):
    """GeoJSON Feature for heatmap visualization"""
    type: str = Field(default="Feature")
    geometry: dict
    properties: dict


class SimulationResponse(BaseModel):
    """Response for simulation endpoint with GeoJSON and metadata"""
    type: str = Field(default="FeatureCollection")
    features: List[GeoJSONFeature]
    metadata: dict = Field(default_factory=dict)
    simulation_params: SimulationParameters
