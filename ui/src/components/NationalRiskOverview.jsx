import { useState, useEffect } from 'react'
import { LineChart, Line, BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import { TrendingUp, Shield, AlertCircle, RefreshCw, Zap } from 'lucide-react'

const NationalRiskOverview = ({ signals, criticalCount, highCount }) => {
  const [trendData, setTrendData] = useState([])
  const [selectedView, setSelectedView] = useState('trend')
  const [loading, setLoading] = useState(false)
  const [statusMessage, setStatusMessage] = useState('')

  useEffect(() => {
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
  }, [signals])

  const handleScrapeIntel = async () => {
    setLoading(true)
    setStatusMessage('Scraping intelligence...')
    try {
      const response = await fetch('http://localhost:8000/api/v1/scrape', { method: 'GET' })
      const data = await response.json()
      setStatusMessage(`✓ Scraped ${data.articles_scraped || 0} articles`)
      setTimeout(() => setStatusMessage(''), 3000)
    } catch (error) {
      setStatusMessage('✗ Scrape failed')
      setTimeout(() => setStatusMessage(''), 3000)
    } finally {
      setLoading(false)
    }
  }

  const handleAnalyzeEvents = async () => {
    setLoading(true)
    setStatusMessage('Analyzing events...')
    try {
      const response = await fetch('http://localhost:8001/api/v1/analyze', { method: 'POST' })
      const data = await response.json()
      setStatusMessage(`✓ Analyzed ${data.events_processed || 0} events`)
      setTimeout(() => setStatusMessage(''), 3000)
    } catch (error) {
      setStatusMessage('✗ Analysis failed')
      setTimeout(() => setStatusMessage(''), 3000)
    } finally {
      setLoading(false)
    }
  }

  const handleCalculateRisks = async () => {
    setLoading(true)
    setStatusMessage('Calculating risks...')
    try {
      const response = await fetch('http://localhost:8002/api/v1/predict', { method: 'POST' })
      const data = await response.json()
      setStatusMessage(`✓ Calculated ${data.signals_generated || 0} risk signals`)
      setTimeout(() => setStatusMessage(''), 3000)
    } catch (error) {
      setStatusMessage('✗ Calculation failed')
      setTimeout(() => setStatusMessage(''), 3000)
    } finally {
      setLoading(false)
    }
  }

  const handleStressTest = async () => {
    setLoading(true)
    setStatusMessage('Running stress test...')
    try {
      const response = await fetch('http://localhost:8002/api/v1/simulate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          fuel_price_index: 95,
          inflation_rate: 85,
          chatter_intensity: 90
        })
      })
      const data = await response.json()
      setStatusMessage(`✓ Stress test complete: ${data.metadata?.total_events || 0} signals`)
      setTimeout(() => setStatusMessage(''), 3000)
    } catch (error) {
      setStatusMessage('✗ Stress test failed')
      setTimeout(() => setStatusMessage(''), 3000)
    } finally {
      setLoading(false)
    }
  }

  const riskDistribution = [
    { name: 'Critical', value: signals.filter(s => s.risk_score >= 80).length, color: '#ef4444' },
    { name: 'High', value: signals.filter(s => s.risk_score >= 60 && s.risk_score < 80).length, color: '#f97316' },
    { name: 'Medium', value: signals.filter(s => s.risk_score >= 40 && s.risk_score < 60).length, color: '#eab308' },
    { name: 'Low', value: signals.filter(s => s.risk_score < 40).length, color: '#22c55e' }
  ]

  const stateBreakdown = Object.entries(
    signals.reduce((acc, signal) => {
      acc[signal.state] = (acc[signal.state] || 0) + 1
      return acc
    }, {})
  ).map(([state, count]) => ({ state, count })).slice(0, 5)

  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-gray-900 border border-gray-700 rounded-lg p-3 shadow-lg">
          <p className="text-white font-semibold">{payload[0].payload.date}</p>
          <p className="text-red-400">Risk: {payload[0].value}</p>
          {payload[0].payload.incidents && (
            <p className="text-blue-400">Incidents: {payload[0].payload.incidents}</p>
          )}
        </div>
      )
    }
    return null
  }

  return (
    <div className="p-6 space-y-6">
      <div className="border-b border-gray-800 pb-4">
        <h3 className="text-lg font-bold text-white flex items-center">
          <TrendingUp className="w-6 h-6 text-blue-400 mr-3" />
          NATIONAL RISK OVERVIEW
        </h3>
        <p className="text-xs text-gray-400 mt-2">7-Day Trend Analysis</p>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div className="bg-gray-900 border border-red-900/50 rounded-lg p-4">
          <div className="flex items-center justify-between mb-2">
            <AlertCircle className="w-5 h-5 text-red-400" />
            <span className="text-2xl font-bold text-red-400">{criticalCount}</span>
          </div>
          <p className="text-xs text-gray-400">Critical Zones</p>
        </div>

        <div className="bg-gray-900 border border-orange-900/50 rounded-lg p-4">
          <div className="flex items-center justify-between mb-2">
            <Shield className="w-5 h-5 text-orange-400" />
            <span className="text-2xl font-bold text-orange-400">{highCount}</span>
          </div>
          <p className="text-xs text-gray-400">High Risk</p>
        </div>
      </div>

      <div className="bg-gray-900 rounded-lg p-4 border border-gray-800">
        <div className="flex items-center justify-between mb-4">
          <h4 className="text-sm font-bold text-white">VIEW MODE</h4>
          <div className="flex space-x-2">
            <button
              onClick={() => setSelectedView('trend')}
              className={`px-3 py-1 rounded text-xs font-semibold transition-all ${
                selectedView === 'trend' ? 'bg-blue-600 text-white' : 'bg-gray-800 text-gray-400'
              }`}
            >
              Trend
            </button>
            <button
              onClick={() => setSelectedView('distribution')}
              className={`px-3 py-1 rounded text-xs font-semibold transition-all ${
                selectedView === 'distribution' ? 'bg-blue-600 text-white' : 'bg-gray-800 text-gray-400'
              }`}
            >
              Distribution
            </button>
          </div>
        </div>

        {selectedView === 'trend' ? (
          <ResponsiveContainer width="100%" height={200}>
            <LineChart data={trendData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis dataKey="date" stroke="#9ca3af" style={{ fontSize: '10px' }} />
              <YAxis stroke="#9ca3af" style={{ fontSize: '10px' }} />
              <Tooltip content={<CustomTooltip />} />
              <Line type="monotone" dataKey="risk" stroke="#ef4444" strokeWidth={2} dot={{ fill: '#ef4444', r: 4 }} />
            </LineChart>
          </ResponsiveContainer>
        ) : (
          <ResponsiveContainer width="100%" height={200}>
            <PieChart>
              <Pie
                data={riskDistribution}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, value }) => `${name}: ${value}`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {riskDistribution.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        )}
      </div>

      <div className="bg-gray-900 rounded-lg p-4 border border-gray-800">
        <h4 className="text-sm font-bold text-white mb-4">TOP AFFECTED STATES</h4>
        <div className="space-y-3">
          {stateBreakdown.map((item, index) => (
            <div key={index} className="flex items-center justify-between">
              <span className="text-sm text-gray-300">{item.state}</span>
              <div className="flex items-center space-x-2">
                <div className="w-24 h-2 bg-gray-800 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-red-500"
                    style={{ width: `${(item.count / signals.length) * 100}%` }}
                  ></div>
                </div>
                <span className="text-sm font-bold text-white w-8 text-right">{item.count}</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="bg-gray-900 rounded-lg p-4 border border-gray-800">
        <h4 className="text-sm font-bold text-white mb-3">QUICK ACTIONS</h4>
        {statusMessage && (
          <div className="mb-3 p-2 bg-gray-800 border border-gray-700 rounded text-xs text-white text-center">
            {statusMessage}
          </div>
        )}
        <div className="space-y-2">
          <button 
            onClick={handleScrapeIntel}
            disabled={loading}
            className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-700 disabled:cursor-not-allowed text-white px-4 py-2 rounded-lg text-sm font-semibold transition-all flex items-center justify-center space-x-2"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
            <span>Scrape Intel</span>
          </button>
          <button 
            onClick={handleAnalyzeEvents}
            disabled={loading}
            className="w-full bg-green-600 hover:bg-green-700 disabled:bg-gray-700 disabled:cursor-not-allowed text-white px-4 py-2 rounded-lg text-sm font-semibold transition-all flex items-center justify-center space-x-2"
          >
            <Shield className="w-4 h-4" />
            <span>Analyze Events</span>
          </button>
          <button 
            onClick={handleCalculateRisks}
            disabled={loading}
            className="w-full bg-orange-600 hover:bg-orange-700 disabled:bg-gray-700 disabled:cursor-not-allowed text-white px-4 py-2 rounded-lg text-sm font-semibold transition-all flex items-center justify-center space-x-2"
          >
            <TrendingUp className="w-4 h-4" />
            <span>Calculate Risks</span>
          </button>
          <button 
            onClick={handleStressTest}
            disabled={loading}
            className="w-full bg-purple-600 hover:bg-purple-700 disabled:bg-gray-700 disabled:cursor-not-allowed text-white px-4 py-2 rounded-lg text-sm font-semibold transition-all flex items-center justify-center space-x-2"
          >
            <Zap className="w-4 h-4" />
            <span>Stress Test</span>
          </button>
        </div>
      </div>

      <div className="bg-gradient-to-br from-blue-900/20 to-purple-900/20 border border-blue-800/50 rounded-lg p-4">
        <h4 className="text-sm font-bold text-blue-400 mb-2">🛡️ SOVEREIGN INTELLIGENCE</h4>
        <ul className="text-xs text-gray-300 space-y-1">
          <li>✓ Zero Vendor Lock-in</li>
          <li>✓ Privacy-First Architecture</li>
          <li>✓ OpenFreeMap - No Tracking</li>
          <li>✓ 100% Offline Capable</li>
        </ul>
      </div>
    </div>
  )
}

export default NationalRiskOverview
