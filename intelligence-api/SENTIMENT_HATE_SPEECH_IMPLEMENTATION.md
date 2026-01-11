# Intelligence API Enhancement - Sentiment & Hate Speech Detection

## Overview

The Intelligence API has been enhanced to detect early-warning social signals through sentiment analysis and hate speech detection. These features enable proactive identification of conflicts driven by inflammatory rhetoric and social tensions.

## Implementation Date
January 11, 2026

## Key Features Implemented

### 1. Sentiment Intensity Analysis
**Purpose**: Measure emotional charge in news articles to identify potential for rapid escalation

**Scale**: 0-100
- **0-30**: Neutral/Low intensity - factual reporting
- **31-60**: Moderate intensity - some emotional language
- **61-80**: High intensity - inflammatory language, urgency
- **81-100**: Extreme intensity - fear-mongering, calls to action

**Detection Criteria**:
- Inflammatory language and rhetoric
- Urgency and time-pressure indicators
- Fear-mongering and threat amplification
- Direct calls to action or mobilization
- Emotional appeals and charged vocabulary

**Example**:
```json
{
  "sentiment_intensity": 85,
  "interpretation": "Extremely charged language indicating high potential for rapid escalation"
}
```

### 2. Hate Speech Indicators
**Purpose**: Identify specific markers of hate speech that may incite violence

**Detected Markers**:
- **Ethnic Targeting**: Slurs, stereotypes, or derogatory language about ethnic groups
- **Religious Intolerance**: Anti-religious rhetoric, blasphemy accusations
- **Dehumanization**: Language that strips human dignity or compares groups to animals/objects
- **Incitement to Violence**: Direct or indirect calls for harm against groups
- **Scapegoating**: Blaming specific groups for societal problems
- **Conspiracy Theories**: False narratives targeting specific communities

**Example**:
```json
{
  "hate_speech_indicators": [
    "ethnic targeting",
    "dehumanization",
    "incitement"
  ]
}
```

### 3. Conflict Driver Categorization
**Purpose**: Classify the primary cause of conflict for targeted intervention strategies

**Categories**:

#### Economic
- Fuel price increases
- Inflation and cost of living
- Unemployment and job scarcity
- Resource competition (land, water, minerals)
- Economic inequality

**Example Events**:
- Fuel subsidy removal protests
- Market trader clashes over prices
- Unemployment-driven youth unrest

#### Environmental
- Climate change impacts (drought, flooding)
- Land degradation and desertification
- Water scarcity
- Agricultural stress
- Forced migration due to environmental factors

**Example Events**:
- Farmer-herder clashes over grazing land
- Flooding-induced displacement conflicts
- Drought-related resource competition

#### Social
- Hate speech and inflammatory rhetoric
- Ethnic tensions and identity conflicts
- Religious intolerance
- Social media chatter and misinformation
- Political polarization

**Example Events**:
- Ethnic violence triggered by social media posts
- Religious riots following inflammatory sermons
- Political rallies with divisive rhetoric

## Data Schema

### Enhanced ParsedEvent Model

```python
class ParsedEvent(BaseModel):
    # Core fields (existing)
    event_type: str
    state: str
    lga: str
    severity: str
    source_title: str
    source_url: str
    
    # Early-warning social signals (NEW)
    sentiment_intensity: Optional[int] = Field(default=None, ge=0, le=100)
    hate_speech_indicators: Optional[list[str]] = Field(default_factory=list)
    conflict_driver: Optional[str] = Field(default=None, regex=r'^(Economic|Environmental|Social)$')
    
    parsed_at: str
```

### MongoDB Document Example

```json
{
  "_id": "507f1f77bcf86cd799439011",
  "event_type": "clash",
  "state": "Plateau",
  "lga": "Jos North",
  "severity": "high",
  "source_title": "Ethnic Tensions Escalate in Jos Following Inflammatory Social Media Posts",
  "source_url": "https://example.com/article",
  "sentiment_intensity": 82,
  "hate_speech_indicators": [
    "ethnic targeting",
    "dehumanization",
    "incitement"
  ],
  "conflict_driver": "Social",
  "parsed_at": "2026-01-11T10:30:00Z"
}
```

## LLM Prompt Engineering

### Enhanced System Prompt

The LLM prompt has been updated to extract all seven fields with specific guidance:

