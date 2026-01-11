import { useMemo } from 'react'
import PropTypes from 'prop-types'
import { AlertTriangle, Shield, Droplets } from 'lucide-react'

const PolicymakerAlert = ({ signals }) => {
  // Ensure signals is always an array
  const signalsArray = Array.isArray(signals) ? signals : []
  
  const criticalAlerts = useMemo(() => {
    if (!signalsArray || signalsArray.length === 0) return []

    return signalsArray
      .filter(signal => {
        const highRisk = signal.risk_score > 80
        const climateStress = signal.climate_recession_index && signal.climate_recession_index > 0.8
        const farmerHerder = signal.is_farmer_herder_conflict
        
        return highRisk && climateStress && farmerHerder
      })
      .map(signal => ({
        ...signal,
        alertType: 'INTERVENTION_REQUIRED',
        priority: 'CRITICAL',
        recommendation: 'Resource mediation required to prevent Farmer-Herder escalation'
      }))
  }, [signalsArray])

  const highImpactClimateZones = useMemo(() => {
    if (!signalsArray || signalsArray.length === 0) return []

    return signalsArray
      .filter(signal => {
        const highRisk = signal.risk_score > 80
        const highImpactZone = signal.climate_zone_region && signal.climate_impact_zone === 'High'
        
        return highRisk && highImpactZone
      })
      .map(signal => ({
        ...signal,
        alertType: 'CLIMATE_CONFLICT',
        priority: 'HIGH',
        recommendation: 'Climate adaptation and resource management intervention needed'
      }))
  }, [signalsArray])

  const allAlerts = [...criticalAlerts, ...highImpactClimateZones]

  if (allAlerts.length === 0) {
    return null
  }

  return (
    <div className="space-y-3">
      {allAlerts.map((alert, idx) => (
        <div
          key={`${alert.state}-${alert.lga}-${idx}`}
          className={`
            border-2 rounded-lg p-4 shadow-lg backdrop-blur-sm
            ${alert.priority === 'CRITICAL' 
              ? 'bg-red-900/90 border-red-500 animate-pulse' 
              : 'bg-orange-900/90 border-orange-500'
            }
          `}
        >
          <div className="flex items-start gap-3">
            <div className="flex-shrink-0 mt-1">
              {alert.alertType === 'INTERVENTION_REQUIRED' ? (
                <AlertTriangle className="w-6 h-6 text-red-300" />
              ) : (
                <Droplets className="w-6 h-6 text-orange-300" />
              )}
            </div>
            
            <div className="flex-1 space-y-2">
              <div className="flex items-center justify-between">
                <div className="font-bold text-white text-sm">
                  {alert.priority === 'CRITICAL' ? '🚨 CRITICAL ALERT' : '⚠️ HIGH PRIORITY ALERT'}
                </div>
                <div className="text-xs text-gray-300 bg-black/30 px-2 py-1 rounded">
                  Risk Score: {alert.risk_score.toFixed(1)}
                </div>
              </div>

              <div className="text-white text-sm">
                <div className="font-semibold mb-1">
                  {alert.state} - {alert.lga}
                </div>
                <div className="text-xs text-gray-200">
                  {alert.event_type} | {alert.severity}
                </div>
              </div>

              {alert.climate_zone_region && (
                <div className="bg-black/30 rounded p-2 text-xs space-y-1">
                  <div className="text-orange-200">
                    <span className="font-semibold">Climate Zone:</span> {alert.climate_zone_region}
                  </div>
                  {alert.climate_recession_index && (
                    <div className="text-orange-200">
                      <span className="font-semibold">Recession Index:</span> {(alert.climate_recession_index * 100).toFixed(0)}%
                    </div>
                  )}
                </div>
              )}

              <div className="flex items-start gap-2 bg-white/10 rounded p-2">
                <Shield className="w-4 h-4 text-green-300 flex-shrink-0 mt-0.5" />
                <div className="text-xs text-white">
                  <div className="font-semibold mb-1">RECOMMENDED ACTION:</div>
                  <div className="text-gray-200">{alert.recommendation}</div>
                </div>
              </div>

              {alert.trigger_reason && (
                <div className="text-xs text-gray-300 border-t border-white/20 pt-2">
                  {alert.trigger_reason}
                </div>
              )}
            </div>
          </div>
        </div>
      ))}

      <div className="bg-gray-900/90 border border-gray-700 rounded-lg p-3 text-xs text-gray-300">
        <div className="flex items-center gap-2 mb-2">
          <span className="text-yellow-400">ℹ️</span>
          <span className="font-semibold text-white">Alert Criteria</span>
        </div>
        <ul className="space-y-1 ml-5 list-disc">
          <li>Risk Score &gt; 80 AND Recession Index &gt; 0.8</li>
          <li>Farmer-Herder conflict patterns detected</li>
          <li>High impact climate stress zones</li>
        </ul>
      </div>
    </div>
  )
}

PolicymakerAlert.propTypes = {
  signals: PropTypes.arrayOf(PropTypes.shape({
    state: PropTypes.string,
    lga: PropTypes.string,
    risk_score: PropTypes.number,
    event_type: PropTypes.string,
    severity: PropTypes.string,
    climate_zone_region: PropTypes.string,
    climate_recession_index: PropTypes.number,
    climate_impact_zone: PropTypes.string,
    is_farmer_herder_conflict: PropTypes.bool,
    trigger_reason: PropTypes.string
  }))
}

export default PolicymakerAlert
