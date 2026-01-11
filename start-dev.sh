#!/bin/bash

echo "🛑 Stopping all existing services..."
# Stop all Docker containers
docker compose down

echo "🧹 Killing any processes on development ports..."
# Kill processes on common development ports
lsof -ti:8080 | xargs kill -9 2>/dev/null
lsof -ti:8000 | xargs kill -9 2>/dev/null
lsof -ti:8001 | xargs kill -9 2>/dev/null
lsof -ti:8002 | xargs kill -9 2>/dev/null
lsof -ti:5173 | xargs kill -9 2>/dev/null
lsof -ti:5174 | xargs kill -9 2>/dev/null

echo "🚀 Starting infrastructure services..."
# Start MongoDB and RabbitMQ
docker compose up -d mongodb rabbitmq
sleep 5  # Wait for services to initialize

echo "🔄 Starting backend services..."
# Start backend services
docker compose up -d scraper intelligence-api predictor
sleep 5  # Wait for backends to initialize

echo "📦 Installing UI dependencies..."
# Navigate to UI directory and install dependencies
cd ui && npm install

echo "🌟 Starting UI in development mode..."
# Start UI in development mode
npm run dev

echo "✨ Development environment ready!"
echo "📊 Dashboard: http://localhost:5173"
echo "📡 Backend Services:"
echo "   - Scraper API: http://localhost:8000"
echo "   - Intelligence API: http://localhost:8001"
echo "   - Predictor API: http://localhost:8002"
echo "🔍 Monitoring:"
echo "   - RabbitMQ: http://localhost:15672"
echo "   - MongoDB: mongodb://localhost:27017"
