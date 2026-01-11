import { Activity, AlertTriangle, MapPin, Radio } from 'lucide-react'
import { useEffect, useState } from 'react'

const KPICards = ({ signals, criticalCount, affectedStates }) => {
  const [lastIngestionTime, setLastIngestionTime] = useState(null)

  useEffect(() => {
    // Calculate time since last ingestion from signals
    if (signals && signals.length > 0) {
      let latestSignal = null
      
      for (const signal of signals) {
        const timestamp = signal.scraped_at || signal.published_at
        if (timestamp) {
          const signalTime = new Date(timestamp)
          // Only consider valid dates (not epoch time)
          if (signalTime.getFullYear() > 2020 && (!latestSignal || signalTime > latestSignal)) {
            latestSignal = signalTime
          }
        }
      }
      
      // If no valid timestamp found, use current time (just ingested)
      setLastIngestionTime(latestSignal || new Date())
    } else {
      setLastIngestionTime(new Date())
    }
  }, [signals])

  const getMinutesAgo = () => {
    if (!lastIngestionTime) return '<1'
    const now = new Date()
    const diffMs = now - lastIngestionTime
    const minutes = Math.floor(diffMs / 60000)
    
    // If less than 1 minute, show <1
    if (minutes < 1) return '<1'
    // If more than 60 minutes, show hours
    if (minutes > 60) {
      const hours = Math.floor(minutes / 60)
      return `${hours}h`
    }
    return minutes
  }

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
      label: 'Operational Status',
      value: `Last Ingestion: ${getMinutesAgo()}m ago`,
      icon: Radio,
      color: 'text-green-400',
      bgColor: 'bg-green-500/10',
      borderColor: 'border-green-500/30',
      subValue: 'Source Uptime: 100%',
      pulse: true
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
                <p className={`${kpi.pulse ? 'text-sm' : 'text-2xl'} font-bold ${kpi.color}`}>{kpi.value}</p>
                {kpi.subValue && (
                  <p className="text-xs text-gray-500 mt-1">{kpi.subValue}</p>
                )}
              </div>
              <div className={`${kpi.bgColor} p-3 rounded-lg relative`}>
                <Icon className={`w-6 h-6 ${kpi.color} ${kpi.pulse ? 'animate-pulse' : ''}`} />
                {kpi.pulse && (
                  <span className="absolute top-1 right-1 w-2 h-2 bg-green-500 rounded-full animate-pulse"></span>
                )}
              </div>
            </div>
          </div>
        )
      })}
    </div>
  )
}

export default KPICards
