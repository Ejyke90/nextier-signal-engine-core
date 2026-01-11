# NNVCD System Design - Demo Overview

## Executive Summary

**Nextier Nigeria Violent Conflicts Database (NNVCD)** is a proactive, AI-powered conflict monitoring system that autonomously scrapes news sources every 15 minutes, extracts conflict events using LLM technology, calculates risk scores, and triggers instant alerts for critical situations.

### Key Value Propositions
- 🤖 **Fully Automated**: No manual intervention required - runs 24/7
- ⚡ **Real-Time Intelligence**: Fresh data every 15 minutes
- 🚨 **Instant Alerts**: Critical events (risk > 85) trigger immediate notifications
- 📊 **AI-Powered Analysis**: LLM extracts structured events from unstructured news
- 🗺️ **Geospatial Visualization**: Interactive heatmap with risk distribution

---

## System Architecture

### High-Level Overview

```
┌────────────────────────────────────────────────────────────────────────┐
│                        AUTOMATED PIPELINE                              │
└────────────────────────────────────────────────────────────────────────┘

    ⏰ BACKGROUND SCHEDULER (Every 15 minutes)
                    │
                    ▼
    ┌───────────────────────────────────────────────────────────────┐
    │  📰 NEWS SOURCES                                              │
    │  • Premium Times  • Vanguard  • Guardian  • Daily Trust       │
    └───────────────────────┬───────────────────────────────────────┘
                            │
                            ▼
    ┌───────────────────────────────────────────────────────────────┐
    │  🔍 SCRAPER SERVICE (Port 8000)                               │
    │  ┌─────────────┐   ┌──────────────┐   ┌──────────────┐      │
    │  │  Fetch HTML │──▶│ Deduplicate  │──▶│ Risk Check   │      │
    │  │  Multi-Src  │   │  SHA-256     │   │  Score > 85? │      │
    │  └─────────────┘   └──────────────┘   └──────┬───────┘      │
    │                                               │               │
    │                                    ┌──────────┴──────────┐   │
    │                                    │                     │   │
    │                                    ▼                     ▼   │
    │                          🚨 High Risk Alert    💾 MongoDB    │
    │                             /data/alerts.json                │
    └────────────────────────────────────┬──────────────────────────┘
                                         │
                                         ▼
                            📨 RabbitMQ: scraped_articles
                                         │
                                         ▼
    ┌───────────────────────────────────────────────────────────────┐
    │  🧠 INTELLIGENCE API (Port 8001)                              │
    │  ┌──────────────┐   ┌──────────────┐                         │
    │  │ LLM Extract  │──▶│  Validate    │──▶ 💾 MongoDB           │
    │  │ (Ollama)     │   │  Events      │                         │
    │  └──────────────┘   └──────────────┘                         │
    └────────────────────────────────────┬──────────────────────────┘
                                         │
                                         ▼
                            📨 RabbitMQ: parsed_events
                                         │
                                         ▼
    ┌───────────────────────────────────────────────────────────────┐
    │  📊 PREDICTOR SERVICE (Port 8002)                             │
    │                                                               │
    │  ┌──────────────────────────────────────────────────────┐   │
    │  │  MULTIDIMENSIONAL RISK FACTORS                       │   │
    │  │  • 🌡️  Climate Data (flood, drought indicators)      │   │
    │  │  • ⛏️  Mining Activity (proximity, intensity)        │   │
    │  │  • 🗺️  Border Signals (cross-border tensions)        │   │
    │  │  • 💰 Economic Data (fuel, inflation, unemployment)  │   │
    │  └──────────────────────┬───────────────────────────────┘   │
    │                         ▼                                     │
    │  ┌──────────────────────────────────┐                        │
    │  │  Risk Calculation Algorithm      │                        │
    │  │  • Event severity weighting      │                        │
    │  │  • Geospatial proximity analysis │                        │
    │  │  • Historical conflict patterns  │                        │
    │  └──────────────┬───────────────────┘                        │
    │                 │                                             │
    │                 └──▶ 💾 MongoDB (risk_signals)               │
    └────────────────────────────────────┬──────────────────────────┘
                                         │
                                         ▼
                            📨 RabbitMQ: risk_signals
                                         │
                                         ▼
    ┌───────────────────────────────────────────────────────────────┐
    │  🖥️  REACT DASHBOARD (Port 8080)                              │
    │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
    │  │ 💓 System    │  │ 🗺️  Live     │  │ 🚨 Instant   │       │
    │  │   Heartbeat  │  │    Heatmap   │  │    Alerts    │       │
    │  │              │  │              │  │              │       │
    │  │ • Status     │  │ • Risk Viz   │  │ • Toast      │       │
    │  │ • Next Run   │  │ • Markers    │  │ • High-Risk  │       │
    │  │ • Last Sync  │  │ • Layers     │  │ • Auto-Poll  │       │
    │  └──────────────┘  └──────────────┘  └──────────────┘       │
    └───────────────────────────────────────────────────────────────┘

    📁 SHARED STATE
    • /data/automation_logs.json    (Execution history)
    • /data/high_risk_alerts.json   (Critical alerts)
    • /data/risk_signals.json       (Current risk data)
```

