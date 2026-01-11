import { useState, useEffect } from 'react'
import SimpleHeatmap from './components/SimpleHeatmap'
import LiveSignalTicker from './components/LiveSignalTicker'
import KPICards from './components/KPICards'
import RiskDistributionCharts from './components/RiskDistributionCharts'
import CompactControlPanel from './components/CompactControlPanel'
import SignalDetailPanel from './components/SignalDetailPanel'
import Toast from './components/Toast'
import { API_CONFIG, POLLING_INTERVAL, NIGERIA_LGA_COORDS, NIGERIA_CENTER, MAP_CONFIG, RISK_THRESHOLDS } from './constants'
import './App.css'

function App() {
  const [riskSignals, setRiskSignals] = useState([])
  const [mapInstance, setMapInstance] = useState(null)
  const [loading, setLoading] = useState(true)
  const [trendData, setTrendData] = useState([])
  const [selectedSignal, setSelectedSignal] = useState(null)
  const [error, setError] = useState(null)
  const [layers, setLayers] = useState({
    heatmap: true,
    markers: true,
    climate: true,
    mining: true,
    border: true
  })
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
    }, POLLING_INTERVAL)
    return () => clearInterval(interval)
  }, [])

  const fetchTrendData = async () => {
    try {
      const response = await fetch(`${API_CONFIG.BASE_URL}${API_CONFIG.ENDPOINTS.RISK_OVERVIEW}`)
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      const data = await response.json()
      if (data.trend_data) {
        setTrendData(data.trend_data)
      } else {
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
      const response = await fetch(API_CONFIG.ENDPOINTS.RISK_SIGNALS)
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
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
      const coords = NIGERIA_LGA_COORDS[signal.lga]
      const center = coords ? [coords.lat, coords.lng] : [NIGERIA_CENTER.lat, NIGERIA_CENTER.lng]
      
      mapInstance.flyTo(center, MAP_CONFIG.DETAIL_ZOOM, {
        duration: MAP_CONFIG.FLY_DURATION
      })
    }
  }

  const handleSignalClick = (signal) => {
    setSelectedSignal(signal)
  }

  const handleLayerChange = (newLayers) => {
    setLayers(newLayers)
  }

  const handleSimulation = async (params) => {
    setSimulationParams(params)
    setError(null)
    try {
      const response = await fetch(`${API_CONFIG.BASE_URL}${API_CONFIG.ENDPOINTS.SIMULATE}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(params)
      })
      
      if (!response.ok) {
        throw new Error(`Simulation failed: ${response.status} ${response.statusText}`)
      }
      
      const data = await response.json()
      if (data.features) {
        const simulatedSignals = data.features.map(f => f.properties)
        setRiskSignals(simulatedSignals)
        setError({ message: 'Simulation completed successfully', type: 'success' })
      }
      fetchTrendData()
    } catch (error) {
      console.error('Simulation error:', error)
      setError({ message: `Simulation failed: ${error.message}`, type: 'error' })
    }
  }

  const criticalCount = riskSignals.filter(s => s.risk_score >= RISK_THRESHOLDS.CRITICAL).length
  const highCount = riskSignals.filter(s => s.risk_score >= RISK_THRESHOLDS.HIGH && s.risk_score < RISK_THRESHOLDS.CRITICAL).length
  const avgRiskScore = riskSignals.length > 0 
    ? Math.round(riskSignals.reduce((sum, s) => sum + s.risk_score, 0) / riskSignals.length)
    : 0
  
  const affectedStates = new Set(riskSignals.map(s => s.state)).size

  return (
    <div className="h-screen flex flex-col bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 text-white overflow-hidden">
      {/* Compact Header with App Name */}
      <div 
        className="flex items-center px-6 flex-shrink-0"
        style={{ 
          height: '50px',
          backgroundColor: '#1a1a2e',
          borderBottom: '1px solid rgba(59, 130, 246, 0.2)',
          zIndex: 1000
        }}
      >
        <h1 
          style={{ 
            color: '#ffffff',
            fontSize: '18px',
            fontWeight: '600',
            margin: 0,
            padding: 0,
            letterSpacing: '0.5px'
          }}
        >
          Nextier Nigeria Violent Conflict Database
        </h1>
      </div>
      
      {/* Top Row - KPI Cards */}
      <div className="flex-shrink-0 border-b border-gray-700/50" style={{ height: '15vh' }}>
        <KPICards 
          signals={riskSignals}
          criticalCount={criticalCount}
          affectedStates={affectedStates}
        />
      </div>
      
      {/* Main Section - Bento Grid */}
      <div className="flex flex-1 min-h-0">
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
            onSignalClick={handleSignalClick}
            layers={layers}
            onLayerChange={handleLayerChange}
          />
        </div>
        
        {/* Right - National Risk Overview with Charts (30% width) */}
        <div className="w-[30%] bg-gray-900/50">
          <RiskDistributionCharts 
            signals={riskSignals}
            trendData={trendData}
          />
        </div>
      </div>
      
      {/* Bottom Section - Control Panel */}
      <div className="flex-shrink-0 border-t border-gray-700/50" style={{ height: '10vh' }}>
        <CompactControlPanel 
          onSimulation={handleSimulation}
        />
      </div>
      
      {/* Signal Detail Panel */}
      {selectedSignal && (
        <SignalDetailPanel 
          signal={selectedSignal}
          onClose={() => setSelectedSignal(null)}
        />
      )}
      
      {/* Toast Notifications */}
      {error && (
        <Toast 
          message={error.message}
          type={error.type}
          onClose={() => setError(null)}
        />
      )}
    </div>
  )
}

export default App
