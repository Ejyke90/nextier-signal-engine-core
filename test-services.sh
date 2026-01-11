#!/bin/bash

echo "🚀 Starting Nextier Signal Engine Test Services"
echo "================================================"
echo ""

# Build and start test services
echo "📦 Building test services..."
docker compose -f docker-compose-test.yml build

echo ""
echo "🔄 Starting test services..."
docker compose -f docker-compose-test.yml up -d

echo ""
echo "⏳ Waiting for services to be ready..."
sleep 10

echo ""
echo "🏥 Testing health endpoints..."
echo "Scraper Test Health:"
curl -s http://localhost:8010/health | jq .
echo ""
echo "Intelligence API Test Health:"
curl -s http://localhost:8011/health | jq .

echo ""
echo "🕷️ Testing scraper..."
echo "Triggering scrape:"
curl -s http://localhost:8010/scrape | jq .

echo ""
echo "📊 Checking scraped articles:"
curl -s http://localhost:8010/articles | jq .

echo ""
echo "🧠 Testing intelligence API status:"
curl -s http://localhost:8011/status | jq .

echo ""
echo "🔍 Triggering analysis:"
curl -s http://localhost:8011/analyze | jq .

echo ""
echo "⏳ Waiting for analysis to complete..."
sleep 15

echo ""
echo "📈 Checking parsed events:"
curl -s http://localhost:8011/events | jq .

echo ""
echo "📋 Final status:"
curl -s http://localhost:8011/status | jq .

echo ""
echo "🗂️  Checking data files:"
echo "Raw news file:"
ls -la data-test/raw_news.json 2>/dev/null || echo "  Not found"
echo "Parsed events file:"
ls -la data-test/parsed_events.json 2>/dev/null || echo "  Not found"

echo ""
echo "🎯 Test Commands for Manual Testing:"
echo "===================================="
echo "Scraper Test (Port 8010):"
echo "  Health: curl http://localhost:8010/health"
echo "  Scrape: curl http://localhost:8010/scrape"
echo "  Articles: curl http://localhost:8010/articles"
echo ""
echo "Intelligence API Test (Port 8011):"
echo "  Health: curl http://localhost:8011/health"
echo "  Status: curl http://localhost:8011/status"
echo "  Analyze: curl http://localhost:8011/analyze"
echo "  Events: curl http://localhost:8011/events"
echo ""
echo "🛑 To stop test services:"
echo "  docker compose -f docker-compose-test.yml down"
echo ""
echo "📝 To view logs:"
echo "  docker compose -f docker-compose-test.yml logs -f"
echo ""
echo "🔍 To view specific service logs:"
echo "  docker compose -f docker-compose-test.yml logs scraper-test"
echo "  docker compose -f docker-compose-test.yml logs intelligence-api-test"
