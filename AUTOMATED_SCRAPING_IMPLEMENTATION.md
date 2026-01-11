# Automated Background Scraping Implementation

## Overview
The NNVCD has been transformed from a reactive (button-click) system to a proactive (automated) system with background task scheduling, instant alerts, and comprehensive monitoring.

## Implementation Summary

### 1. Background Scheduler (✅ Completed)

**File**: `scraper/services/scheduler.py`

- **Technology**: APScheduler with BackgroundScheduler
- **Schedule**: Every 15 minutes (Cron: `*/15 * * * *`)
- **Features**:
  - Automatic scraping from multiple news sources
  - MongoDB persistence
  - RabbitMQ message publishing
  - High-risk article detection (risk_score > 85)
  - Webhook notifications for critical alerts
  - Automation logging to `/data/automation_logs.json`

**Key Components**:
```python
class AutomationScheduler:
    - _scrape_job(): Async scraping job
    - _trigger_high_risk_webhook(): Alert system for critical articles
    - _log_automation_event(): System health tracking
    - start(): Initialize scheduler with 15-min cron trigger
    - get_status(): Return scheduler status for UI
```

**Integration**: Automatically starts with FastAPI application lifecycle in `scraper/main.py`

### 2. UI System Heartbeat (✅ Completed)

**File**: `ui/src/components/SystemHeartbeat.jsx`

**Replaced**: Manual "Scrape" button in CompactControlPanel

**Features**:
- Real-time scheduler status indicator
- Next scheduled scrape countdown timer
- Last successful sync timestamp
- Schedule information display (Every 15 minutes)
- Auto-refresh every 10 seconds

**API Endpoint**: `GET /api/v1/scheduler/status`

**Visual Indicators**:
- 🟢 Green: System Active
- 🟡 Yellow: System Inactive
- 🔴 Red: Scheduler Offline

### 3. High-Risk Webhook Notifications (✅ Completed)

**File**: `ui/src/components/HighRiskAlertMonitor.jsx`

**Trigger**: Articles with `risk_score > 85`

**Features**:
- Instant toast notifications for critical articles
- Polls `/data/high_risk_alerts.json` every 5 seconds
- Deduplication to prevent repeated alerts
- 10-second display duration
- Shows article count and title

**Backend Integration**:
- Scheduler detects high-risk articles during automated scraping
- Writes alerts to `/data/high_risk_alerts.json`
- Keeps last 20 alerts in memory

### 4. Automation Logs & State Management (✅ Completed)

**Log File**: `/data/automation_logs.json`

**Tracked Events**:
- `scheduled_scrape`: Automated scraping job execution
- `scheduler_start`: Scheduler initialization
- `scheduler_stop`: Scheduler shutdown

**Log Entry Structure**:
```json
{
  "timestamp": "2026-01-11T09:28:00.000Z",
  "event_type": "scheduled_scrape",
  "status": "success",
  "details": {
    "articles_count": 45,
    "high_risk_count": 3,
    "duration_seconds": 12.5,
    "db_success": true,
    "mq_success": true
  }
}
```

**API Endpoint**: `GET /api/v1/automation/logs?limit=20`

**State Management**:
- Shared `/data` volume across all Docker containers
- File-based state for cross-service communication
- Automatic cleanup (keeps last 100 log entries)

## Architecture Changes

### Before (Reactive)
```
User clicks "Scrape" → API call → Scraping → Manual refresh
```

### After (Proactive)
```
Scheduler (15 min) → Auto-scrape → MongoDB + RabbitMQ → UI auto-updates
                   ↓
            High-risk detection → Webhook → Instant toast alert
```

## Configuration

### Dependencies Added
- `apscheduler==3.10.4` in `scraper/requirements.txt`

### Docker Volumes
All services have access to `/data` volume for state sharing:
```yaml
volumes:
  - ./data:/data
```

### Environment Variables
No new environment variables required. Uses existing configuration.

## API Endpoints

### 1. Scheduler Status
```
GET /api/v1/scheduler/status
```
**Response**:
```json
{
  "status": "active",
  "scheduler_running": true,
  "job_running": false,
  "last_run": "2026-01-11T09:15:00.000Z",
  "next_run": "2026-01-11T09:30:00.000Z",
  "schedule": "Every 15 minutes (*/15 * * * *)"
}
```

