import { PieChart, Pie, Cell, AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import { TrendingUp, AlertTriangle } from 'lucide-react'

const RiskDistributionCharts = ({ signals, trendData }) => {
  const riskDistribution = [
    { name: 'Critical', value: signals.filter(s => s.risk_score >= 80).length, color: '#FF4B4B' },
    { name: 'High', value: signals.filter(s => s.risk_score >= 60 && s.risk_score < 80).length, color: '#FFA500' },
    { name: 'Medium', value: signals.filter(s => s.risk_score >= 40 && s.risk_score < 60).length, color: '#FFD700' },
    { name: 'Low', value: signals.filter(s => s.risk_score < 40).length, color: '#00FF00' }
  ]

  const topAffectedStates = signals
    .reduce((acc, signal) => {
      const state = signal.state || 'Unknown'
      acc[state] = (acc[state] || 0) + 1
      return acc
    }, {})

  const topStates = Object.entries(topAffectedStates)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 5)
    .map(([state, count]) => ({ state, count }))

  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-gray-900/95 border border-gray-700 p-3 rounded-lg backdrop-blur-sm">
          <p className="text-white font-semibold">{payload[0].name}</p>
          <p className="text-gray-300">{payload[0].value} signals</p>
        </div>
      )
    }
    return null
  }

  const TrendTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-gray-900/95 border border-gray-700 p-3 rounded-lg backdrop-blur-sm">
          <p className="text-white font-semibold">{payload[0].payload.date}</p>
          <p className="text-red-400">Risk: {payload[0].value}</p>
          <p className="text-gray-300">Incidents: {payload[0].payload.incidents}</p>
        </div>
      )
    }
    return null
  }

  return (
    <div className="h-full flex flex-col space-y-4 p-4">
      {/* Risk Level Distribution - Donut Chart */}
      <div className="glassmorphism rounded-xl p-4 flex-shrink-0">
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-lg font-semibold text-white flex items-center gap-2">
            <AlertTriangle className="w-5 h-5 text-red-500" />
            Risk Distribution
          </h3>
        </div>
        <ResponsiveContainer width="100%" height={200}>
          <PieChart>
            <Pie
              data={riskDistribution}
              cx="50%"
              cy="50%"
              innerRadius={50}
              outerRadius={80}
              paddingAngle={2}
              dataKey="value"
            >
              {riskDistribution.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.color} />
              ))}
            </Pie>
            <Tooltip content={<CustomTooltip />} />
          </PieChart>
        </ResponsiveContainer>
        <div className="grid grid-cols-2 gap-2 mt-3">
          {riskDistribution.map((item) => (
            <div key={item.name} className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full" style={{ backgroundColor: item.color }}></div>
              <span className="text-sm text-gray-300">{item.name}: {item.value}</span>
            </div>
          ))}
        </div>
      </div>

      {/* 7-Day Risk Trend - Area Chart */}
      <div className="glassmorphism rounded-xl p-4 flex-1">
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-lg font-semibold text-white flex items-center gap-2">
            <TrendingUp className="w-5 h-5 text-amber-500" />
            7-Day Risk Trend
          </h3>
        </div>
        <ResponsiveContainer width="100%" height="85%">
          <AreaChart data={trendData}>
            <defs>
              <linearGradient id="colorRisk" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#FF4B4B" stopOpacity={0.8}/>
                <stop offset="95%" stopColor="#FF4B4B" stopOpacity={0.1}/>
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
            <XAxis 
              dataKey="date" 
              stroke="#9CA3AF"
              style={{ fontSize: '12px' }}
            />
            <YAxis 
              stroke="#9CA3AF"
              style={{ fontSize: '12px' }}
            />
            <Tooltip content={<TrendTooltip />} />
            <Area 
              type="monotone" 
              dataKey="risk" 
              stroke="#FF4B4B" 
              strokeWidth={2}
              fillOpacity={1} 
              fill="url(#colorRisk)" 
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      {/* Top Affected States */}
      <div className="glassmorphism rounded-xl p-4 flex-shrink-0">
        <h3 className="text-lg font-semibold text-white mb-3">Top Affected States</h3>
        <div className="space-y-2">
          {topStates.map((item, index) => (
            <div key={item.state} className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span className="text-xs font-bold text-gray-400 w-4">{index + 1}</span>
                <span className="text-sm text-white">{item.state}</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-20 h-2 bg-gray-700 rounded-full overflow-hidden">
                  <div 
                    className="h-full bg-red-500 rounded-full"
                    style={{ width: `${(item.count / signals.length) * 100}%` }}
                  ></div>
                </div>
                <span className="text-sm font-semibold text-red-400 w-8 text-right">{item.count}</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

export default RiskDistributionCharts