---

## Core Components

### 1. Background Scheduler (Automation Engine)

**Technology**: APScheduler with Cron Trigger

**Schedule**: `*/15 * * * *` (Every 15 minutes)

**Responsibilities**:
- Trigger automated scraping from multiple news sources
- Detect high-risk articles (risk_score > 85)
- Write webhook alerts to shared volume
- Log all executions for audit trail

**Key Features**:
- Single-instance execution (prevents duplicates)
- Graceful error handling with retry logic
- Automatic cleanup of old logs
- Integration with FastAPI lifecycle

### 2. Scraper Service (Port 8000)

**Pattern**: Autonomous Collector

**Data Sources**:
- Premium Times Nigeria
- Vanguard News
- The Guardian Nigeria
- Daily Trust
- Punch Newspapers

**Processing Pipeline**:
```
News Sources → Fetch HTML → Parse Content → Deduplicate → 
MongoDB + RabbitMQ → High-Risk Check → Webhook Alert
```

**Deduplication**: SHA-256 fingerprinting prevents duplicate processing

**High-Risk Detection**:
- Articles with `risk_score > 85` flagged immediately
- Alerts written to `/data/high_risk_alerts.json`
- UI polls this file every 5 seconds for instant notifications

### 3. Intelligence API Service (Port 8001)

**Pattern**: LLM-Powered Event Extractor

**LLM Integration**: Ollama (local deployment)

**Event Extraction**:
```json
{
  "event_type": "clash",
  "location": "Maiduguri, Borno State",
  "actors": ["Boko Haram", "Nigerian Military"],
  "casualties": 15,
  "date": "2026-01-11",
  "severity": "high"
}
```

**Resilience**:
- Circuit breaker protects against LLM failures
- Exponential backoff retry mechanism
- Batch processing for efficiency

### 4. Predictor Service (Port 8002)

**Pattern**: Multidimensional Risk Calculator

**Risk Scoring Algorithm**:
```python
risk_score = (
    event_severity_weight * 0.4 +
    climate_risk_factor * 0.15 +
    mining_proximity_factor * 0.15 +
    border_tension_factor * 0.15 +
    economic_stress_factor * 0.15
)
```

**Multidimensional Risk Factors**:

1. **🌡️ Climate Data**
   - Flood inundation levels
   - Drought severity indicators
   - Rainfall patterns
   - Temperature anomalies

2. **⛏️ Mining Activity**
   - Proximity to mining sites (Haversine distance)
   - Mining intensity levels
   - Resource conflict indicators
   - Illegal mining hotspots

3. **🗺️ Border Signals**
   - Cross-border tension levels
   - Border proximity risk
   - Transnational conflict spillover
   - Migration pressure indicators

4. **💰 Economic Data**
   - Fuel price trends by state
   - Inflation rates
   - Unemployment data
   - Economic stress indices

**Geospatial Analysis**:
- Haversine distance calculations for proximity analysis
- Historical conflict pattern mapping
- Event clustering detection

**Output**: GeoJSON risk signals with multidimensional scoring for map visualization

### 5. UI Dashboard (Port 8080)

