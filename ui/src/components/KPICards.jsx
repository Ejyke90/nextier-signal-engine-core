import { Activity, AlertTriangle, MapPin, Clock } from 'lucide-react'
import { useEffect, useState } from 'react'

const KPICards = ({ signals, criticalCount, affectedStates }) => {
  const [currentTime, setCurrentTime] = useState(new Date())

  useEffect(() => {
    const timer = setInterval(() => setCurrentTime(new Date()), 1000)
    return () => clearInterval(timer)
  }, [])

  const kpis = [
    {
      label: 'Active Signals',
      value: signals.length,
      icon: Activity,
      color: 'text-blue-400',
      bgColor: 'bg-blue-500/10',
      borderColor: 'border-blue-500/30'
    },
    {
      label: 'Critical LGAs',
      value: criticalCount,
      icon: AlertTriangle,
      color: 'text-red-400',
      bgColor: 'bg-red-500/10',
      borderColor: 'border-red-500/30'
    },
    {
      label: 'Affected States',
      value: affectedStates,
      icon: MapPin,
      color: 'text-amber-400',
      bgColor: 'bg-amber-500/10',
      borderColor: 'border-amber-500/30'
    },
    {
      label: 'System Time',
      value: currentTime.toLocaleTimeString('en-US', { hour12: false }),
      icon: Clock,
      color: 'text-green-400',
      bgColor: 'bg-green-500/10',
      borderColor: 'border-green-500/30',
      subValue: currentTime.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
    }
  ]

  return (
    <div className="grid grid-cols-4 gap-4 p-4">
      {kpis.map((kpi, index) => {
        const Icon = kpi.icon
        return (
          <div 
            key={index}
            className={`glassmorphism rounded-xl p-4 border ${kpi.borderColor} hover:border-opacity-60 transition-all duration-300`}
          >
            <div className="flex items-center justify-between">
              <div className="flex-1">
                <p className="text-xs text-gray-400 uppercase tracking-wider mb-1">{kpi.label}</p>
                <p className={`text-2xl font-bold ${kpi.color}`}>{kpi.value}</p>
                {kpi.subValue && (
                  <p className="text-xs text-gray-500 mt-1">{kpi.subValue}</p>
                )}
              </div>
              <div className={`${kpi.bgColor} p-3 rounded-lg`}>
                <Icon className={`w-6 h-6 ${kpi.color}`} />
              </div>
            </div>
          </div>
        )
      })}
    </div>
  )
}

export default KPICards
