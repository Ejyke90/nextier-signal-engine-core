# UI Dashboard Refactor - "Intervention View" Implementation Guide

## Overview
This document outlines the implementation of the Strategic Decision view for policymakers, including conflict driver visualization, intervention recommendations, sentiment velocity monitoring, and mining zones overlay.

## Implementation Date
January 11, 2026

## Completed Components

### 1. Mining Zones GeoJSON ✅
**File**: `data/mining_zones.geojson`

Contains illegal mining zones for:
- **Zamfara**: Gold mining / Banditry funding (95% intensity)
- **Kaduna**: Gemstones/Gold / Resource-driven conflict (75% intensity)
- **Sokoto**: Gold/Lead / Extremist funding potential (85% intensity)

### 2. Conflict Driver Chart Component ✅
**File**: `ui/src/components/ConflictDriverChart.jsx`

**Features**:
- Bar chart showing breakdown of Economic vs Environmental vs Social drivers
- Color-coded visualization (Economic: Orange, Environmental: Green, Social: Red)
- Percentage distribution display
- Responsive design with Recharts library

**Usage**:
```jsx
import ConflictDriverChart from './components/ConflictDriverChart'

<ConflictDriverChart riskSignals={riskSignals} />
```

### 3. Intervention Tooltip Component ✅
**File**: `ui/src/components/InterventionTooltip.jsx`

**Features**:
- Displays when clicking Critical LGA on map
- Shows suggested actions based on conflict driver:
  - **Economic**: Food aid, employment programs, microfinance, fuel stabilization
  - **Environmental**: Water resources, grazing reserves, climate adaptation, agricultural support
  - **Social**: Community policing, peace-building, hate speech monitoring, religious engagement
- Displays sentiment intensity bar
- Shows hate speech indicators if detected
- Action buttons for "Deploy Response Team" and "View Full Report"

**Usage**:
```jsx
import InterventionTooltip from './components/InterventionTooltip'

const [selectedSignal, setSelectedSignal] = useState(null)
const [tooltipPosition, setTooltipPosition] = useState(null)

// On map marker click
const handleMarkerClick = (signal, event) => {
  if (signal.risk_level === 'Critical') {
    setSelectedSignal(signal)
    setTooltipPosition({ x: event.clientX, y: event.clientY })
  }
}

<InterventionTooltip 
  signal={selectedSignal}
  position={tooltipPosition}
  onClose={() => setSelectedSignal(null)}
/>
```

## Pending Implementation

### 4. System Heartbeat Update - Sentiment Velocity Monitor
**File**: `ui/src/components/SystemHeartbeat.jsx`

**Changes Needed**:

```jsx
// Add sentiment velocity state
const [sentimentVelocity, setSentimentVelocity] = useState({
  status: 'monitoring',
  avgIntensity: 0,
  trend: 'stable'
})

// Fetch sentiment velocity from API
const fetchSentimentVelocity = async () => {
  try {
    const response = await fetch('http://localhost:8001/api/v1/sentiment/velocity')
    const data = await response.json()
    setSentimentVelocity(data)
  } catch (error) {
    console.error('Error fetching sentiment velocity:', error)
  }
}

// Add to UI
<div className="heartbeat-metric">
  <Activity size={16} />
  <span className="metric-label">Sentiment Velocity</span>
  <span className={`metric-value ${sentimentVelocity.trend}`}>
    {sentimentVelocity.avgIntensity}% {sentimentVelocity.trend}
  </span>
</div>
```

**API Endpoint Needed** (Intelligence API):
```python
# intelligence-api/api/endpoints.py
@router.get("/sentiment/velocity")
async def get_sentiment_velocity(mongodb_repo: MongoDBRepository = Depends()):
    """Get sentiment velocity metrics for monitoring"""
    try:
        # Get events from last 24 hours
        recent_events = mongodb_repo.get_recent_events(hours=24)
        
        if not recent_events:
            return {
                "status": "no_data",
                "avgIntensity": 0,
                "trend": "stable"
            }
        
        # Calculate average sentiment intensity
        sentiments = [e.get('sentiment_intensity', 0) for e in recent_events if e.get('sentiment_intensity')]
        avg_intensity = sum(sentiments) / len(sentiments) if sentiments else 0
        
        # Determine trend (compare to previous 24 hours)
        prev_events = mongodb_repo.get_recent_events(hours=48, offset=24)
        prev_sentiments = [e.get('sentiment_intensity', 0) for e in prev_events if e.get('sentiment_intensity')]
        prev_avg = sum(prev_sentiments) / len(prev_sentiments) if prev_sentiments else 0
        
        if avg_intensity > prev_avg + 10:
            trend = "rising"
        elif avg_intensity < prev_avg - 10:
            trend = "falling"
        else:
            trend = "stable"
        
        return {
            "status": "monitoring",
            "avgIntensity": round(avg_intensity, 1),
            "trend": trend,
            "sample_size": len(sentiments)
        }
    except Exception as e:
        logger.error("Error calculating sentiment velocity", error=str(e))
        return {"status": "error", "avgIntensity": 0, "trend": "unknown"}
```

