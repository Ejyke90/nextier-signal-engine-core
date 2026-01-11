import { useState } from 'react'
import { RefreshCw, Zap, Activity, TrendingUp } from 'lucide-react'

const CompactControlPanel = ({ onSimulation }) => {
  const [loading, setLoading] = useState(false)
  const [statusMessage, setStatusMessage] = useState('')
  const [sliders, setSliders] = useState({
    fuel_price_index: 50,
    inflation_rate: 50,
    chatter_intensity: 50
  })

  const handleSliderChange = (key, value) => {
    const newSliders = { ...sliders, [key]: parseInt(value) }
    setSliders(newSliders)
    // Real-time update on slider move
    if (onSimulation) {
      onSimulation(newSliders)
    }
  }

  const handleQuickAction = async (action) => {
    setLoading(true)
    setStatusMessage(`${action}...`)
    
    try {
      let endpoint = ''
      let method = 'GET'
      
      switch(action) {
        case 'Scrape':
          endpoint = 'http://localhost:8000/api/v1/scrape'
          break
        case 'Analyze':
          endpoint = 'http://localhost:8001/api/v1/analyze'
          method = 'POST'
          break
        case 'Calculate':
          endpoint = 'http://localhost:8002/api/v1/predict'
          method = 'POST'
          break
        case 'StressTest':
          endpoint = 'http://localhost:8002/api/v1/simulate'
          method = 'POST'
          break
      }
      
      const options = { method }
      
      // Add body for stress test
      if (action === 'StressTest') {
        options.headers = { 'Content-Type': 'application/json' }
        options.body = JSON.stringify({
          fuel_price_index: 95,
          inflation_rate: 85,
          chatter_intensity: 90
        })
      }
      
      const response = await fetch(endpoint, options)
      const data = await response.json()
      
      // Update status based on action
      if (action === 'StressTest') {
        setStatusMessage(`✓ Stress test: ${data.metadata?.total_events || 0} signals`)
        // Trigger simulation callback if available
        if (onSimulation) {
          onSimulation({
            fuel_price_index: 95,
            inflation_rate: 85,
            chatter_intensity: 90
          })
        }
      } else {
        setStatusMessage(`✓ ${action} complete`)
      }
      setTimeout(() => setStatusMessage(''), 2000)
    } catch (error) {
      setStatusMessage(`✗ ${action} failed`)
      setTimeout(() => setStatusMessage(''), 2000)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="h-full flex items-center justify-between px-6 bg-gray-900/50 backdrop-blur-sm">
      {/* Quick Actions */}
      <div className="flex items-center gap-3">
        <button
          onClick={() => handleQuickAction('Scrape')}
          disabled={loading}
          className="glassmorphism px-4 py-2 rounded-lg text-sm font-semibold text-white hover:bg-white/10 transition-all flex items-center gap-2 disabled:opacity-50"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          Scrape
        </button>
        <button
          onClick={() => handleQuickAction('Analyze')}
          disabled={loading}
          className="glassmorphism px-4 py-2 rounded-lg text-sm font-semibold text-white hover:bg-white/10 transition-all flex items-center gap-2 disabled:opacity-50"
        >
          <Activity className="w-4 h-4" />
          Analyze
        </button>
        <button
          onClick={() => handleQuickAction('Calculate')}
          disabled={loading}
          className="glassmorphism px-4 py-2 rounded-lg text-sm font-semibold text-white hover:bg-white/10 transition-all flex items-center gap-2 disabled:opacity-50"
        >
          <TrendingUp className="w-4 h-4" />
          Calculate
        </button>
        <button
          onClick={() => handleQuickAction('StressTest')}
          disabled={loading}
          className="glassmorphism px-4 py-2 rounded-lg text-sm font-semibold text-purple-400 hover:bg-purple-500/20 transition-all flex items-center gap-2 disabled:opacity-50 border border-purple-500/30"
        >
          <Zap className="w-4 h-4" />
          Stress Test
        </button>
      </div>

      {/* Status Message */}
      {statusMessage && (
        <div className="glassmorphism px-4 py-2 rounded-lg text-sm text-white">
          {statusMessage}
        </div>
      )}

      {/* Simulation Sliders */}
      <div className="flex items-center gap-6">
        <div className="flex items-center gap-3">
          <Zap className="w-4 h-4 text-amber-400" />
          <div className="flex flex-col">
            <label className="text-xs text-gray-400 mb-1">Fuel Price</label>
            <input
              type="range"
              min="0"
              max="100"
              value={sliders.fuel_price_index}
              onChange={(e) => handleSliderChange('fuel_price_index', e.target.value)}
              className="w-32 h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer slider"
            />
            <span className="text-xs text-white mt-1">{sliders.fuel_price_index}%</span>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <TrendingUp className="w-4 h-4 text-red-400" />
          <div className="flex flex-col">
            <label className="text-xs text-gray-400 mb-1">Inflation</label>
            <input
              type="range"
              min="0"
              max="100"
              value={sliders.inflation_rate}
              onChange={(e) => handleSliderChange('inflation_rate', e.target.value)}
              className="w-32 h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer slider"
            />
            <span className="text-xs text-white mt-1">{sliders.inflation_rate}%</span>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <Activity className="w-4 h-4 text-blue-400" />
          <div className="flex flex-col">
            <label className="text-xs text-gray-400 mb-1">Chatter</label>
            <input
              type="range"
              min="0"
              max="100"
              value={sliders.chatter_intensity}
              onChange={(e) => handleSliderChange('chatter_intensity', e.target.value)}
              className="w-32 h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer slider"
            />
            <span className="text-xs text-white mt-1">{sliders.chatter_intensity}%</span>
          </div>
        </div>
      </div>
    </div>
  )
}

export default CompactControlPanel
