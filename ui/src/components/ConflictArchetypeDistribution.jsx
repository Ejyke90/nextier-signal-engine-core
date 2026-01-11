import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import { Sword, Users, Shield, DollarSign } from 'lucide-react'

const ConflictArchetypeDistribution = ({ data }) => {
  // Ensure data is an array
  const rawData = Array.isArray(data) ? data : []

  // Map existing categories to conflict archetypes
  const categoryMapping = {
    'Organized Banditry': 'Organized Banditry',
    'Kidnapping-for-Ransom': 'Kidnapping-for-Ransom',
    'Sectarian Insurgency': 'Sectarian Insurgency',
    'Farmer-Herder Clashes': 'Farmer-Herder Clashes',
    // Legacy mappings for backward compatibility
    'Banditry': 'Organized Banditry',
    'Kidnapping': 'Kidnapping-for-Ransom',
    'Gunmen Violence': 'Sectarian Insurgency'
  }

  // Transform data to archetypes
  const archetypeData = rawData.map(item => ({
    archetype: categoryMapping[item.category] || item.category,
    count: item.count,
    confidence: item.confidence,
    originalCategory: item.category
  })).filter(item => item.archetype !== item.originalCategory || item.originalCategory === 'Farmer-Herder Clashes')

  // Add missing archetypes with 0 count if not present
  const requiredArchetypes = ['Organized Banditry', 'Farmer-Herder Clashes', 'Sectarian Insurgency', 'Kidnapping-for-Ransom']
  const completeData = requiredArchetypes.map(archetype => {
    const existing = archetypeData.find(item => item.archetype === archetype)
    return existing || { archetype, count: 0, confidence: 0 }
  })

  // Icons for archetypes
  const getArchetypeIcon = (archetype) => {
    switch (archetype) {
      case 'Organized Banditry': return Sword
      case 'Farmer-Herder Clashes': return Users
      case 'Sectarian Insurgency': return Shield
      case 'Kidnapping-for-Ransom': return DollarSign
      default: return Sword
    }
  }

  // Custom tooltip
  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload
      return (
        <div className="bg-gray-900/95 border border-gray-700 p-3 rounded-lg backdrop-blur-sm">
          <p className="text-white font-semibold">{data.archetype}</p>
          <p className="text-blue-400">{data.count} Incidents</p>
          <p className="text-green-400">AI Certainty: {data.confidence}%</p>
        </div>
      )
    }
    return null
  }

  return (
    <div className="bg-gray-800/50 rounded-lg p-4 border border-gray-700/50">
      {/* Header */}
      <div className="flex items-center mb-4">
        <Shield className="w-5 h-5 text-red-400 mr-2" />
        <h3 className="text-lg font-semibold text-white">Conflict Archetype Distribution</h3>
      </div>

      {/* Chart */}
      <div className="h-64 mb-4">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart
            data={completeData}
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
              dataKey="archetype"
              stroke="#9CA3AF"
              fontSize={12}
              width={140}
            />
            <Tooltip content={<CustomTooltip />} />
            <Bar
              dataKey="count"
              fill="#EF4444"
              radius={[0, 4, 4, 0]}
            />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* AI Certainty Labels Below Bars */}
      <div className="space-y-2">
        {completeData.map((item, index) => {
          const Icon = getArchetypeIcon(item.archetype)
          return (
            <div key={index} className="flex items-center justify-between text-sm bg-gray-700/30 rounded px-3 py-2">
              <div className="flex items-center">
                <Icon className="w-4 h-4 text-gray-400 mr-2" />
                <span className="text-gray-300">{item.archetype}</span>
              </div>
              <span className="text-green-400 font-medium">
                AI Certainty: {item.confidence}%
              </span>
            </div>
          )
        })}
      </div>
    </div>
  )
}

export default ConflictArchetypeDistribution