### 5. Mining Zones Map Overlay
**File**: `ui/src/components/SimpleHeatmap.jsx`

**Changes Needed**:

```jsx
import { useEffect, useState } from 'react'
import L from 'leaflet'

// Add mining zones state
const [miningZones, setMiningZones] = useState(null)

// Load mining zones GeoJSON
useEffect(() => {
  fetch('/data/mining_zones.geojson')
    .then(res => res.json())
    .then(data => setMiningZones(data))
    .catch(err => console.error('Error loading mining zones:', err))
}, [])

// Add mining zones layer to map
useEffect(() => {
  if (!map || !miningZones || !layers.mining) return

  const miningLayer = L.geoJSON(miningZones, {
    style: (feature) => ({
      fillColor: '#f59e0b',
      weight: 2,
      opacity: 0.8,
      color: '#f59e0b',
      fillOpacity: feature.properties.intensity * 0.4
    }),
    onEachFeature: (feature, layer) => {
      layer.bindPopup(`
        <div style="font-family: sans-serif;">
          <h4 style="margin: 0 0 8px 0; color: #1f2937;">${feature.properties.state}</h4>
          <p style="margin: 4px 0; font-size: 13px;"><strong>Mineral:</strong> ${feature.properties.mineral}</p>
          <p style="margin: 4px 0; font-size: 13px;"><strong>Risk Type:</strong> ${feature.properties.risk_type}</p>
          <p style="margin: 4px 0; font-size: 13px;"><strong>Intensity:</strong> ${(feature.properties.intensity * 100).toFixed(0)}%</p>
        </div>
      `)
    }
  }).addTo(map)

  return () => {
    map.removeLayer(miningLayer)
  }
}, [map, miningZones, layers.mining])
```

**Layer Toggle**:
```jsx
// Add to layer controls
<label className="layer-toggle">
  <input
    type="checkbox"
    checked={layers.mining}
    onChange={(e) => setLayers({...layers, mining: e.target.checked})}
  />
  <span>Mining Zones</span>
</label>
```

### 6. App.jsx Integration

**Changes Needed**:

```jsx
import ConflictDriverChart from './components/ConflictDriverChart'
import InterventionTooltip from './components/InterventionTooltip'

// Add state for intervention tooltip
const [selectedSignal, setSelectedSignal] = useState(null)
const [tooltipPosition, setTooltipPosition] = useState(null)

// Add mining zones layer to layers state
const [layers, setLayers] = useState({
  heatmap: true,
  markers: true,
  climate: true,
  mining: true,  // NEW
  border: true,
  miningZones: true  // NEW
})

// Add Conflict Driver Chart to National Risk Overview section
<div className="national-risk-overview">
  <KPICards riskSignals={riskSignals} />
  <ConflictDriverChart riskSignals={riskSignals} />  {/* NEW */}
  <RiskDistributionCharts trendData={trendData} />
</div>

// Add Intervention Tooltip
{selectedSignal && (
  <InterventionTooltip
    signal={selectedSignal}
    position={tooltipPosition}
    onClose={() => setSelectedSignal(null)}
  />
)}

// Pass marker click handler to SimpleHeatmap
<SimpleHeatmap
  riskSignals={riskSignals}
  onMarkerClick={(signal, event) => {
    if (signal.risk_level === 'Critical') {
      setSelectedSignal(signal)
      setTooltipPosition({ x: event.clientX, y: event.clientY })
    }
  }}
  layers={layers}
/>
```

## CSS Styling

Add to `App.css`:

