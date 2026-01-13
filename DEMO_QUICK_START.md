# 🎯 DEMO QUICK START GUIDE

## For Your Demo Tomorrow

### ⚡ Quick Start (Recommended for Demo)

```bash
./demo-start.sh --skip-build
```

This will:
- ✅ Check Docker is running (auto-start if needed)
- ✅ Clean up ports and stop old containers
- ✅ Start MongoDB & RabbitMQ
- ✅ Start all backend services (Scraper, Intelligence API, Predictor)
- ✅ Start UI Dashboard
- ✅ Verify all services are healthy

**Startup Time:** ~2-3 minutes (without rebuild)

---

## 🚀 All Available Startup Options

### 1. **Full Production Startup** (First Time)
```bash
./demo-start.sh
```
Builds Docker images and starts everything. Takes 5-10 minutes.

### 2. **Quick Demo Startup** (Recommended)
```bash
./demo-start.sh --skip-build
```
Skips rebuild, starts in 2-3 minutes. Perfect for demos!

### 3. **Development Mode**
```bash
./demo-start.sh --dev
```
Starts backend in Docker, UI with Vite hot-reload on port 5173.

### 4. **With Live Logs**
```bash
./demo-start.sh --skip-build --logs
```
Shows live logs after startup (Ctrl+C to exit logs).

---

## 🌐 Access Points After Startup

### Main Dashboard
- **Production:** http://localhost:8080/
- **Development:** http://localhost:5173/

### Backend APIs
- **Scraper API:** http://localhost:8000/docs
- **Intelligence API:** http://localhost:8001/docs
- **Predictor API:** http://localhost:8002/docs

### Infrastructure
- **RabbitMQ Management:** http://localhost:15672/ (admin/password)
- **MongoDB:** mongodb://localhost:27017/

---

## 🛠️ Useful Commands During Demo

### Check Service Status
```bash
docker compose ps
```

### View Logs
```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f scraper
docker compose logs -f intelligence-api
docker compose logs -f predictor
docker compose logs -f ui
```

### Restart a Service
```bash
docker compose restart scraper
docker compose restart intelligence-api
docker compose restart predictor
docker compose restart ui
```

### Stop Everything
```bash
docker compose down
```

### Quick Restart
```bash
docker compose restart
```

---

## 🔧 Troubleshooting

### If Docker isn't running:
```bash
# macOS
open -a Docker

# Linux
sudo systemctl start docker
```

### If ports are busy:
```bash
# The script handles this automatically, but manually:
lsof -ti:8000 | xargs kill -9  # Scraper
lsof -ti:8001 | xargs kill -9  # Intelligence API
lsof -ti:8002 | xargs kill -9  # Predictor
lsof -ti:8080 | xargs kill -9  # UI
```

### If a service won't start:
```bash
# Check logs
docker compose logs <service-name>

# Rebuild specific service
docker compose build <service-name>
docker compose up -d <service-name>
```

### Complete Reset
```bash
docker compose down -v  # Removes volumes too
./demo-start.sh         # Fresh start
```

---

## 📋 Pre-Demo Checklist

- [ ] Docker Desktop is installed and running
- [ ] Run `./demo-start.sh --skip-build` at least once before demo
- [ ] Verify all services are green at http://localhost:8080/
- [ ] Test key features you'll demonstrate
- [ ] Have http://localhost:8080/ bookmarked
- [ ] Keep this guide open for quick reference

---

## 🎬 Demo Day Workflow

### 30 Minutes Before Demo:
```bash
./demo-start.sh --skip-build
```

### During Demo:
- Open http://localhost:8080/ in your browser
- All backend services are running and ready
- Use API docs at /docs endpoints if needed

### After Demo:
```bash
docker compose down  # Clean shutdown
```

---

## 📊 What Each Service Does

| Service | Port | Purpose |
|---------|------|---------|
| **Scraper** | 8000 | Collects conflict data from news sources |
| **Intelligence API** | 8001 | Processes and analyzes conflict events |
| **Predictor** | 8002 | Generates risk predictions and signals |
| **UI Dashboard** | 8080 | Main visualization and interaction interface |
| **MongoDB** | 27017 | Database for all conflict data |
| **RabbitMQ** | 5672 | Message queue for service communication |

---

## 🆘 Emergency Commands

### Service won't respond:
```bash
docker compose restart <service-name>
```

### Everything is broken:
```bash
docker compose down
./demo-start.sh
```

### Need to see what's happening:
```bash
docker compose logs -f --tail=100
```

---

## 💡 Pro Tips for Demo

1. **Start early:** Run the startup script 30 minutes before your demo
2. **Test first:** Open the dashboard and click around to ensure everything works
3. **Keep terminal open:** In case you need to check logs quickly
4. **Bookmark URLs:** Have all service URLs ready in your browser
5. **Know the reset:** `docker compose restart` is your friend

---

## 📞 Quick Reference Card

```
START:    ./demo-start.sh --skip-build
STATUS:   docker compose ps
LOGS:     docker compose logs -f
RESTART:  docker compose restart
STOP:     docker compose down
DASHBOARD: http://localhost:8080/
```

---

**Good luck with your demo! 🚀**
