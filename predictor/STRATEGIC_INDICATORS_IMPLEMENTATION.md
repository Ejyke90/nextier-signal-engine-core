# Strategic Deep Indicators - Implementation Documentation

## Overview

The predictor service has been refactored to implement **Strategic Deep Indicators** requested by the client. These indicators provide enhanced risk assessment capabilities by incorporating state-level normalized data and advanced detection logic.

## Implementation Date
January 11, 2026

## Key Features Implemented

### 1. Climate Stress Multiplier
**Data Source**: `climate_vulnerability` from `nigeria_econ_indicators.csv`

**Logic**:
- If `climate_vulnerability > 0.7` (70%), apply bonus points
- Bonus calculation: `climate_vulnerability * 15` (up to 15 points)
- Captures environmental stress that amplifies conflict risk

**Example**:
- Borno State: 95% climate vulnerability → +14.25 risk points
- Rationale: High climate stress increases resource scarcity and displacement

### 2. Funding Risk Multiplier
**Data Source**: `mining_density` from `nigeria_econ_indicators.csv`

**Logic**:
- If `mining_density > 0.6` (60%), apply bonus points and tag as high escalation
- Bonus calculation: `mining_density * 20` (up to 20 points)
- Tags risk signal with `[HIGH ESCALATION POTENTIAL]` prefix

**Example**:
- Sokoto State: 85% mining density → +17 risk points + escalation tag
- Rationale: High mining density enables illicit funding for armed groups

### 3. Farmer-Herder Conflict Logic
**Data Source**: `migration_pressure` from `nigeria_econ_indicators.csv`

**Detection**:
- Keyword-based classification using event title, content, and type
- Keywords: farmer, herder, herdsmen, fulani, pastoralist, cattle, grazing, farmland, livestock

**Logic**:
- If classified as Farmer-Herder conflict AND `migration_pressure > 0.5` (50%)
- Apply multiplier: `1 + migration_pressure` (1.5x to 2.0x)
- Multiplies entire risk score

**Example**:
- Benue State Farmer-Herder clash: 80% migration pressure → 1.8x multiplier
- Base score 60 → Final score 108 (capped at 100)
- Rationale: Pastoralist displacement intensifies land competition

### 4. High Escalation Potential Tagging
**Trigger**: `mining_density > 0.6`

**Implementation**:
- Adds `[HIGH ESCALATION POTENTIAL]` prefix to trigger_reason
- Sets `high_escalation_potential` field to `true` in RiskSignal
- Visible in API responses and UI alerts

**Purpose**: Flags conflicts in high mining zones as having greater potential for escalation due to illicit funding streams

### 5. Surge Detection (Early Warning)
**Logic**: Detects >20% risk increase in 15-minute scrape window

**Implementation**:
```python
def detect_surge(state, lga, current_risk_score):
    location_key = f"{state}:{lga}"
    if location_key in previous_risk_scores:
        previous_score = previous_risk_scores[location_key]
        percentage_increase = ((current_risk_score - previous_score) / previous_score) * 100
        
        if percentage_increase > 20:
            surge_detected = True
            # Log warning and add to trigger_reason
```

**Features**:
- Tracks risk scores per location across scrape cycles
- Compares current score to previous score
- Adds ⚠️ SURGE ALERT to trigger_reason if >20% increase detected
- Sets `surge_detected` and `surge_percentage_increase` fields

**Example**:
- Kaduna/Zaria: Previous score 45 → Current score 60 → 33% increase
- Alert: "⚠️ SURGE ALERT: Risk increased by 33.3% in last 15 minutes - rapid escalation detected"

## Data Schema

### Strategic Indicators CSV
**File**: `/data/nigeria_econ_indicators.csv`

```csv
state,poverty_rate,inflation_rate,unemployment,mining_density,climate_vulnerability,migration_pressure
Sokoto,0.91,12.94,0.45,0.85,0.70,0.65
Borno,0.83,14.50,0.52,0.30,0.95,0.90
Kaduna,0.67,13.20,0.40,0.75,0.40,0.75
Benue,0.65,15.10,0.38,0.20,0.85,0.80
Lagos,0.31,11.80,0.18,0.05,0.20,0.30
```

**Values**: Normalized 0-1 scale based on North-South disparities

### RiskSignal Model Extensions
New fields added to `predictor/models/risk.py`:

```python
# Strategic Deep Indicators
climate_vulnerability: Optional[float] = Field(default=None, ge=0, le=1)
mining_density: Optional[float] = Field(default=None, ge=0, le=1)
migration_pressure: Optional[float] = Field(default=None, ge=0, le=1)
poverty_rate: Optional[float] = Field(default=None, ge=0, le=1)
high_escalation_potential: bool = Field(default=False)
is_farmer_herder_conflict: bool = Field(default=False)
surge_detected: bool = Field(default=False)
surge_percentage_increase: Optional[float] = Field(default=None)
```

## Risk Calculation Flow

