# 🎯 TWO-STEP DEMO WORKFLOW

## The Problem We Solved
Docker Desktop has a timing issue where it reports as "running" but the daemon isn't fully ready. This causes connection failures when starting services.

## ✅ The Solution: Two-Script Approach

Split the process into two reliable steps:
1. **Prep** - Get Docker ready (do this early)
2. **Run** - Start services (do this when ready to demo)

---

## 📋 Step 1: Preparation (Run 15-30 min before demo)

```bash
./demo-prep.sh
```

**What it does:**
- ✅ Starts Docker Desktop
- ✅ Waits for Docker to be fully operational
- ✅ Builds React UI locally (with all your latest changes!)
- ✅ Builds/verifies all Docker images
- ✅ Pulls base images (MongoDB, RabbitMQ)
- ✅ Cleans up old containers

**Time:** 5-10 minutes (first time), 2-3 minutes (subsequent)

**When to run:**
- 15-30 minutes before your demo
- After making code changes
- First time setup

---

## 🚀 Step 2: Start Demo (Run when ready to present)

```bash
./demo-run.sh
```

**What it does:**
- ✅ Verifies Docker is running
- ✅ Cleans up ports
- ✅ Starts MongoDB & RabbitMQ
- ✅ Starts all backend services
- ✅ Starts UI Dashboard
- ✅ Verifies all services are healthy

**Time:** ~2 minutes

**When to run:**
- Right before you start presenting
- When you need to restart services
- After stopping services with `docker compose down`

---

## 🎬 Demo Day Workflow

### Morning of Demo (or 30 min before):
```bash
./demo-prep.sh
```
☕ Take a break while it prepares everything

### Right Before Demo:
```bash
./demo-run.sh
```
⏱️ Wait 2 minutes, then open: **http://localhost:8080/**

### During Demo:
- Everything is running and stable
- Use the dashboard at http://localhost:8080/
- Show API docs at /docs endpoints if needed

### After Demo:
```bash
docker compose down
```

---

## 🔧 Quick Reference

| Command | Purpose | When to Use |
|---------|---------|-------------|
| `./demo-prep.sh` | Prepare Docker & images | Before demo (once) |
| `./demo-run.sh` | Start all services | When ready to demo |
| `docker compose down` | Stop everything | After demo |
| `docker compose logs -f` | View logs | Troubleshooting |
| `docker compose ps` | Check status | Verify services |

---

## 💡 Options

### demo-prep.sh Options:
```bash
./demo-prep.sh              # Full preparation with build
./demo-prep.sh --skip-build # Skip build if images exist
```

### demo-run.sh Options:
```bash
./demo-run.sh        # Start services
./demo-run.sh --logs # Start and show logs
```

---

## 🆘 Troubleshooting

### If demo-prep.sh fails:
1. Manually open Docker Desktop
2. Wait 60 seconds for it to fully start
3. Run `./demo-prep.sh --skip-build`

### If demo-run.sh fails:
1. Check Docker is running: `docker ps`
2. If not, run `./demo-prep.sh` again
3. Then run `./demo-run.sh`

### If services won't start:
```bash
# Full reset
docker compose down -v
./demo-prep.sh
./demo-run.sh
```

### If a specific service fails:
```bash
# Check logs
docker compose logs <service-name>

# Restart specific service
docker compose restart <service-name>
```

---

## 🎯 Why Two Scripts?

**Problem:** Docker Desktop's daemon takes time to fully initialize, causing race conditions.

**Solution:** 
- **demo-prep.sh** - Handles the slow, unpredictable Docker startup
- **demo-run.sh** - Fast, reliable service startup (assumes Docker ready)

**Benefits:**
- ✅ More reliable startup
- ✅ Faster when you need to restart
- ✅ Clear separation of concerns
- ✅ Better error handling
- ✅ Can prep early, run when ready

---

## 📊 What Gets Started

Both scripts work together to start:

1. **MongoDB** (Port 27017) - Database
2. **RabbitMQ** (Port 5672, 15672) - Message Queue  
3. **Scraper** (Port 8000) - Data Collection API
4. **Intelligence API** (Port 8001) - Event Analysis
5. **Predictor** (Port 8002) - Risk Prediction
6. **UI Dashboard** (Port 8080) - Main Interface

---

## ✅ Pre-Demo Checklist

- [ ] Run `./demo-prep.sh` (15-30 min before)
- [ ] Verify Docker Desktop is running (check menu bar)
- [ ] Run `./demo-run.sh` (right before demo)
- [ ] Open http://localhost:8080/ and verify it loads
- [ ] Test key features you'll demonstrate
- [ ] Keep terminal open for quick access to logs

---

## 🎪 Demo Presentation Tips

1. **Prep Early:** Run `demo-prep.sh` well before your demo
2. **Keep Docker Running:** Don't close Docker Desktop
3. **Quick Start:** Run `demo-run.sh` takes only 2 minutes
4. **Bookmark URL:** Have http://localhost:8080/ ready
5. **Know the Logs:** `docker compose logs -f` if needed
6. **Emergency Restart:** `docker compose restart` is your friend

---

## 🔄 Comparison with Old Script

| Feature | demo-start.sh (old) | demo-prep.sh + demo-run.sh (new) |
|---------|---------------------|----------------------------------|
| **Reliability** | ⚠️ Timing issues | ✅ Very reliable |
| **Speed** | 2-5 minutes | Prep: 5-10 min, Run: 2 min |
| **Flexibility** | Limited | ✅ Can prep early |
| **Error Handling** | Good | ✅ Excellent |
| **Demo Ready** | Sometimes | ✅ Always |

---

## 🚀 Quick Start Summary

```bash
# BEFORE DEMO (once)
./demo-prep.sh

# WHEN READY TO DEMO
./demo-run.sh

# OPEN BROWSER
http://localhost:8080/

# AFTER DEMO
docker compose down
```

**That's it! Two simple commands for a reliable demo.**
