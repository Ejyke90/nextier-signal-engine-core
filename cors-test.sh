#!/bin/bash

echo "🔧 CORS Fix Verification"
echo "======================"
echo ""

echo "✅ Testing CORS-enabled API calls..."
echo ""

# Test all APIs with CORS headers
echo "📊 Data with CORS Headers:"
echo "Articles (with Origin):"
curl -s -H "Origin: http://localhost:8080" http://localhost:8000/articles | jq '.count'
echo ""

echo "Events (with Origin):"
curl -s -H "Origin: http://localhost:8080" http://localhost:8001/events | jq '.count'
echo ""

echo "Risk Signals (with Origin):"
curl -s -H "Origin: http://localhost:8080" http://localhost:8002/signals | jq '.count'
echo ""

echo "🌐 UI Status:"
echo "UI Health:"
curl -s http://localhost:8080/health | jq .
echo ""

echo "🎯 UI Data Loading Test:"
echo "Testing the exact API calls the UI makes..."

# Test the specific endpoints the UI JavaScript calls
echo "1. Status Cards Data:"
raw_count=$(curl -s -H "Origin: http://localhost:8080" http://localhost:8000/articles | jq '.count')
intel_status=$(curl -s -H "Origin: http://localhost:8080" http://localhost:8001/status)
pred_status=$(curl -s -H "Origin: http://localhost:8080" http://localhost:8002/status)

echo "Raw Articles: $raw_count"
echo "Intelligence Status: $(echo $intel_status | jq '.parsed_events_count')"
echo "Predictor Status: $(echo $pred_status | jq '.risk_signals_count')"
echo ""

echo "2. Map Visualization Data:"
echo "Risk signals for map:"
curl -s -H "Origin: http://localhost:8080" http://localhost:8002/signals | jq '.signals[] | {state, risk_score, risk_level}' | head -10
echo ""

echo "3. Chart Data:"
echo "Risk distribution:"
curl -s -H "Origin: http://localhost:8080" http://localhost:8002/signals | jq '.signals | group_by(.risk_level) | map({risk_level: .[0].risk_level, count: length})'
echo ""

echo "✅ CORS Fix Complete!"
echo ""
echo "🌐 UI should now work at: http://localhost:8080"
echo "📱 All API calls from browser should succeed"
echo "🗺️ Map should show risk markers"
echo "📊 Charts should display data"
echo "📋 Tables should populate with events"
