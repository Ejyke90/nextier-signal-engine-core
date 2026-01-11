#!/bin/bash

echo "🚀 Nextier Signal Engine - Complete System Test"
echo "=============================================="
echo ""

# Check all services
echo "🏥 Checking service health..."
echo "Scraper Health:"
curl -s http://localhost:8000/health | jq .
echo ""
echo "Intelligence API Health:"
curl -s http://localhost:8001/health | jq .
echo ""
echo "Predictor Health:"
curl -s http://localhost:8002/health | jq .
echo ""
echo "UI Health:"
curl -s http://localhost:8080/health | jq .
echo ""

# Test complete pipeline
echo "🔄 Testing complete pipeline..."
echo ""

echo "1️⃣ Triggering scraping..."
curl -s http://localhost:8000/scrape | jq .
echo ""

echo "2️⃣ Triggering analysis..."
curl -s http://localhost:8001/analyze | jq .
echo ""

echo "3️⃣ Triggering risk prediction..."
curl -s http://localhost:8002/predict | jq .
echo ""

echo "⏳ Waiting for processing to complete..."
sleep 10

echo ""
echo "📊 Final System Status:"
echo "======================"
echo "Scraper Status:"
curl -s http://localhost:8000/articles | jq '.count'
echo ""
echo "Intelligence API Status:"
curl -s http://localhost:8001/status | jq .
echo ""
echo "Predictor Status:"
curl -s http://localhost:8002/status | jq .
echo ""

echo ""
echo "🎯 Risk Signals Generated:"
curl -s http://localhost:8002/signals | jq .
echo ""

echo ""
echo "🌐 UI Access:"
echo "============"
echo "Main Dashboard: http://localhost:8080"
echo ""
echo "🔗 API Endpoints:"
echo "Scraper: http://localhost:8000"
echo "Intelligence: http://localhost:8001"
echo "Predictor: http://localhost:8002"
echo "UI: http://localhost:8080"
echo ""

echo "📋 Quick Test Commands:"
echo "======================"
echo "# Test individual services"
echo "curl http://localhost:8000/health"
echo "curl http://localhost:8001/health"
echo "curl http://localhost:8002/health"
echo "curl http://localhost:8080/health"
echo ""
echo "# Trigger pipeline"
echo "curl http://localhost:8000/scrape"
echo "curl http://localhost:8001/analyze"
echo "curl http://localhost:8002/predict"
echo ""
echo "# View results"
echo "curl http://localhost:8000/articles"
echo "curl http://localhost:8001/events"
echo "curl http://localhost:8002/signals"
echo ""
echo "🛑 To stop all services:"
echo "docker compose down"
echo ""
echo "📝 To view logs:"
echo "docker compose logs -f"
echo ""
echo "🎮 READY FOR DEMO! Open http://localhost:8080 in your browser"
