import { useState, useEffect } from 'react'
import Toast from './Toast'

const HighRiskAlertMonitor = () => {
  const [alerts, setAlerts] = useState([])
  const [displayedAlerts, setDisplayedAlerts] = useState(new Set())
  const [currentAlert, setCurrentAlert] = useState(null)

  useEffect(() => {
    fetchHighRiskAlerts()
    const interval = setInterval(fetchHighRiskAlerts, 5000) // Poll every 5 seconds
    return () => clearInterval(interval)
  }, [])

  const fetchHighRiskAlerts = async () => {
    try {
      const response = await fetch('/data/high_risk_alerts.json')
      if (!response.ok) {
        return
      }
      const data = await response.json()
      
      if (Array.isArray(data) && data.length > 0) {
        // Get the latest alert
        const latestAlert = data[data.length - 1]
        const alertId = latestAlert.timestamp
        
        // Only show if we haven't displayed this alert yet
        if (!displayedAlerts.has(alertId)) {
          setCurrentAlert(latestAlert)
          setDisplayedAlerts(prev => new Set([...prev, alertId]))
          
          // Keep only last 50 alert IDs in memory
          if (displayedAlerts.size > 50) {
            const newSet = new Set([...displayedAlerts])
            const firstItem = newSet.values().next().value
            newSet.delete(firstItem)
            setDisplayedAlerts(newSet)
          }
        }
      }
    } catch (err) {
      // Silently fail - file might not exist yet
      console.debug('High-risk alerts file not available yet')
    }
  }

  const handleCloseAlert = () => {
    setCurrentAlert(null)
  }

  if (!currentAlert) {
    return null
  }

  const alertMessage = `🚨 HIGH-RISK ALERT: ${currentAlert.count} critical article${currentAlert.count > 1 ? 's' : ''} detected with risk score > 85. ${currentAlert.articles?.[0]?.title || 'Check dashboard for details.'}`

  return (
    <Toast
      message={alertMessage}
      type="warning"
      onClose={handleCloseAlert}
      duration={10000}
    />
  )
}

export default HighRiskAlertMonitor