### Enhanced Algorithm
```
1. Base Score Calculation
   ├─ Event type score (clash: 40, conflict: 35, etc.)
   ├─ Severity modifier (high: 20, critical: 30, etc.)
   └─ Economic modifiers (inflation, fuel prices)

2. Load Strategic Indicators (state-level)
   ├─ climate_vulnerability
   ├─ mining_density
   ├─ migration_pressure
   └─ poverty_rate

3. Apply Multidimensional Multipliers
   ├─ Climate Stress Multiplier (if vulnerability > 0.7)
   ├─ Funding Risk Multiplier (if mining_density > 0.6)
   ├─ Farmer-Herder Logic (if detected + migration_pressure > 0.5)
   └─ Sahelian Multiplier (border activity)

4. Detect Surge (>20% increase from previous cycle)

5. Tag High Escalation Potential (if mining_density > 0.6)

6. Generate RiskSignal with all indicators
```

## API Response Example

```json
{
  "event_type": "clash",
  "state": "Sokoto",
  "lga": "Wurno",
  "severity": "high",
  "risk_score": 92.5,
  "risk_level": "Critical",
  "trigger_reason": "[HIGH ESCALATION POTENTIAL] Critical Risk: High Climate Vulnerability (70%) - environmental stress amplifies conflict risk; High Escalation Potential due to Illicit Funding - Mining density 85% enables armed group financing; Farmer-Herder Conflict amplified by Migration Pressure (65%) - pastoralist displacement intensifies land competition; ⚠️ SURGE ALERT: Risk increased by 28.5% in last 15 minutes - rapid escalation detected",
  "climate_vulnerability": 0.70,
  "mining_density": 0.85,
  "migration_pressure": 0.65,
  "poverty_rate": 0.91,
  "high_escalation_potential": true,
  "is_farmer_herder_conflict": true,
  "surge_detected": true,
  "surge_percentage_increase": 28.5,
  "calculated_at": "2026-01-11T05:15:00Z"
}
```

## Testing Scenarios

### Scenario 1: High Mining Density Zone
**State**: Kaduna (mining_density: 0.75)
**Expected**:
- Funding risk bonus: +15 points
- `high_escalation_potential`: true
- Trigger reason includes: "[HIGH ESCALATION POTENTIAL]"

### Scenario 2: Farmer-Herder Conflict
**State**: Benue (migration_pressure: 0.80)
**Event**: Contains keywords "farmer", "herder", "cattle"
**Expected**:
- Classification: `is_farmer_herder_conflict`: true
- Multiplier: 1.8x applied to base score
- Trigger reason includes migration pressure explanation

### Scenario 3: Climate Stress
**State**: Borno (climate_vulnerability: 0.95)
**Expected**:
- Climate stress bonus: +14.25 points
- Trigger reason includes climate vulnerability percentage

### Scenario 4: Surge Detection
**Location**: Kaduna/Zaria
**Previous Score**: 50
**Current Score**: 65
**Expected**:
- Percentage increase: 30%
- `surge_detected`: true
- `surge_percentage_increase`: 30.0
- Trigger reason includes: "⚠️ SURGE ALERT"

## Integration Points

### 1. Automated Scraping
- Strategic indicators loaded on service initialization
- Applied to every risk calculation automatically
- No manual intervention required

### 2. UI Dashboard
- High escalation signals displayed with special tag
- Surge alerts trigger instant toast notifications
- Strategic indicator values visible in signal details

### 3. MongoDB Storage
- All strategic indicator fields persisted
- Enables historical analysis of indicator impact
- Supports trend detection over time

## Performance Considerations

### Caching
- Strategic indicators CSV loaded once at service startup
- State-level lookups cached in memory
- Previous risk scores stored in dictionary for surge detection

### Memory Usage
- Strategic indicators: ~5 states × 6 indicators = minimal overhead
- Surge tracking: One entry per unique state/LGA combination
- Automatic cleanup not implemented (consider for production)

## Future Enhancements

### Potential Improvements
1. **Dynamic Thresholds**: Make 0.7, 0.6, 0.5 thresholds configurable
2. **Weighted Combinations**: Combine multiple strategic indicators with custom weights
3. **Temporal Analysis**: Track indicator trends over multiple scrape cycles
4. **Surge Decay**: Implement time-based decay for surge detection
5. **Additional Indicators**: Expand CSV with unemployment, poverty impact
6. **ML Integration**: Use strategic indicators as features for predictive models

### Scalability
- Current implementation handles 5 states efficiently
- For full 36-state coverage, consider:
  - Database storage for indicators
  - Redis caching for high-frequency lookups
  - Batch processing optimizations

## Deployment Notes

### Prerequisites
1. Ensure `/data/nigeria_econ_indicators.csv` exists
2. Verify CSV format matches schema
3. Restart predictor service to load new indicators

### Monitoring
- Check logs for "Loaded strategic indicators for X states"
- Monitor surge detection warnings in logs
- Track high escalation potential signals in dashboard

### Rollback
If issues occur:
1. Remove strategic indicators CSV
2. Service will gracefully handle missing data
3. Risk calculations continue with existing multidimensional factors

## Summary

The Strategic Deep Indicators refactoring enhances the NNVCD predictor with:

✅ **Climate Stress Multiplier** - Environmental vulnerability amplification  
✅ **Funding Risk Multiplier** - Mining density escalation tagging  
✅ **Farmer-Herder Logic** - Migration pressure conflict amplification  
✅ **High Escalation Tagging** - Clear flagging of high-risk zones  
✅ **Surge Detection** - Early warning for rapid escalation (>20% increase)  

These indicators provide deeper, more nuanced risk assessment aligned with on-the-ground realities in Nigeria's conflict landscape.
