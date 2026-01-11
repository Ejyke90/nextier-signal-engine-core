# Dynamic Risk Simulation - Implementation Documentation

## Overview

This document describes the dynamic risk simulation feature that enables real-time risk score recalculation based on three adjustable parameters: fuel price index, inflation rate, and social media chatter intensity.

## Architecture

### Components

1. **SimulationParameters Model** (`models/risk.py`)
   - Validates slider inputs (0-100 range)
   - Three parameters: `fuel_price_index`, `inflation_rate`, `chatter_intensity`

2. **Dynamic Risk Calculation** (`services/risk_service.py`)
   - `calculate_risk_score_dynamic()` method
   - Weighted scoring model with real-time parameter injection

3. **Simulation Endpoint** (`api/endpoints.py`)
   - `POST /simulate` endpoint
   - Returns GeoJSON FeatureCollection with updated risk scores

## Key Features

### 1. Economic Igniter

**Trigger Condition:** `fuel_price_index > 80`

**Effect:** Applies 1.5x multiplier to risk scores for **urban LGAs only**

**Rationale:** Economic shocks (fuel price crises) correlate strongly with civil unrest in Nigerian cities.

**Urban LGA Classification:**
- 60+ major urban centers across Nigeria
- Includes: Lagos, Abuja, Kano, Port Harcourt, Kaduna, Ibadan, etc.
- See `utils/config.py` for complete list

**Example:**
```python
# Before Economic Igniter
base_score = 60

# After Economic Igniter (fuel_price_index = 85, urban LGA)
final_score = 60 * 1.5 = 90  # CRITICAL status
```

### 2. Social Trigger

**Parameter:** `chatter_intensity` (0-100)

**Effect:** Maps directly to heatmap visualization properties

**Heatmap Radius Calculation:**
```python
base_radius = 5 km
max_radius = 50 km
heatmap_radius = base_radius + (chatter_intensity / 100) * (max_radius - base_radius)
```

**Heatmap Weight Calculation:**
```python
heatmap_weight = min(1.0, (risk_score / 100) * (1 + chatter_intensity / 100))
```

**Rationale:** High social media chatter indicates broader awareness and potential for event escalation, expanding the geographic "heat zone."

### 3. CRITICAL Status Flag

**Trigger Condition:** `risk_score >= 80`

**Effect:** Sets `status: "CRITICAL"` in response

**Purpose:** Triggers pulsing animation in UI for high-risk events

**Status Levels:**
- `CRITICAL`: risk_score >= 80
- `HIGH`: risk_score >= 60
- `MEDIUM`: risk_score >= 40
- `LOW`: risk_score >= 20
- `MINIMAL`: risk_score < 20

## API Usage

### Endpoint

```
POST /simulate
```

### Request Body

```json
{
  "fuel_price_index": 85.0,
  "inflation_rate": 45.0,
  "chatter_intensity": 70.0
}
```

### Response Format

```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "geometry": {
        "type": "Point",
        "coordinates": [3.3515, 6.6018]
      },
      "properties": {
        "risk_score": 92.5,
        "risk_level": "Critical",
        "status": "CRITICAL",
        "event_type": "clash",
        "state": "Lagos",
        "lga": "Ikeja",
        "severity": "high",
        "source_title": "Communal clash in Ikeja",
        "source_url": "https://example.com/news",
        "trigger_reason": "Critical Risk: High inflation (45.0%); Elevated fuel prices (index: 85/100); Economic Crisis in Urban Center (fuel index: 85) - 1.5x multiplier applied",
        "heatmap_weight": 0.925,
        "heatmap_radius_km": 36.5,
        "is_urban": true,
        "calculated_at": "2026-01-11T04:40:00.000Z"
      }
    }
  ],
  "metadata": {
    "total_events": 150,
    "critical_count": 25,
    "high_count": 40,
    "medium_count": 50,
    "low_count": 35,
    "timestamp": "2026-01-11T04:40:00.000Z",
    "simulation_active": true
  },
  "simulation_params": {
    "fuel_price_index": 85.0,
    "inflation_rate": 45.0,
    "chatter_intensity": 70.0
  }
}
```

## Risk Scoring Algorithm

### Base Score Calculation

```python
base_score = BASE_RISK_SCORE (30)
base_score += event_type_score  # 5-40 points
base_score += severity_modifier  # 3-30 points
```

### Dynamic Economic Modifiers

```python
# Inflation impact
if inflation_rate > INFLATION_THRESHOLD (20%):
    inflation_bonus = min((inflation_rate - 20) * 2, 20)
    base_score += inflation_bonus

# Fuel price impact (scaled from 0-100 index)
fuel_bonus = (fuel_price_index / 100) * 20
base_score += fuel_bonus
```

### Multidimensional Indicators

1. **Climate Multiplier**
   - Flooding > 20% inundation → 1.5x multiplier for clash/conflict events

2. **Mining Multiplier**
   - Proximity < 10km to mining site → +15 points (high funding potential)

3. **Sahelian Multiplier**
   - High border activity in Sokoto/Kebbi → +20 points (Lakurawa presence)

### Economic Igniter Application

```python
if fuel_price_index > 80 and is_urban_lga(lga):
    base_score = base_score * 1.5
```

