import { useState, useEffect } from 'react'
import SimpleHeatmap from './components/SimpleHeatmap'
import LiveSignalTicker from './components/LiveSignalTicker'
import KPICards from './components/KPICards'
import RiskDistributionCharts from './components/RiskDistributionCharts'
import CompactControlPanel from './components/CompactControlPanel'
import SignalDetailPanel from './components/SignalDetailPanel'
import Toast from './components/Toast'
import HighRiskAlertMonitor from './components/HighRiskAlertMonitor'
import PolicymakerAlert from './components/PolicymakerAlert'
import CategorizationIntelligence from './components/CategorizationIntelligence'
import ConflictArchetypeDistribution from './components/ConflictArchetypeDistribution'
import Logo from './components/Logo';
import ChatWithData from './components/ChatWithData'
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
    climateStress: true,
    mining: true,
    border: true
  })
  const [simulationParams, setSimulationParams] = useState({
    fuel_price_index: 50,
    inflation_rate: 50,
    chatter_intensity: 50
  })
  const [miningZoneOverlaps, setMiningZoneOverlaps] = useState(new Set())
  const [categorizationData, setCategorizationData] = useState([])
  const [ingestionVolume, setIngestionVolume] = useState(0)
  const [intelligenceDepth, setIntelligenceDepth] = useState(0)

  useEffect(() => {
    fetchRiskSignals()
    fetchTrendData()
    fetchCategorizationData()
    fetchCategorizationAudit()
    fetchIngestionVolume()
    fetchIntelligenceDepth()
    const interval = setInterval(() => {
      fetchRiskSignals()
      fetchTrendData()
      fetchCategorizationData()
      fetchIngestionVolume()
      fetchIntelligenceDepth()
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

  const fetchCategorizationData = async () => {
    try {
      const response = await fetch(`${API_CONFIG.BASE_URL}${API_CONFIG.ENDPOINTS.CATEGORIZATION_STATS}`)
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      const data = await response.json()
      setCategorizationData(data.categories || [])
      console.log('Categorization data loaded:', data.categories?.length || 0, 'categories')
    } catch (error) {
      console.error('Error fetching categorization data:', error)
      // Use sample data for demo
      const sampleData = [
        { category: 'Banditry', count: 14, confidence: 94 },
        { category: 'Kidnapping', count: 8, confidence: 87 },
        { category: 'Gunmen Violence', count: 22, confidence: 91 },
        { category: 'Farmer-Herder Clashes', count: 16, confidence: 89 }
      ]
      setCategorizationData(sampleData)
      console.log('Using sample categorization data')
    }
  }

  const fetchCategorizationAudit = async () => {
    try {
      const response = await fetch(`${API_CONFIG.BASE_URL}/api/v1/stats/categorization-audit`)
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      const data = await response.json()
      
      // If there are remaining uncategorized articles, trigger categorization
      if (data.remaining_articles > 0) {
        console.log(`Found ${data.remaining_articles} uncategorized articles, triggering categorization...`)
        await triggerCategorization()
      } else {
        console.log('All articles are categorized')
      }
    } catch (error) {
      console.error('Error fetching categorization audit:', error)
      // For demo, do not trigger categorization on 404 error
      if (error.message.includes('404')) {
        console.log('Categorization audit endpoint not found, skipping trigger')
      } else {
        // For other errors, trigger categorization anyway if fetch fails
        await triggerCategorization()
      }
    }
  }

  const triggerCategorization = async () => {
    try {
      const response = await fetch(`${API_CONFIG.BASE_URL}${API_CONFIG.ENDPOINTS.TRIGGER_CATEGORIZATION}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      })
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      const data = await response.json()
      console.log('Categorization triggered:', data.message)
    } catch (error) {
      console.error('Error triggering categorization:', error)
      if (error.message.includes('404')) {
        console.log('Categorization endpoint not found, skipping trigger')
      }
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
      const response = await fetch(`${API_CONFIG.BASE_URL}${API_CONFIG.ENDPOINTS.RISK_SIGNALS}`)
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      const data = await response.json()
      const signals = data.signals || data || []  // Handle both response formats
      setRiskSignals(signals)
      setLoading(false)
      console.log('Risk signals loaded:', signals.length, 'signals')
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
          category: "Banditry",
          confidence: 94
        },
        {
          event_type: "protest",
          state: "Lagos",
          lga: "Ikeja",
          severity: "medium",
          fuel_price: 680.0,
          inflation: 18.2,
          risk_score: 68.0,
          category: "Gunmen Violence",
          confidence: 78
        }
      ]
      setRiskSignals(sampleData)
      setLoading(false)
      console.log('Using sample data:', sampleData.length, 'signals')
    }
  }

  const fetchIngestionVolume = async () => {
    try {
      const response = await fetch(`${API_CONFIG.BASE_URL}${API_CONFIG.ENDPOINTS.INGESTION_VOLUME}`)
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      const data = await response.json()
      setIngestionVolume(data.ingestion_volume || 0)
    } catch (error) {
      console.error('Error fetching ingestion volume:', error)
      setIngestionVolume(0)
    }
  }

  const fetchIntelligenceDepth = async () => {
    try {
      const response = await fetch(`${API_CONFIG.BASE_URL}${API_CONFIG.ENDPOINTS.INTELLIGENCE_DEPTH}`)
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      const data = await response.json()
      setIntelligenceDepth(data.intelligence_depth || 0)
    } catch (error) {
      console.error('Error fetching intelligence depth:', error)
      setIntelligenceDepth(0)
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

  const handleMiningZonesUpdate = (overlaps) => {
    setMiningZoneOverlaps(overlaps)
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
        
        // Update categorization with simulated data if available
        if (data.metadata && data.metadata.simulated_categories) {
          setCategorizationData(data.metadata.simulated_categories)
        }
        
        setError({ message: 'Simulation completed successfully', type: 'success' })
      }
      fetchTrendData()
    } catch (error) {
      console.error('Simulation error:', error)
      setError({ message: `Simulation failed: ${error.message}`, type: 'error' })
    }
  }

  const signalsArray = Array.isArray(riskSignals) ? riskSignals : []
  const criticalCount = signalsArray.filter(s => s.risk_score >= RISK_THRESHOLDS.CRITICAL).length
  const highCount = signalsArray.filter(s => s.risk_score >= RISK_THRESHOLDS.HIGH && s.risk_score < RISK_THRESHOLDS.CRITICAL).length
  const avgRiskScore = signalsArray.length > 0 
    ? Math.round(signalsArray.reduce((sum, s) => sum + s.risk_score, 0) / signalsArray.length)
    : 0
  
  const affectedStates = new Set(signalsArray.map(s => s.state)).size

  // Enrich signals with mining zone information
  const enrichedSignals = signalsArray.map((signal, idx) => {
    const signalKey = `${signal.state}-${signal.lga}-${idx}`
    const inMiningZone = miningZoneOverlaps.has(signalKey)
    return {
      ...signal,
      inMiningZone,
      miningZoneAlert: inMiningZone ? 'Conflict likely fueled by illicit mineral trade' : null
    }
  })

  return (
    <div className="h-screen flex flex-col bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 text-white overflow-hidden">
      {/* Fixed Header with App Name */}
      <div 
        className="flex items-center px-6 flex-shrink-0 fixed top-0 left-0 right-0 z-50"
        style={{ 
          height: '60px',
          backgroundColor: '#1a1a2e',
          borderBottom: '1px solid rgba(59, 130, 246, 0.2)',
        }}
      >
        <div className="flex items-center gap-3">
          <Logo />
          <h1 
            className="text-xl font-semibold text-white tracking-wide m-0 p-0"
          >
            Nextier Nigeria Violent Conflict Database
          </h1>
        </div>
      </div>
      
      {/* Main Content with padding for fixed header */}
      <div className="pt-16 pb-0 h-screen flex flex-col overflow-hidden">
        {/* Top Row - KPI Cards */}
        <div className="flex-shrink-0 border-b border-gray-700/50" style={{ height: '15vh' }}>
          <KPICards 
            signals={riskSignals}
            criticalCount={criticalCount}
            affectedStates={affectedStates}
            ingestionVolume={ingestionVolume}
            intelligenceDepth={intelligenceDepth}
          />
        </div>
        
        {/* Main Section - Bento Grid */}
        <div className="flex flex-1 min-h-0">
          {/* Left - Live Signal Ticker (25% width) */}
          <div className="w-[25%] border-r border-gray-700/50">
            <LiveSignalTicker 
              signals={enrichedSignals}
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
              onMiningZonesUpdate={handleMiningZonesUpdate}
            />
          </div>
          
          {/* Right - National Risk Overview with Charts and Chat (30% width) */}
          <div className="w-[30%] bg-gray-900/50 overflow-y-auto">
            <div className="p-4 space-y-4">
              <PolicymakerAlert signals={enrichedSignals} />
              <ChatWithData />
              <RiskDistributionCharts 
                signals={riskSignals}
                trendData={trendData}
              />
              <CategorizationIntelligence data={categorizationData} />
              <ConflictArchetypeDistribution data={categorizationData} />
            </div>
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
        
        {/* High-Risk Alert Monitor - Instant Webhooks */}
        <HighRiskAlertMonitor />
      </div>
    </div>
  )
}

export default App
