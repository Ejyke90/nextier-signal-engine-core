# NNVCD System Design - Key Themes & Patterns

## Core Design Philosophy

**Proactive over Reactive** - The system operates autonomously, eliminating manual intervention through automated background tasks and instant alerting.

## Key Architectural Themes

### 1. Automation-First Design
- **Background Scheduler**: APScheduler runs scraping every 15 minutes
- **Zero Manual Intervention**: No buttons to click, system runs continuously
- **Self-Healing**: Graceful error handling with automatic retry
- **Audit Trail**: All executions logged to `/data/automation_logs.json`

### 2. Event-Driven Communication
- **Message Queues**: RabbitMQ decouples services (articles → events → signals)
- **File-Based Webhooks**: High-risk alerts via shared `/data` volume
- **Async Processing**: Non-blocking I/O throughout the stack
- **State Polling**: UI polls for updates (5-10 second intervals)

### 3. Real-Time Intelligence
- **Instant Alerts**: Articles with risk_score > 85 trigger immediate notifications
- **System Heartbeat**: Live scheduler status with countdown timer
- **Continuous Monitoring**: Fresh intelligence every 15 minutes
- **Proactive Detection**: Automated risk assessment without user action

### 4. Clean Architecture Patterns
- **Layered Design**: API → Services → Repositories → Data
- **Dependency Injection**: Testable, modular components
- **Single Responsibility**: Each service has one clear purpose
- **Separation of Concerns**: Business logic isolated from infrastructure

### 5. Resilience & Observability
- **Circuit Breakers**: Protect against external service failures
- **Retry Mechanisms**: Exponential backoff for transient errors
- **Structured Logging**: JSON logs with correlation IDs
- **Health Checks**: Comprehensive dependency monitoring

## Service Archetypes

### Scraper Service - The Autonomous Collector
**Pattern**: Scheduled Background Worker
- Runs on cron trigger (`*/15 * * * *`)
- Detects high-risk articles automatically
- Writes webhooks for critical alerts
- Maintains execution history

### Intelligence API - The Event Extractor
**Pattern**: LLM-Powered Processor
- Consumes articles from message queue
- Extracts structured events via LLM
- Publishes events for downstream processing
- Circuit breaker protects LLM calls

### Predictor Service - The Risk Calculator
**Pattern**: Economic Data Analyzer
- Consumes events from message queue
- Calculates risk scores with economic indicators
- Publishes risk signals
- Caches expensive operations

### UI Dashboard - The Real-Time Monitor
**Pattern**: Polling-Based SPA
- System heartbeat shows scheduler status
- Polls for high-risk alerts (5s interval)
- Displays next scrape countdown
- Toast notifications for critical events

## Key Design Decisions

### Why APScheduler?
- Lightweight background task execution
- Cron-based scheduling (familiar syntax)
- Integrated with FastAPI lifecycle
- Single-instance execution (prevents duplicates)

### Why File-Based Webhooks?
- Simple cross-service communication
- No additional infrastructure required
- Shared Docker volume for state management
- Easy to debug and monitor

### Why 15-Minute Intervals?
- Balances freshness with rate limiting
- Prevents IP blacklisting from news sources
- Sufficient for conflict monitoring use case
- Reduces infrastructure costs

### Why Polling vs WebSockets?
- Simpler implementation and debugging
- No persistent connection management
- Works with static file serving
- Sufficient for 5-10 second update intervals

## Data Flow Patterns

### Automated Scraping Flow
```
Scheduler (15 min) → Scrape → Deduplicate → MongoDB + RabbitMQ
                              ↓
                    High-Risk Check (>85)
                              ↓
                    Webhook Alert → UI Toast
```

### Event Processing Flow
```
RabbitMQ Queue → LLM Extraction → Event Validation → MongoDB + RabbitMQ
```

### Risk Calculation Flow
```
RabbitMQ Queue → Economic Data Join → Risk Score → MongoDB + RabbitMQ
```

### UI Update Flow
```
Poll Scheduler Status (10s) → Display Heartbeat
Poll High-Risk Alerts (5s) → Show Toast Notification
Poll Risk Signals (5s) → Update Dashboard
```

## State Management Strategy

### Shared State via `/data` Volume
- `automation_logs.json` - Execution history (last 100 entries)
- `high_risk_alerts.json` - Critical alerts (last 20 entries)
- `risk_signals.json` - Current risk data
- All services mount same volume for coordination

### Database State (MongoDB)
- `raw_articles` - Scraped news articles
- `parsed_events` - LLM-extracted events
- `risk_signals` - Calculated risk scores
- `economic_data` - Economic indicators

### Message Queue State (RabbitMQ)
- `scraped_articles` - Pending article processing
- `parsed_events` - Pending risk calculation
- `risk_signals` - Pending downstream consumption

## Observability Patterns

### Automation Logging
```json
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
```

### Health Check Response
```json
{
  "status": "active",
  "scheduler_running": true,
  "last_run": "2026-01-11T09:15:00Z",
  "next_run": "2026-01-11T09:30:00Z",
  "schedule": "Every 15 minutes"
}
```

### High-Risk Alert Format
```json
{
  "timestamp": "2026-01-11T09:16:00Z",
  "alert_type": "high_risk_articles",
  "count": 3,
  "articles": [
    {
      "title": "Major conflict in...",
      "source": "Premium Times",
      "risk_score": 92
    }
  ]
}
```

## Security Considerations

### Automated System Security
- Scheduler runs within Docker container (isolated)
- No external API for scheduler control (read-only status)
- Automation logs contain metadata only (no sensitive data)
- File-based webhooks use shared volume (no network exposure)

### Input Validation
- Pydantic models validate all inputs
- Sanitized error messages prevent info leakage
- CORS restricted to specific origins

## Performance Characteristics

### Resource Usage
- **CPU**: Minimal (scheduler runs in background thread)
- **Memory**: ~50MB additional for APScheduler
- **Disk**: ~1MB for logs (with automatic cleanup)
- **Network**: Respects rate limits (semaphore-controlled)

### Scalability Limits
- Single scheduler instance (prevents duplicate jobs)
- Horizontal scaling for processing services
- Message queue handles load distribution
- File-based state limits to single-node deployment

## Future Evolution Patterns

### Potential Enhancements
- **Dynamic Scheduling**: Adjust frequency based on activity
- **WebSocket Notifications**: Replace polling for instant updates
- **Distributed Scheduler**: Multi-node coordination
- **ML-Based Alerting**: Predictive risk thresholds
- **Email/Slack Integration**: External notification channels

### Scalability Path
- Kubernetes for container orchestration
- Redis for distributed state management
- Kafka for high-throughput event streaming
- Elasticsearch for log aggregation

## Summary

The NNVCD system embodies a **proactive, automated** architecture where:
- **Automation replaces manual actions** (15-min scheduler)
- **Events drive communication** (RabbitMQ + file webhooks)
- **Real-time intelligence is continuous** (instant alerts)
- **Clean architecture ensures maintainability** (layered design)
- **Resilience is built-in** (circuit breakers, retries)

This design eliminates operational overhead while providing continuous, real-time conflict monitoring with instant alerting for critical situations.
