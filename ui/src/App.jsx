import { useState, useEffect } from 'react'
import SimpleHeatmap from './components/SimpleHeatmap'
import LiveSignalTicker from './components/LiveSignalTicker'
import KPICards from './components/KPICards'
import RiskDistributionCharts from './components/RiskDistributionCharts'
import CompactControlPanel from './components/CompactControlPanel'
import './App.css'

function App() {
  const [riskSignals, setRiskSignals] = useState([])
  const [mapInstance, setMapInstance] = useState(null)
  const [loading, setLoading] = useState(true)
  const [trendData, setTrendData] = useState([])
  const [simulationParams, setSimulationParams] = useState({
    fuel_price_index: 50,
    inflation_rate: 50,
    chatter_intensity: 50
  })

  useEffect(() => {
    fetchRiskSignals()
    fetchTrendData()
    const interval = setInterval(() => {
      fetchRiskSignals()
      fetchTrendData()
    }, 5000)
    return () => clearInterval(interval)
  }, [])

  const fetchTrendData = async () => {
    try {
      const response = await fetch('http://localhost:8002/api/v1/risk-overview')
      const data = await response.json()
      if (data.trend_data) {
        setTrendData(data.trend_data)
      } else {
        // Fallback to generated data
        generateTrendData()
      }
    } catch (error) {
      console.error('Error fetching trend data:', error)
      generateTrendData()
    }
  }

  const generateTrendData = () => {
    const last7Days = Array.from({ length: 7 }, (_, i) => {
      const date = new Date()
      date.setDate(date.getDate() - (6 - i))
      return {
        date: date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
        risk: Math.floor(Math.random() * 40) + 40 + (i * 5),
        incidents: Math.floor(Math.random() * 20) + 10
      }
    })
    setTrendData(last7Days)
  }

  const fetchRiskSignals = async () => {
    try {
      // Try to fetch from the data directory relative to the project root
      const response = await fetch('/data/risk_signals.json')
      const data = await response.json()
      setRiskSignals(data)
      setLoading(false)
      console.log('Risk signals loaded:', data.length, 'signals')
    } catch (error) {
      console.error('Error fetching risk signals:', error)
      // Fallback to sample data for demo
      const sampleData = [
        {
          event_type: "clash",
          state: "Borno",
          lga: "Maiduguri",
          severity: "high",
          fuel_price: 570.0,
          inflation: 28.9,
          risk_score: 100,
          risk_level: "Critical"
        },
        {
          event_type: "protest",
          state: "Lagos",
          lga: "Ikeja",
          severity: "medium",
          fuel_price: 680.0,
          inflation: 18.2,
          risk_score: 68.0,
          risk_level: "High"
        }
      ]
      setRiskSignals(sampleData)
      setLoading(false)
      console.log('Using sample data:', sampleData.length, 'signals')
    }
  }

  const handleLocationClick = (signal) => {
    if (mapInstance && signal.lga) {
      const nigeriaLGACoords = {
        'Maiduguri': [13.1571, 11.8333],
        'Ikeja': [3.3375, 6.5964],
        'Kano': [8.5167, 12.0000],
        'Kaduna': [7.4333, 10.5167],
        'Port Harcourt': [7.0167, 4.7833],
        'Abuja': [7.4951, 9.0579]
      }

      const coords = nigeriaLGACoords[signal.lga] || [8.6753, 9.0820]
      
      mapInstance.flyTo({
        center: coords,
        zoom: 12,
        duration: 2000,
        essential: true
      })
    }
  }

  const handleZoomToFit = () => {
    if (mapInstance) {
      mapInstance.flyTo({
        center: [8.6753, 9.0820], // Nigeria center
        zoom: 6,
        duration: 1500,
        essential: true
      })
    }
  }

  const handleSimulation = async (params) => {
    setSimulationParams(params)
    try {
      const response = await fetch('http://localhost:8002/api/v1/simulate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(params)
      })
      const data = await response.json()
      if (data.features) {
        // Update signals with simulated data
        const simulatedSignals = data.features.map(f => f.properties)
        setRiskSignals(simulatedSignals)
      }
      // Refresh trend data after simulation
      fetchTrendData()
    } catch (error) {
      console.error('Simulation error:', error)
    }
  }

  const criticalCount = riskSignals.filter(s => s.risk_score >= 80).length
  const highCount = riskSignals.filter(s => s.risk_score >= 60 && s.risk_score < 80).length
  const avgRiskScore = riskSignals.length > 0 
    ? Math.round(riskSignals.reduce((sum, s) => sum + s.risk_score, 0) / riskSignals.length)
    : 0
  
  const affectedStates = new Set(riskSignals.map(s => s.state)).size

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 text-white">
      {/* Top Row - KPI Cards (15% height) */}
      <div className="h-[15vh] border-b border-gray-700/50">
        <KPICards 
          signals={riskSignals}
          criticalCount={criticalCount}
          affectedStates={affectedStates}
        />
      </div>
      
      {/* Main Section - Bento Grid (75% height) */}
      <div className="h-[75vh] flex">
        {/* Left - Live Signal Ticker (25% width) */}
        <div className="w-[25%] border-r border-gray-700/50">
          <LiveSignalTicker 
            signals={riskSignals}
            onLocationClick={handleLocationClick}
            loading={loading}
          />
        </div>
        
        {/* Center - Map (45% width) */}
        <div className="w-[45%] relative border-r border-gray-700/50">
          <SimpleHeatmap 
            signals={riskSignals}
            onMapReady={setMapInstance}
          />
          {/* Zoom to Fit Button */}
          <button
            onClick={handleZoomToFit}
            className="absolute top-4 right-4 z-[1000] glassmorphism px-4 py-2 rounded-lg text-white hover:bg-white/20 transition-all duration-300 flex items-center gap-2 border border-white/20"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0zM10 7v3m0 0v3m0-3h3m-3 0H7" />
            </svg>
            Zoom to Fit
          </button>
        </div>
        
        {/* Right - National Risk Overview with Charts (30% width) */}
        <div className="w-[30%] bg-gray-900/50">
          <RiskDistributionCharts 
            signals={riskSignals}
            trendData={trendData}
          />
        </div>
      </div>
      
      {/* Bottom Section - Control Panel (10% height) */}
      <div className="h-[10vh] border-t border-gray-700/50">
        <CompactControlPanel 
          onSimulation={handleSimulation}
        />
      </div>
    </div>
  )
}

export default App
