import { useState, useEffect } from 'react'
import { Activity, Clock, CheckCircle, AlertCircle } from 'lucide-react'

const SystemHeartbeat = () => {
  const [schedulerStatus, setSchedulerStatus] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetchSchedulerStatus()
    const interval = setInterval(fetchSchedulerStatus, 10000) // Update every 10 seconds
    return () => clearInterval(interval)
  }, [])

  const fetchSchedulerStatus = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/v1/scheduler/status')
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      const data = await response.json()
      setSchedulerStatus(data)
      setError(null)
      setLoading(false)
    } catch (err) {
      console.error('Error fetching scheduler status:', err)
      setError(err.message)
      setLoading(false)
    }
  }

  const formatTime = (isoString) => {
    if (!isoString) return 'N/A'
    const date = new Date(isoString)
    return date.toLocaleTimeString('en-US', { 
      hour: '2-digit', 
      minute: '2-digit',
      second: '2-digit'
    })
  }

  const getTimeUntilNext = (nextRunIso) => {
    if (!nextRunIso) return 'N/A'
    const now = new Date()
    const nextRun = new Date(nextRunIso)
    const diffMs = nextRun - now
    
    if (diffMs < 0) return 'Running...'
    
    const minutes = Math.floor(diffMs / 60000)
    const seconds = Math.floor((diffMs % 60000) / 1000)
    
    return `${minutes}m ${seconds}s`
  }

  if (loading) {
    return (
      <div className="flex items-center gap-2 px-4 py-2 glassmorphism rounded-lg">
        <Activity className="w-4 h-4 text-blue-400 animate-pulse" />
        <span className="text-sm text-gray-400">Loading...</span>
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex items-center gap-2 px-4 py-2 glassmorphism rounded-lg border border-red-500/30">
        <AlertCircle className="w-4 h-4 text-red-400" />
        <span className="text-sm text-red-400">Scheduler Offline</span>
      </div>
    )
  }

  const isActive = schedulerStatus?.status === 'active' && schedulerStatus?.scheduler_running

  return (
    <div className="flex items-center gap-4">
      {/* Status Indicator */}
      <div className={`flex items-center gap-2 px-4 py-2 glassmorphism rounded-lg border ${
        isActive ? 'border-green-500/30' : 'border-yellow-500/30'
      }`}>
        {isActive ? (
          <>
            <Activity className="w-4 h-4 text-green-400 animate-pulse" />
            <span className="text-sm font-semibold text-green-400">System Active</span>
          </>
        ) : (
          <>
            <AlertCircle className="w-4 h-4 text-yellow-400" />
            <span className="text-sm font-semibold text-yellow-400">System Inactive</span>
          </>
        )}
      </div>

      {/* Next Scheduled Scrape */}
      {isActive && schedulerStatus?.next_run && (
        <div className="flex items-center gap-2 px-4 py-2 glassmorphism rounded-lg">
          <Clock className="w-4 h-4 text-cyan-400" />
          <div className="flex flex-col">
            <span className="text-xs text-gray-400">Next Scrape</span>
            <span className="text-sm font-semibold text-cyan-400">
              {getTimeUntilNext(schedulerStatus.next_run)}
            </span>
          </div>
        </div>
      )}

      {/* Last Successful Sync */}
      {isActive && schedulerStatus?.last_run && (
        <div className="flex items-center gap-2 px-4 py-2 glassmorphism rounded-lg">
          <CheckCircle className="w-4 h-4 text-emerald-400" />
          <div className="flex flex-col">
            <span className="text-xs text-gray-400">Last Sync</span>
            <span className="text-sm font-semibold text-emerald-400">
              {formatTime(schedulerStatus.last_run)}
            </span>
          </div>
        </div>
      )}

      {/* Schedule Info */}
      {isActive && schedulerStatus?.schedule && (
        <div className="flex items-center gap-2 px-3 py-2 glassmorphism rounded-lg border border-blue-500/20">
          <span className="text-xs text-blue-400 font-mono">
            {schedulerStatus.schedule}
          </span>
        </div>
      )}
    </div>
  )
}

export default SystemHeartbeat