### 2. Automation Logs
```
GET /api/v1/automation/logs?limit=20
```
**Response**:
```json
{
  "logs": [...],
  "total_count": 45
}
```

## Testing & Verification

### 1. Verify Scheduler is Running
```bash
curl http://localhost:8000/api/v1/scheduler/status
```

### 2. Check Automation Logs
```bash
curl http://localhost:8000/api/v1/automation/logs
```

### 3. Monitor High-Risk Alerts
```bash
cat data/high_risk_alerts.json
```

### 4. UI Verification
- Open dashboard at `http://localhost:8080`
- Check bottom control panel for System Heartbeat indicator
- Verify "Next Scrape" countdown timer
- Wait for automated scraping cycle (max 15 minutes)
- Observe toast notifications for high-risk articles

## Deployment Instructions

### 1. Install Dependencies
```bash
cd scraper
pip install -r requirements.txt
```

### 2. Start Services
```bash
docker-compose up -d
```

### 3. Verify Scheduler
```bash
docker logs scraper-service | grep "Automation scheduler started"
```

### 4. Monitor Logs
```bash
# Real-time logs
docker logs -f scraper-service

# Automation logs
cat data/automation_logs.json | jq '.'
```

## Monitoring & Observability

### System Health Indicators
1. **Scheduler Status**: Green indicator in UI
2. **Last Sync Time**: Shows successful execution
3. **Next Scrape Timer**: Countdown to next run
4. **Automation Logs**: Historical execution data

### Alert Thresholds
- **High-Risk**: `risk_score > 85` triggers instant webhook
- **Critical**: Articles flagged for immediate attention

### Log Retention
- Automation logs: Last 100 entries
- High-risk alerts: Last 20 alerts
- Automatic cleanup to prevent disk bloat

## Troubleshooting

### Scheduler Not Starting
```bash
# Check logs
docker logs scraper-service | grep -i scheduler

# Verify APScheduler installation
docker exec scraper-service pip list | grep apscheduler
```

### No Automation Logs
```bash
# Check data directory permissions
ls -la data/

# Manually create log file
echo '[]' > data/automation_logs.json
```

### High-Risk Alerts Not Showing
```bash
# Verify alert file exists
cat data/high_risk_alerts.json

# Check UI console for errors
# Open browser DevTools → Console
```

## Performance Considerations

### Resource Usage
- **CPU**: Minimal (scheduler runs in background thread)
- **Memory**: ~50MB additional for APScheduler
- **Disk**: ~1MB for logs (with cleanup)

### Scalability
- Scheduler uses single instance (max_instances=1)
- Prevents duplicate scraping jobs
- Thread-safe execution with asyncio

### Network Impact
- Scraping respects rate limits (semaphore-controlled)
- 15-minute interval prevents IP blacklisting
- Graceful error handling for failed sources

## Future Enhancements

### Potential Improvements
1. **Dynamic Scheduling**: Adjust frequency based on activity
2. **Email Notifications**: Send alerts for critical events
3. **Slack/Discord Integration**: Real-time team notifications
4. **Dashboard Analytics**: Scraping success rate charts
5. **Manual Trigger**: Admin override for immediate scraping
6. **Configurable Thresholds**: User-defined risk score alerts

## Security Considerations

### Access Control
- Scheduler runs within Docker container
- No external API exposure for scheduler control
- Read-only access to automation logs via API

### Data Privacy
- Logs contain metadata only (no sensitive content)
- High-risk alerts show titles only (no full content)
- Automatic log rotation prevents data accumulation

## Compliance & Audit Trail

### Audit Logging
- All automated scraping jobs logged with timestamps
- Success/failure status tracked
- Article counts and durations recorded
- System start/stop events captured

### Traceability
- Each log entry has unique timestamp
- Event types clearly categorized
- Full execution details preserved

## Conclusion

The NNVCD is now a fully automated, proactive conflict monitoring system that:
- ✅ Scrapes news sources every 15 minutes automatically
- ✅ Detects and alerts on high-risk articles instantly
- ✅ Provides real-time system health monitoring
- ✅ Maintains comprehensive audit logs
- ✅ Eliminates manual intervention requirements

The system is production-ready and requires no manual scraping actions from users.