**Technology**: React + Leaflet + TailwindCSS

**Key Features**:

#### System Heartbeat Monitor
- Live scheduler status (Active/Inactive)
- Next scrape countdown timer
- Last successful sync timestamp
- Schedule information display

#### Interactive Heatmap
- Real-time risk visualization
- Color-coded severity levels (Critical/High/Medium/Low)
- Clickable markers for event details
- Layer toggles (Climate, Mining, Border zones)

#### Instant Alert System
- Toast notifications for high-risk articles
- 10-second display duration
- Automatic deduplication
- Shows article title and risk score

#### KPI Cards
- Total active signals
- Critical alerts count
- Affected states
- Average risk score

---

## Data Flow (Automated)

### 1. Scraping Cycle (Every 15 Minutes)

```
┌─────────────────┐
│ Scheduler Fires │
└────────┬────────┘
         │
         ▼
┌─────────────────────┐
│ Scrape News Sources │
│ (Multi-threaded)    │
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│ Deduplicate         │
│ (SHA-256 hash)      │
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│ Save to MongoDB     │
│ Publish to RabbitMQ │
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│ Check Risk Score    │
│ (threshold: 85)     │
└────────┬────────────┘
         │
         ├─── > 85 ───▶ Write Webhook Alert
         │
         └─── ≤ 85 ───▶ Continue
```

### 2. Event Processing Pipeline

```
RabbitMQ Queue → Intelligence API → LLM Extraction → 
Event Validation → MongoDB + RabbitMQ → Predictor Service
```

### 3. Risk Calculation Pipeline

```
RabbitMQ Queue → Join Economic Data → Calculate Risk Score →
Generate GeoJSON → MongoDB + RabbitMQ → UI Dashboard
```

### 4. UI Update Cycle

```
┌─────────────────────────────────────────┐
│ Polling Intervals                       │
├─────────────────────────────────────────┤
│ • Scheduler Status: 10 seconds          │
│ • High-Risk Alerts: 5 seconds           │
│ • Risk Signals: 5 seconds               │
│ • Trend Data: 5 seconds                 │
└─────────────────────────────────────────┘
```

---

## State Management

### Shared Volume (`/data`)

All services mount the same Docker volume for coordination:

```
/data/
├── automation_logs.json      # Execution history (last 100)
├── high_risk_alerts.json     # Critical alerts (last 20)
├── risk_signals.json         # Current risk data
├── parsed_events.json        # Extracted events
└── raw_news.json             # Scraped articles
```

### MongoDB Collections

```
nextier_signal/
├── raw_articles              # Scraped news articles
├── parsed_events             # LLM-extracted events
├── risk_signals              # Calculated risk scores
└── economic_data             # Economic indicators
```

### RabbitMQ Queues

```
scraped_articles  → Intelligence API
parsed_events     → Predictor Service
risk_signals      → UI Dashboard
```

---

## Key APIs for Demo

### 1. Scheduler Status
```bash
GET http://localhost:8000/api/v1/scheduler/status

Response:
{
  "status": "active",
  "scheduler_running": true,
  "last_run": "2026-01-11T09:15:00Z",
  "next_run": "2026-01-11T09:30:00Z",
  "schedule": "Every 15 minutes"
}
```

### 2. Automation Logs
```bash
GET http://localhost:8000/api/v1/automation/logs?limit=10

Response:
{
  "logs": [
    {
      "timestamp": "2026-01-11T09:15:00Z",
      "event_type": "scheduled_scrape",
      "status": "success",
      "details": {
        "articles_count": 45,
        "high_risk_count": 3,
        "duration_seconds": 12.5
      }
    }
  ]
}
```

### 3. Risk Signals
```bash
GET http://localhost:8002/api/v1/signals

Response: GeoJSON with risk scores
```

---

## Demo Walkthrough

### 1. System Startup
```bash
docker-compose up -d
```

**Show**:
- Services starting in Docker logs
- Scheduler initialization message
- First automated scrape execution

### 2. System Heartbeat
**Navigate to**: `http://localhost:8080`

**Point out**:
- Green "System Active" indicator
- Next scrape countdown timer
- Last sync timestamp
- Schedule information (Every 15 minutes)

