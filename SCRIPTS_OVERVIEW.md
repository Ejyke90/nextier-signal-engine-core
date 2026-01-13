# Scripts Overview

## 🎯 NEW: Master Demo Script (USE THIS FOR DEMO!)

### `demo-start.sh` ⭐ **RECOMMENDED FOR DEMO**
**Single command to start everything!**

```bash
./demo-start.sh --skip-build
```

**Features:**
- ✅ Auto-starts Docker Desktop if needed
- ✅ Cleans up ports automatically
- ✅ Starts all 6 services in correct order
- ✅ Verifies health of all services
- ✅ Beautiful colored output with progress
- ✅ Multiple modes (production, dev, with logs)
- ✅ Comprehensive error handling

**Startup Time:** 2-3 minutes (with --skip-build)

---

## 📋 Existing Scripts (Still Available)

### `start-services.sh`
Full production startup with Docker rebuild capability.
- Rebuilds Docker images
- Starts all services
- Includes health checks
- **Time:** 5-10 minutes

```bash
./start-services.sh
./start-services.sh --no-rebuild  # Skip rebuild
```

### `start-dev.sh`
Development mode with UI hot-reload.
- Starts backend in Docker
- Runs UI with Vite on port 5173
- Good for development work

```bash
./start-dev.sh
```

### `complete-test.sh`
Runs comprehensive test suite.

```bash
./complete-test.sh
```

### `cors-test.sh`
Tests CORS configuration.

```bash
./cors-test.sh
```

### `ui-test.sh`
Tests UI components.

```bash
./ui-test.sh
```

---

## 🆚 Comparison

| Feature | demo-start.sh | start-services.sh | start-dev.sh |
|---------|---------------|-------------------|--------------|
| **Auto Docker Start** | ✅ | ✅ | ❌ |
| **Port Cleanup** | ✅ | Optional | ✅ |
| **Health Verification** | ✅ | ✅ | ❌ |
| **Colored Output** | ✅ | ✅ | ❌ |
| **Multiple Modes** | ✅ | Limited | ❌ |
| **Dev Mode Support** | ✅ | ❌ | ✅ |
| **Quick Start** | ✅ (--skip-build) | ✅ (--no-rebuild) | ✅ |
| **Best For** | **Demos & Presentations** | Production deploys | Development |

---

## 🎬 For Your Demo Tomorrow

**Use this command:**
```bash
./demo-start.sh --skip-build
```

**Why?**
- Fastest startup (2-3 minutes)
- Most reliable
- Best error handling
- Clear visual feedback
- Auto-recovery features

**See:** `DEMO_QUICK_START.md` for complete demo guide

---

## 🔧 Service Architecture

All scripts start these services:

1. **MongoDB** (Port 27017) - Database
2. **RabbitMQ** (Port 5672, 15672) - Message Queue
3. **Scraper** (Port 8000) - Data Collection
4. **Intelligence API** (Port 8001) - Event Analysis
5. **Predictor** (Port 8002) - Risk Prediction
6. **UI Dashboard** (Port 8080 or 5173) - Visualization

---

## 📚 Additional Scripts

### Infrastructure
- `init-mongo.js` - MongoDB initialization
- `init-rabbitmq.sh` - RabbitMQ setup

### Testing
- `test-services.sh` - Service health tests
- `health-check.py` - Python health checker

### Utilities
- `scripts/build_nnvcd_brain.py` - Build vector database
- `scripts/setup_ai_agents.sh` - Configure AI agents

### Docker
- `docker-compose.yml` - Production configuration
- `docker-compose-test.yml` - Test configuration

---

## 💡 Quick Reference

```bash
# DEMO (Recommended)
./demo-start.sh --skip-build

# Development
./demo-start.sh --dev

# With Logs
./demo-start.sh --skip-build --logs

# Full Rebuild
./demo-start.sh

# Stop Everything
docker compose down

# Check Status
docker compose ps
```