```
You are a Nextier Conflict Analyst specializing in early-warning social signals.

Analyze the text and extract the following information in valid JSON format:

1. Event_Type: Type of event (clash, conflict, violence, protest, political, security, crime, economic, social, unknown)
2. State: Nigerian state where event occurred
3. LGA: Local Government Area where event occurred
4. Severity: Event severity (low, medium, high, critical)
5. Sentiment_Intensity: Emotional intensity on scale 0-100 (0=neutral, 100=extremely charged)
   - Consider inflammatory language, urgency, fear-mongering, calls to action
   - High scores (70-100) indicate potential for rapid escalation
6. Hate_Speech_Indicators: Array of detected hate speech markers (empty array if none)
   - Examples: ethnic slurs, religious intolerance, dehumanizing language, incitement to violence
   - Be specific: ["ethnic targeting", "religious intolerance", "dehumanization", "incitement"]
7. Conflict_Driver: Primary cause category
   - "Economic" - fuel prices, inflation, unemployment, resource scarcity
   - "Environmental" - climate change, drought, flooding, land degradation
   - "Social" - hate speech, ethnic tensions, religious conflict, social media chatter

Return ONLY valid JSON with these exact field names.
```

### Validation Logic

The LLM service includes robust validation:

1. **Sentiment Intensity Validation**:
   - Must be integer between 0-100
   - Out-of-range values set to `None`
   - Invalid types logged and set to `None`

2. **Hate Speech Indicators Validation**:
   - Must be a list/array
   - Non-list values converted to empty array
   - Individual markers validated as strings

3. **Conflict Driver Validation**:
   - Must be one of: "Economic", "Environmental", "Social"
   - Invalid values set to `None`
   - Case-sensitive matching

## Use Cases

### 1. Early Warning for Social Media-Driven Violence

**Scenario**: Inflammatory social media posts trigger ethnic violence

**Detection**:
```json
{
  "event_type": "violence",
  "sentiment_intensity": 92,
  "hate_speech_indicators": ["ethnic targeting", "incitement", "dehumanization"],
  "conflict_driver": "Social"
}
```

**Action**: Immediate alert to security agencies, social media monitoring intensified

### 2. Climate-Induced Farmer-Herder Conflicts

**Scenario**: Drought forces herders into farmland, triggering clashes

**Detection**:
```json
{
  "event_type": "clash",
  "sentiment_intensity": 65,
  "hate_speech_indicators": [],
  "conflict_driver": "Environmental"
}
```

**Action**: Deploy environmental mitigation strategies, water resource management

### 3. Economic Protest Escalation

**Scenario**: Fuel price protests turn violent due to inflammatory rhetoric

**Detection**:
```json
{
  "event_type": "protest",
  "sentiment_intensity": 78,
  "hate_speech_indicators": ["incitement"],
  "conflict_driver": "Economic"
}
```

**Action**: Economic policy communication, crowd management, de-escalation

## API Response Examples

### High-Risk Social Conflict

```json
{
  "id": "507f1f77bcf86cd799439011",
  "event_type": "violence",
  "state": "Kaduna",
  "lga": "Zaria",
  "severity": "critical",
  "source_title": "Ethnic Violence Erupts Following Hate Speech Rally",
  "source_url": "https://example.com/article",
  "sentiment_intensity": 95,
  "hate_speech_indicators": [
    "ethnic targeting",
    "religious intolerance",
    "dehumanization",
    "incitement"
  ],
  "conflict_driver": "Social",
  "parsed_at": "2026-01-11T10:30:00Z"
}
```

### Environmental Conflict

```json
{
  "id": "507f1f77bcf86cd799439012",
  "event_type": "clash",
  "state": "Benue",
  "lga": "Makurdi",
  "severity": "high",
  "source_title": "Farmers and Herders Clash Over Grazing Land Amid Drought",
  "source_url": "https://example.com/article",
  "sentiment_intensity": 58,
  "hate_speech_indicators": [],
  "conflict_driver": "Environmental",
  "parsed_at": "2026-01-11T10:31:00Z"
}
```

### Economic Protest

```json
{
  "id": "507f1f77bcf86cd799439013",
  "event_type": "protest",
  "state": "Lagos",
  "lga": "Ikeja",
  "severity": "medium",
  "source_title": "Fuel Price Protests Turn Violent in Lagos",
  "source_url": "https://example.com/article",
  "sentiment_intensity": 72,
  "hate_speech_indicators": ["incitement"],
  "conflict_driver": "Economic",
  "parsed_at": "2026-01-11T10:32:00Z"
}
```