### 3. Live Heatmap
**Show**:
- Interactive map with risk markers
- Color-coded severity (Red = Critical, Orange = High)
- Click marker to see event details
- Layer toggles for additional data

### 4. Automated Scraping Cycle
**Wait for next 15-minute mark**:
- Countdown timer reaches zero
- System automatically scrapes
- New articles appear in dashboard
- KPI cards update in real-time

### 5. High-Risk Alert
**Trigger**: Manually create high-risk article or wait for detection

**Show**:
- Toast notification appears instantly
- Alert shows article title and risk score
- No manual refresh needed
- Alert auto-dismisses after 10 seconds

### 6. Automation Logs
```bash
curl http://localhost:8000/api/v1/automation/logs
```

**Show**:
- Historical execution data
- Success/failure rates
- Article counts per cycle
- Duration metrics

---

## Technical Highlights

### Automation
- ✅ Zero manual intervention
- ✅ Runs 24/7 without supervision
- ✅ Self-healing with retry logic
- ✅ Comprehensive audit trail

### Real-Time Intelligence
- ✅ 15-minute data freshness
- ✅ Instant high-risk alerts
- ✅ Live dashboard updates
- ✅ Continuous monitoring

### Scalability
- ✅ Microservices architecture
- ✅ Horizontal scaling ready
- ✅ Message queue load balancing
- ✅ Connection pooling

### Resilience
- ✅ Circuit breakers for external services
- ✅ Exponential backoff retry
- ✅ Graceful degradation
- ✅ Health check monitoring

### Observability
- ✅ Structured JSON logging
- ✅ Correlation IDs for tracing
- ✅ Performance metrics
- ✅ Automation logs

---

## Demo Talking Points

### Problem Statement
"Traditional conflict monitoring requires manual data collection and analysis, leading to delayed responses and missed early warning signals."

### Solution
"NNVCD automates the entire pipeline - from news scraping to risk assessment - providing real-time intelligence with instant alerts for critical situations."

### Key Differentiators
1. **Fully Automated**: Runs every 15 minutes without human intervention
2. **AI-Powered**: LLM extracts structured events from unstructured news
3. **Instant Alerts**: High-risk situations trigger immediate notifications
4. **Proactive Monitoring**: Continuous surveillance vs reactive analysis
5. **Geospatial Intelligence**: Interactive map visualization of risk distribution

### Business Impact
- **Faster Response**: 15-minute intelligence cycle vs hours/days
- **Reduced Costs**: Automation eliminates manual monitoring overhead
- **Better Coverage**: Multi-source scraping ensures comprehensive data
- **Early Warning**: Instant alerts enable proactive intervention
- **Data-Driven**: Economic indicators enhance risk assessment accuracy

---

## System Requirements

### Minimum
- Docker 20.10+
- Docker Compose 2.0+
- 4GB RAM
- 2 CPU cores
- 10GB disk space

### Recommended
- 8GB RAM
- 4 CPU cores
- 20GB disk space
- SSD storage

---

## Quick Start for Demo

```bash
# Clone repository
git clone https://github.com/Ejyke90/nextier-nigeria-violent-conflicts-database.git
cd nextier-nigeria-violent-conflicts-database

# Start all services
docker-compose up -d

# Verify scheduler is running
curl http://localhost:8000/api/v1/scheduler/status

# Open dashboard
open http://localhost:8080

# Monitor logs
docker-compose logs -f scraper
```

---

## Future Enhancements

### Short-Term
- Email/Slack notifications for critical alerts
- Configurable risk thresholds
- Historical trend analysis
- Export reports (PDF/CSV)

### Long-Term
- Predictive risk modeling with ML
- Sentiment analysis integration
- Multi-language support
- Mobile app for field teams
- Integration with external alert systems

---

## Conclusion

NNVCD represents a paradigm shift from reactive to **proactive conflict monitoring**. By automating the entire intelligence pipeline and providing instant alerts, the system enables faster response times and better situational awareness for conflict prevention and management.

**Key Takeaway**: "Set it and forget it" - The system runs autonomously 24/7, providing continuous intelligence without manual intervention.
