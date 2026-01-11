# Climate-Conflict Correlation & Intervention UI Implementation

## Overview
This implementation integrates climate stress indicators with conflict prediction to identify environmental drivers of violence and trigger policy interventions.

## Components Implemented

### 1. Backend: Predictor Service (`predictor/services/risk_service.py`)

#### Data Ingestion
- **`_load_climate_indicators_geojson()`**: Loads `data/climate_indicators.geojson` containing climate stress zones
- Initializes on service startup in `RiskService.__init__()`
- Handles Lake Chad Basin and Hadejia-Nguru Wetlands data

#### Risk Algorithm
- **`calculate_climate_risk(event)`**: Core function that:
  - Uses `_point_in_polygon()` ray-casting algorithm to check if event coordinates fall within climate stress zones
  - Returns climate zone metadata including:
    - `region`: Geographic area (e.g., "Lake Chad Basin")
    - `recession_index`: Water scarcity metric (0.0-1.0)
    - `impact_zone`: Severity level ("High", "Medium-High", "Medium")
    - `conflict_correlation`: Conflict driver description
    - `is_high_impact`: Boolean flag for High impact zones

#### Risk Score Integration
- Integrated into `calculate_risk_score()` function:
  - **High Impact Zones** (recession_index > 0.8): +25 points to risk score
  - **Medium-High/Medium Zones**: +15 points to risk score
  - Sets `conflict_driver = 'Environmental/Climate'` for events in climate zones
  - Adds detailed trigger reasons explaining climate-conflict correlation

### 2. Frontend: React Dashboard

#### ClimateStressLayer Component (`ui/src/components/ClimateStressLayer.jsx`)
- **Visual Design**: Brown-to-orange gradient representing desertification/water scarcity
  - High impact: `#D2691E` (chocolate) with 40-70% opacity
  - Medium-High: `#CD853F` (peru) with 30-50% opacity
  - Medium: `#DEB887` (burlywood) with 20-35% opacity
- **Styling**: Dashed borders (`dashArray: '5, 5'`) to distinguish from mining zones
- **Interactive Popups**: Display on hover:
  - Region name and climate indicator
  - Recession index percentage
  - Impact zone severity
  - Conflict correlation explanation
- **Integration**: Leaflet GeoJSON layer that loads from `/data/climate_indicators.geojson`

#### PolicymakerAlert Component (`ui/src/components/PolicymakerAlert.jsx`)
- **Alert Criteria**:
  - **CRITICAL**: `risk_score > 80 AND recession_index > 0.8 AND is_farmer_herder_conflict`
  - **HIGH**: `risk_score > 80 AND climate_impact_zone === 'High'`
- **Alert Message**: 
  - Critical: "INTERVENTION RECOMMENDED: Resource mediation required to prevent Farmer-Herder escalation"
  - High: "Climate adaptation and resource management intervention needed"
- **Visual Design**:
  - Critical alerts: Red background with pulse animation
  - High alerts: Orange background
  - Icons: AlertTriangle for interventions, Droplets for climate conflicts
- **Display Information**:
  - Location (state/LGA)
  - Risk score and event details
  - Climate zone and recession index
  - Recommended action
  - Full trigger reason

#### UI Integration (`ui/src/App.jsx`)
- Added `climateStress` layer to layer toggle system
- Integrated `ClimateStressLayer` into `SimpleHeatmap` component
- Added `PolicymakerAlert` to right panel above risk distribution charts
- Enriched signals with climate zone data for alert processing

#### Layer Toggle Updates (`ui/src/components/LayerToggle.jsx`)
- Added "🌡️ Climate Stress Zones" toggle option
- Positioned between Climate and Mining indicators
- Supports independent on/off control

## Data Flow

```
1. Event Detection (Intelligence API)
   ↓
2. Risk Calculation (Predictor Service)
   ↓
3. calculate_climate_risk() checks coordinates against GeoJSON polygons
   ↓
4. If in climate zone:
   - Increase risk_score based on impact_zone
   - Set conflict_driver = 'Environmental/Climate'
   - Add climate metadata to RiskSignal
   ↓
5. Frontend receives enriched signals
   ↓
6. ClimateStressLayer visualizes stress zones on map
   ↓
7. PolicymakerAlert filters for intervention-worthy events
   ↓
8. Alerts displayed to policymakers with actionable recommendations
```

## Alert Thresholds

### Intervention Required (Critical)
- Risk Score: > 80
- Recession Index: > 0.8 (80% water/land loss)
- Conflict Type: Farmer-Herder
- **Action**: Resource mediation, water rights negotiation, grazing land allocation

### Climate Adaptation Needed (High)
- Risk Score: > 80
- Climate Impact Zone: High
- **Action**: Climate adaptation programs, resource management, livelihood diversification

## Climate Indicators Data Structure

```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "properties": {
        "region": "Lake Chad Basin",
        "indicator": "Water Recession",
        "recession_index": 0.92,
        "impact_zone": "High",
        "conflict_correlation": "Resource Scarcity / Extremist Recruitment"
      },
      "geometry": {
        "type": "Polygon",
        "coordinates": [[[lon, lat], ...]]
      }
    }
  ]
}
```

## Key Features

1. **Spatiotemporal Analysis**: Events are checked against geographic climate stress zones in real-time
2. **Conflict Multiplier**: Climate stress acts as a risk amplifier, adding 15-25 points to base risk scores
3. **Policy Triggers**: Automated alerts when conditions meet intervention thresholds
4. **Visual Overlay**: Map layer shows climate stress zones with gradient intensity based on recession index
5. **Actionable Intelligence**: Specific recommendations for resource mediation and conflict prevention

## Testing Recommendations

1. Create test events with coordinates inside Lake Chad Basin (13.5-14.5°E, 13.0-14.0°N)
2. Verify risk scores increase by 25 points for High impact zones
3. Confirm PolicymakerAlert displays when risk > 80 and recession_index > 0.8
4. Test layer toggle functionality in UI
5. Verify climate zone popups display correct metadata

## Future Enhancements

1. Add more climate stress zones (Sahel belt, Middle Belt, Niger Delta)
2. Integrate real-time satellite data for dynamic recession index updates
3. Add seasonal variation to climate risk calculations
4. Implement predictive modeling for climate-induced migration patterns
5. Create early warning system for drought-conflict escalation cycles