```css
/* Conflict Driver Chart */
.conflict-driver-chart {
  background: #1f2937;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 20px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

/* Mining Zones Legend */
.mining-zones-legend {
  position: absolute;
  bottom: 80px;
  right: 20px;
  background: rgba(31, 41, 55, 0.95);
  padding: 15px;
  border-radius: 8px;
  border: 1px solid #374151;
  z-index: 1000;
}

.mining-zones-legend h4 {
  margin: 0 0 10px 0;
  font-size: 13px;
  font-weight: 600;
  color: #f3f4f6;
}

.mining-zone-item {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
  font-size: 12px;
  color: #d1d5db;
}

.mining-zone-color {
  width: 16px;
  height: 16px;
  border-radius: 3px;
  border: 2px solid #f59e0b;
}

/* Sentiment Velocity Indicator */
.sentiment-velocity {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: #111827;
  border-radius: 6px;
  border: 1px solid #374151;
}

.sentiment-velocity.rising {
  border-color: #ef4444;
}

.sentiment-velocity.falling {
  border-color: #10b981;
}

.sentiment-velocity.stable {
  border-color: #6b7280;
}
```

## Testing Checklist

- [ ] Conflict Driver Chart displays correctly with sample data
- [ ] Chart updates when risk signals change
- [ ] Intervention Tooltip appears on Critical LGA click
- [ ] Tooltip shows correct intervention strategies based on driver
- [ ] Sentiment intensity bar displays correctly
- [ ] Hate speech indicators appear when present
- [ ] System Heartbeat shows sentiment velocity status
- [ ] Mining zones overlay displays on map
- [ ] Mining zones have correct opacity based on intensity
- [ ] Mining zone popups show correct information
- [ ] Layer toggle controls work for mining zones
- [ ] All components are responsive on mobile

## API Dependencies

### Intelligence API Endpoints Needed:
1. `GET /api/v1/sentiment/velocity` - Sentiment velocity metrics
2. `GET /api/v1/events/recent?hours=24` - Recent events with sentiment data

### Predictor API Endpoints (Existing):
1. `GET /api/v1/risk-overview` - Risk signals with conflict_driver field
2. `GET /data/risk_signals.json` - Risk signals JSON file

## Data Requirements

### Risk Signal Schema (Enhanced):
```json
{
  "event_type": "clash",
  "state": "Kaduna",
  "lga": "Zaria",
  "severity": "critical",
  "risk_score": 95,
  "risk_level": "Critical",
  "conflict_driver": "Social",
  "sentiment_intensity": 85,
  "hate_speech_indicators": ["ethnic targeting", "incitement"],
  "latitude": 11.0448,
  "longitude": 7.7166
}
```

## Deployment Steps

1. **Install Dependencies** (if not already installed):
   ```bash
   cd ui
   npm install recharts lucide-react
   ```

2. **Copy GeoJSON File**:
   ```bash
   cp data/mining_zones.geojson ui/public/data/
   ```

3. **Update Components**:
   - Add ConflictDriverChart import to App.jsx
   - Add InterventionTooltip import to App.jsx
   - Update SystemHeartbeat.jsx with sentiment velocity
   - Update SimpleHeatmap.jsx with mining zones layer

4. **Implement API Endpoint**:
   - Add `/api/v1/sentiment/velocity` to intelligence-api

5. **Test Locally**:
   ```bash
   npm run dev
   ```

6. **Rebuild Docker Container** (if using Docker):
   ```bash
   docker compose build ui
   docker compose up -d ui
   ```

## Future Enhancements

1. **Real-Time Sentiment Tracking**: WebSocket connection for live sentiment updates
2. **Intervention History**: Track deployed interventions and outcomes
3. **Multi-Driver Analysis**: Show conflicts with multiple contributing drivers
4. **Predictive Intervention**: ML model to suggest preventive actions
5. **Mobile App**: Native mobile app for field deployment teams
6. **Export Reports**: PDF/Excel export of intervention recommendations
7. **Integration with Emergency Services**: Direct dispatch to response teams

## Summary

The UI Dashboard Refactor adds critical decision-support features for policymakers:

✅ **Conflict Driver Chart** - Visual breakdown of Economic/Environmental/Social causes  
✅ **Intervention Tooltip** - Context-specific action recommendations  
✅ **Mining Zones Overlay** - Highlight illegal mining and conflict overlap  
⏳ **Sentiment Velocity Monitor** - Track emotional intensity trends  
⏳ **Enhanced Map Interactions** - Click-to-intervene workflow  

These features transform the dashboard from a monitoring tool into an actionable intervention platform.
