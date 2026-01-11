import { useEffect, useState } from 'react'
import { Bell } from 'lucide-react'

const ThreatStatusBar = ({ avgRiskScore, criticalCount, totalSignals }) => {
  const [currentTime, setCurrentTime] = useState(new Date())

  useEffect(() => {
    const timer = setInterval(() => setCurrentTime(new Date()), 1000)
    return () => clearInterval(timer)
  }, [])

  const getThreatStatus = () => {
    if (avgRiskScore >= 80) return { status: 'CRITICAL', color: 'text-red-400', bg: 'from-gray-900 to-red-900/20', border: 'border-red-500' }
    if (avgRiskScore >= 60) return { status: 'HIGH', color: 'text-orange-400', bg: 'from-gray-900 to-orange-900/20', border: 'border-orange-500' }
    if (avgRiskScore >= 40) return { status: 'ELEVATED', color: 'text-yellow-400', bg: 'from-gray-900 to-yellow-900/20', border: 'border-yellow-500' }
    return { status: 'SAFE', color: 'text-green-400', bg: 'from-gray-900 to-green-900/20', border: 'border-green-500' }
  }

  const threat = getThreatStatus()

  return (
    <div className={`h-[60px] bg-gradient-to-r ${threat.bg} border-b-2 ${threat.border} flex items-center justify-between px-8`}>
      <div className="flex items-center space-x-6">
        <div className="flex items-center space-x-3">
          <div className="w-12 h-12 bg-gradient-to-br from-red-600 to-red-800 rounded-lg flex items-center justify-center shadow-lg">
            <Bell className="w-7 h-7 text-white" />
          </div>
          <div>
            <h1 className="text-xl font-bold text-white">NEXTIER COMMAND & CONTROL</h1>
            <p className="text-sm text-gray-400">Nigeria Geospatial Intelligence System</p>
          </div>
        </div>
      </div>
      
      <div className="flex items-center space-x-8">
        <div className="text-center">
          <div className="text-xs font-semibold text-gray-400">NATIONAL THREAT STATUS</div>
          <div className={`text-2xl font-black ${threat.color} mt-1`}>{threat.status}</div>
        </div>
        <div className="text-center">
          <div className="text-xs font-semibold text-gray-400">AGGREGATE RISK</div>
          <div className="text-2xl font-black text-white mt-1">{avgRiskScore}</div>
        </div>
        <div className="text-center">
          <div className="text-xs font-semibold text-gray-400">ACTIVE HOTSPOTS</div>
          <div className="text-2xl font-black text-white mt-1">{criticalCount}</div>
        </div>
        <div className="text-center">
          <div className="text-xs font-semibold text-gray-400">SYSTEM TIME</div>
          <div className="text-lg font-mono text-white mt-1">
            {currentTime.toLocaleTimeString('en-US', { hour12: false })}
          </div>
        </div>
      </div>
    </div>
  )
}

export default ThreatStatusBar
