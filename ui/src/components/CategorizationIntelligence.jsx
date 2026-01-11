import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import { Brain, TrendingUp } from 'lucide-react'

const CategorizationIntelligence = ({ data }) => {
  // Ensure data is an array
  const chartData = Array.isArray(data) ? data : []

  // Custom tooltip to show category info
  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload
      return (
        <div className="bg-gray-900/95 border border-gray-700 p-3 rounded-lg backdrop-blur-sm">
          <p className="text-white font-semibold">{data.category}</p>
          <p className="text-blue-400">{data.count} Events</p>
          <p className="text-green-400">{data.confidence}% Avg Confidence</p>
        </div>
      )
    }
    return null
  }

  return (
    <div className="bg-gray-800/50 rounded-lg p-4 border border-gray-700/50">
      {/* Header */}
      <div className="flex items-center mb-4">
        <Brain className="w-5 h-5 text-purple-400 mr-2" />
        <h3 className="text-lg font-semibold text-white">Categorization Intelligence</h3>
      </div>

      {/* Chart */}
      <div className="h-64">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart
            data={chartData}
            layout="horizontal"
            margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
          >
            <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
            <XAxis
              type="number"
              stroke="#9CA3AF"
              fontSize={12}
            />
            <YAxis
              type="category"
              dataKey="category"
              stroke="#9CA3AF"
              fontSize={12}
              width={120}
            />
            <Tooltip content={<CustomTooltip />} />
            <Bar
              dataKey="count"
              fill="#8B5CF6"
              radius={[0, 4, 4, 0]}
            />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Trust Signals */}
      <div className="mt-4 space-y-2">
        {chartData.map((item, index) => (
          <div key={index} className="flex justify-between items-center text-sm">
            <span className="text-gray-300">{item.category}:</span>
            <span className="text-white font-medium">
              {item.count} Events | {item.confidence}% Avg Confidence
            </span>
          </div>
        ))}
      </div>
    </div>
  )
}

export default CategorizationIntelligence