## Integration with Risk Scoring

The new fields enhance the predictor service's risk calculation:

### Sentiment Intensity Multiplier
- **High sentiment (70-100)**: Apply 1.2x multiplier to base risk score
- **Extreme sentiment (85-100)**: Apply 1.5x multiplier + flag for immediate review

### Hate Speech Escalation Factor
- **1-2 indicators**: +10 risk points
- **3-4 indicators**: +20 risk points
- **5+ indicators**: +30 risk points + critical alert

### Conflict Driver Weighting
- **Social conflicts**: Higher weight for sentiment and hate speech
- **Environmental conflicts**: Higher weight for climate vulnerability
- **Economic conflicts**: Higher weight for inflation and fuel prices

## Trend Analysis Queries

### High Sentiment Events by State

```javascript
db.events.aggregate([
  { $match: { sentiment_intensity: { $gte: 70 } } },
  { $group: { 
      _id: "$state", 
      avg_sentiment: { $avg: "$sentiment_intensity" },
      count: { $sum: 1 }
  }},
  { $sort: { avg_sentiment: -1 } }
])
```

### Hate Speech Hotspots

```javascript
db.events.aggregate([
  { $match: { hate_speech_indicators: { $ne: [] } } },
  { $unwind: "$hate_speech_indicators" },
  { $group: {
      _id: { state: "$state", indicator: "$hate_speech_indicators" },
      count: { $sum: 1 }
  }},
  { $sort: { count: -1 } }
])
```

### Conflict Driver Distribution

```javascript
db.events.aggregate([
  { $match: { conflict_driver: { $ne: null } } },
  { $group: {
      _id: "$conflict_driver",
      count: { $sum: 1 },
      avg_severity: { $avg: { $cond: [
        { $eq: ["$severity", "critical"] }, 4,
        { $cond: [
          { $eq: ["$severity", "high"] }, 3,
          { $cond: [
            { $eq: ["$severity", "medium"] }, 2, 1
          ]}
        ]}
      ]}}
  }},
  { $sort: { count: -1 } }
])
```

## Performance Considerations

### LLM Processing Time
- Enhanced prompt adds ~2-3 seconds to processing time
- Acceptable trade-off for early-warning capabilities
- Batch processing maintains throughput

### MongoDB Storage
- New fields add ~100-200 bytes per document
- Indexed fields: `sentiment_intensity`, `conflict_driver`
- Efficient querying for trend analysis

### Validation Overhead
- Minimal impact (<100ms per event)
- Ensures data quality and consistency
- Prevents invalid data from polluting database

## Future Enhancements

### Potential Improvements
1. **Sentiment Trend Detection**: Track sentiment changes over time per location
2. **Hate Speech Taxonomy**: Expand to 20+ specific indicators
3. **Multi-Language Support**: Detect hate speech in Hausa, Yoruba, Igbo
4. **Social Media Integration**: Direct monitoring of Twitter/Facebook
5. **Predictive Modeling**: ML model trained on sentiment + hate speech patterns
6. **Real-Time Alerts**: Webhook notifications for high-sentiment events
7. **Conflict Driver Combinations**: Multi-factor causation analysis

## Deployment Notes

### Prerequisites
1. Ollama LLM must be running and accessible
2. MongoDB connection established
3. RabbitMQ queue configured

### Testing
```bash
# Test sentiment extraction
curl -X POST http://localhost:8001/api/v1/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Ethnic Violence Erupts Following Inflammatory Rally",
    "content": "Tensions escalated after hate speech targeting minority groups..."
  }'
```

### Monitoring
- Check logs for validation warnings
- Monitor sentiment_intensity distribution
- Track hate_speech_indicators frequency
- Analyze conflict_driver patterns

## Summary

The Intelligence API now provides comprehensive early-warning social signal detection through:

✅ **Sentiment Intensity Analysis** - 0-100 scale emotional charge measurement  
✅ **Hate Speech Detection** - Specific marker identification for incitement  
✅ **Conflict Driver Categorization** - Economic/Environmental/Social classification  
✅ **Enhanced LLM Prompting** - Detailed extraction guidance  
✅ **Robust Validation** - Data quality assurance  
✅ **MongoDB Integration** - Persistent storage for trend analysis  

These enhancements enable proactive conflict prevention by identifying inflammatory rhetoric and social tensions before they escalate into violence.
