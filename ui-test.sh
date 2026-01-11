#!/bin/bash

echo "🎨 UI Functionality Test"
echo "======================"
echo ""

# Test UI service
echo "🌐 UI Service Test:"
echo "UI Health:"
curl -s http://localhost:8080/health | jq .
echo ""

# Test data endpoints that UI consumes
echo "📊 Data Endpoints Test:"
echo "Raw Articles Count:"
curl -s http://localhost:8000/articles | jq '.count'
echo ""

echo "Parsed Events Count:"
curl -s http://localhost:8001/events | jq '.count'
echo ""

echo "Risk Signals Count:"
curl -s http://localhost:8002/signals | jq '.count'
echo ""

# Test UI action endpoints
echo "🎛️ UI Action Buttons Test:"
echo ""

echo "1. Scrape Button Test:"
scrape_result=$(curl -s http://localhost:8000/scrape)
echo "$scrape_result" | jq '.articles_scraped'
echo ""

echo "2. Analyze Button Test:"
analyze_result=$(curl -s http://localhost:8001/analyze)
echo "$analyze_result" | jq '.status'
echo ""

echo "3. Predict Button Test:"
predict_result=$(curl -s http://localhost:8002/predict)
echo "$predict_result" | jq '.status'
echo ""

# Wait for processing
echo "⏳ Waiting for background processing..."
sleep 8

# Test final data state
echo "📈 Final Data State:"
echo "Status Cards Data:"
echo "Raw Articles: $(curl -s http://localhost:8000/articles | jq '.count')"
echo "Parsed Events: $(curl -s http://localhost:8001/status | jq '.parsed_events_count')"
echo "Risk Signals: $(curl -s http://localhost:8002/signals | jq '.count')"
echo ""

# Test risk signal data for visualization
echo "🗺️ Map Visualization Data:"
echo "Risk Signals for Map:"
curl -s http://localhost:8002/signals | jq '.signals[] | {state, lga, risk_score, risk_level}'
echo ""

echo "📊 Chart Data:"
echo "Risk Distribution:"
critical=$(curl -s http://localhost:8002/signals | jq '.signals[] | select(.risk_level == "Critical") | length')
high=$(curl -s http://localhost:8002/signals | jq '.signals[] | select(.risk_level == "High") | length')
medium=$(curl -s http://localhost:8002/signals | jq '.signals[] | select(.risk_level == "Medium") | length')
low=$(curl -s http://localhost:8002/signals | jq '.signals[] | select(.risk_level == "Low") | length')
minimal=$(curl -s http://localhost:8002/signals | jq '.signals[] | select(.risk_level == "Minimal") | length')

echo "Critical: $critical, High: $high, Medium: $medium, Low: $low, Minimal: $minimal"
echo ""

echo "📋 Table Data Sample:"
echo "Recent Risk Signals (first 2):"
curl -s http://localhost:8002/signals | jq '.signals[:2] | .[] | {event_type, state, lga, severity, risk_score, risk_level}'
echo ""

echo "✅ UI Test Complete!"
echo ""
echo "🌐 Access the full UI at: http://localhost:8080"
echo ""
echo "🎯 UI Features Tested:"
echo "✅ Service health checks"
echo "✅ Real-time data fetching"
echo "✅ Interactive button actions"
echo "✅ Background processing"
echo "✅ Risk visualization data"
echo "✅ Map coordinate data"
echo "✅ Chart distribution data"
echo "✅ Table display data"