### Normalization

```python
risk_score = max(0, min(100, base_score))
```

**Guarantee:** Risk score is **always** between 0 and 100.

## Testing

Run comprehensive test suite:

```bash
cd predictor
pytest tests/test_simulation.py -v
```

### Test Coverage

- ✅ Risk score normalization (0-100 bounds)
- ✅ CRITICAL status flag (risk_score > 80)
- ✅ Economic Igniter for urban LGAs
- ✅ Economic Igniter exclusion for rural LGAs
- ✅ Social Trigger heatmap mapping
- ✅ Fuel price index impact
- ✅ Inflation rate impact
- ✅ Parameter validation
- ✅ Missing coordinates handling
- ✅ Urban LGA classification
- ✅ Multidimensional indicators preservation
- ✅ Status level assignment

## Integration with UI

### Slider Configuration

```javascript
// Fuel Price Index Slider
{
  id: 'fuel_price_index',
  label: 'Fuel Price Crisis Index',
  min: 0,
  max: 100,
  default: 50,
  description: 'Economic shock indicator (>80 triggers urban crisis multiplier)'
}

// Inflation Rate Slider
{
  id: 'inflation_rate',
  label: 'Inflation Rate (%)',
  min: 0,
  max: 100,
  default: 25,
  description: 'Current inflation percentage'
}

// Chatter Intensity Slider
{
  id: 'chatter_intensity',
  label: 'Social Media Chatter',
  min: 0,
  max: 100,
  default: 50,
  description: 'Social media activity intensity (affects heatmap radius)'
}
```

### API Call Example

```javascript
async function runSimulation(sliderValues) {
  const response = await fetch('http://localhost:8002/simulate', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      fuel_price_index: sliderValues.fuelPrice,
      inflation_rate: sliderValues.inflation,
      chatter_intensity: sliderValues.chatter
    })
  });
  
  const geojson = await response.json();
  
  // Update map with new GeoJSON
  updateHeatmap(geojson);
  
  // Trigger pulse animation for CRITICAL events
  geojson.features
    .filter(f => f.properties.status === 'CRITICAL')
    .forEach(f => triggerPulseAnimation(f));
}
```

### Heatmap Visualization

```javascript
// Use heatmap_radius_km and heatmap_weight from properties
function updateHeatmap(geojson) {
  geojson.features.forEach(feature => {
    const { heatmap_radius_km, heatmap_weight, status } = feature.properties;
    
    // Create heat circle
    L.circle([feature.geometry.coordinates[1], feature.geometry.coordinates[0]], {
      radius: heatmap_radius_km * 1000, // Convert to meters
      fillOpacity: heatmap_weight,
      color: status === 'CRITICAL' ? '#ff0000' : getColorByRisk(status),
      className: status === 'CRITICAL' ? 'pulse-animation' : ''
    }).addTo(map);
  });
}
```

## Performance Considerations

### Optimization Strategies

1. **Caching:** Economic data lookups are cached with `@lru_cache`
2. **Batch Processing:** All events processed in single request
3. **Efficient Calculations:** No blocking I/O in calculation loop
4. **Limit Parameter:** Default 1000 events, configurable

### Expected Performance

- **1000 events:** ~2-3 seconds response time
- **100 events:** ~200-300ms response time
- **Memory:** ~50MB for typical dataset

## Security Considerations

### Input Validation

- ✅ Pydantic models enforce 0-100 bounds
- ✅ Type validation for all parameters
- ✅ Sanitized database queries
- ✅ No user input in raw SQL/NoSQL queries

### Rate Limiting

Recommended: Implement rate limiting on `/simulate` endpoint

```python
# Example with slowapi
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@router.post("/simulate")
@limiter.limit("10/minute")
async def simulate_risk_scenarios(...):
    ...
```

## Future Enhancements

1. **Historical Simulation:** Compare current vs. historical parameter values
2. **Scenario Presets:** Pre-configured crisis scenarios (e.g., "2023 Fuel Subsidy Removal")
3. **Predictive Modeling:** ML-based forecasting with parameter trends
4. **Multi-Region Comparison:** Side-by-side simulation for different regions
5. **Export Capabilities:** Download simulation results as CSV/PDF

## Troubleshooting

### Common Issues

**Issue:** Risk scores not updating
- **Solution:** Verify events have valid coordinates (latitude/longitude)

**Issue:** Economic Igniter not triggering
- **Solution:** Check LGA is in `URBAN_LGAS` set in `config.py`

**Issue:** Heatmap radius not changing
- **Solution:** Ensure `chatter_intensity` parameter is being passed correctly

**Issue:** All scores showing as CRITICAL
- **Solution:** Check slider values - extreme values (all 100) will trigger high scores

## References

- **Risk Scoring Algorithm:** `predictor/services/risk_service.py:346-522`
- **Urban LGA List:** `predictor/utils/config.py:32-88`
- **API Endpoint:** `predictor/api/endpoints.py:236-361`
- **Models:** `predictor/models/risk.py:114-133`
- **Tests:** `predictor/tests/test_simulation.py`

## Contact

For questions or issues, refer to the main project documentation or create an issue in the repository.
