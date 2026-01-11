import { useState, useEffect } from 'react'
import SimpleHeatmap from './components/SimpleHeatmap'
import LiveSignalTicker from './components/LiveSignalTicker'
import NationalRiskOverview from './components/NationalRiskOverview'
import ThreatStatusBar from './components/ThreatStatusBar'
import './App.css'

function App() {
  const [riskSignals, setRiskSignals] = useState([])
  const [mapInstance, setMapInstance] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchRiskSignals()
    const interval = setInterval(fetchRiskSignals, 5000)
    return () => clearInterval(interval)
  }, [])

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

  const criticalCount = riskSignals.filter(s => s.risk_score >= 80).length
  const highCount = riskSignals.filter(s => s.risk_score >= 60 && s.risk_score < 80).length
  const avgRiskScore = riskSignals.length > 0 
    ? Math.round(riskSignals.reduce((sum, s) => sum + s.risk_score, 0) / riskSignals.length)
    : 0

  return (
    <div className="min-h-screen bg-bg-primary text-white">
      <ThreatStatusBar 
        avgRiskScore={avgRiskScore}
        criticalCount={criticalCount}
        totalSignals={riskSignals.length}
      />
      
      <div className="grid grid-cols-12 h-[calc(100vh-60px)]">
        <LiveSignalTicker 
          signals={riskSignals}
          onLocationClick={handleLocationClick}
          loading={loading}
        />
        
        <div className="col-span-7 relative">
          <SimpleHeatmap 
            signals={riskSignals}
          />
        </div>
        
        <div className="col-span-3 bg-bg-secondary border-l border-gray-800 overflow-y-auto">
          <NationalRiskOverview 
            signals={riskSignals}
            criticalCount={criticalCount}
            highCount={highCount}
          />
        </div>
      </div>
    </div>
  )
}

export default App
