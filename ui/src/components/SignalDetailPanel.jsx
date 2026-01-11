import PropTypes from 'prop-types'
import { RISK_THRESHOLDS } from '../constants'

const SignalDetailPanel = ({ signal, onClose }) => {
  if (!signal) return null
  
  return (
    <div className="fixed right-0 top-0 h-full w-96 bg-gray-900/95 backdrop-blur-md border-l border-gray-700 z-[2000] overflow-y-auto" role="dialog" aria-labelledby="signal-detail-title">
      <div className="p-6">
        {/* Header */}
        <div className="flex items-start justify-between mb-6">
          <div>
            <h2 id="signal-detail-title" className="text-xl font-bold text-white mb-1">Signal Details</h2>
            <p className="text-sm text-gray-400">{signal.state} - {signal.lga}</p>
          </div>
          <button
            onClick={onClose}
            aria-label="Close signal details panel"
            className="text-gray-400 hover:text-white transition-colors"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        
        {/* Risk Score Badge */}
        <div className={`mb-6 p-4 rounded-lg ${
          signal.risk_score >= RISK_THRESHOLDS.CRITICAL ? 'bg-red-900/50 border border-red-500' :
          signal.risk_score >= RISK_THRESHOLDS.HIGH ? 'bg-orange-900/50 border border-orange-500' :
          signal.risk_score >= RISK_THRESHOLDS.MEDIUM ? 'bg-yellow-900/50 border border-yellow-500' :
          'bg-blue-900/50 border border-blue-500'
        }`}>
          <div className="text-3xl font-bold text-white mb-1">{signal.risk_score}</div>
          <div className="text-sm text-gray-300">{signal.risk_level} Risk</div>
        </div>
        
        {/* Core Information */}
        <div className="mb-6">
          <h3 className="text-sm font-bold text-gray-400 uppercase mb-3">Core Information</h3>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-gray-400">Event Type:</span>
              <span className="text-white font-semibold capitalize">{signal.event_type}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">Severity:</span>
              <span className="text-white font-semibold capitalize">{signal.severity}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">Fuel Price:</span>
              <span className="text-white font-semibold">₦{signal.fuel_price}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">Inflation:</span>
              <span className="text-white font-semibold">{signal.inflation}%</span>
            </div>
          </div>
        </div>
        
        {/* Climate Indicators */}
        {(signal.flood_inundation_index || signal.precipitation_anomaly || signal.vegetation_health_index) && (
          <div className="mb-6">
            <h3 className="text-sm font-bold text-blue-400 uppercase mb-3 flex items-center gap-2">
              <span>🌊</span> Climate Indicators
            </h3>
            <div className="bg-blue-900/20 border border-blue-800 rounded-lg p-3 space-y-2 text-sm">
              {signal.flood_inundation_index && (
                <div className="flex justify-between">
                  <span className="text-gray-400">Flood Inundation:</span>
                  <span className="text-white font-semibold">{signal.flood_inundation_index?.toFixed(1) ?? 'N/A'}%</span>
                </div>
              )}
              {signal.precipitation_anomaly && (
                <div className="flex justify-between">
                  <span className="text-gray-400">Precipitation Anomaly:</span>
                  <span className="text-white font-semibold">{signal.precipitation_anomaly?.toFixed(1) ?? 'N/A'}%</span>
                </div>
              )}
              {signal.vegetation_health_index && (
                <div className="flex justify-between">
                  <span className="text-gray-400">Vegetation Health:</span>
                  <span className="text-white font-semibold">{((signal.vegetation_health_index ?? 0) * 100).toFixed(0)}%</span>
                </div>
              )}
              {signal.flood_inundation_index > 20 && (
                <div className="mt-2 pt-2 border-t border-blue-700">
                  <p className="text-xs text-blue-300">⚠️ High flooding increases resource competition and displacement risk</p>
                </div>
              )}
            </div>
          </div>
        )}
        
        {/* Mining Indicators */}
        {(signal.mining_proximity_km || signal.mining_site_name) && (
          <div className="mb-6">
            <h3 className="text-sm font-bold text-amber-400 uppercase mb-3 flex items-center gap-2">
              <span>⛏️</span> Mining Proximity
            </h3>
            <div className="bg-amber-900/20 border border-amber-800 rounded-lg p-3 space-y-2 text-sm">
              {signal.mining_site_name && (
                <div className="flex justify-between">
                  <span className="text-gray-400">Nearest Site:</span>
                  <span className="text-white font-semibold">{signal.mining_site_name}</span>
                </div>
              )}
              {signal.mining_proximity_km && (
                <div className="flex justify-between">
                  <span className="text-gray-400">Distance:</span>
                  <span className="text-white font-semibold">{signal.mining_proximity_km?.toFixed(1) ?? 'N/A'} km</span>
                </div>
              )}
              {signal.informal_taxation_rate && (
                <div className="flex justify-between">
                  <span className="text-gray-400">Informal Taxation:</span>
                  <span className="text-white font-semibold">{((signal.informal_taxation_rate ?? 0) * 100).toFixed(0)}%</span>
                </div>
              )}
              {signal.high_funding_potential && (
                <div className="mt-2 pt-2 border-t border-amber-700">
                  <p className="text-xs text-amber-300">⚠️ High funding potential - Event within 10km of mining site</p>
                </div>
              )}
            </div>
          </div>
        )}
        
        {/* Border Activity */}
        {(signal.border_activity || signal.lakurawa_presence) && (
          <div className="mb-6">
            <h3 className="text-sm font-bold text-red-400 uppercase mb-3 flex items-center gap-2">
              <span>🚨</span> Border Activity
            </h3>
            <div className="bg-red-900/20 border border-red-800 rounded-lg p-3 space-y-2 text-sm">
              {signal.border_activity && (
                <div className="flex justify-between">
                  <span className="text-gray-400">Activity Level:</span>
                  <span className={`font-semibold ${
                    signal.border_activity === 'Critical' ? 'text-red-400' :
                    signal.border_activity === 'High' ? 'text-orange-400' :
                    'text-yellow-400'
                  }`}>{signal.border_activity}</span>
                </div>
              )}
              {signal.group_affiliation && (
                <div className="flex justify-between">
                  <span className="text-gray-400">Group Affiliation:</span>
                  <span className="text-white font-semibold">{signal.group_affiliation}</span>
                </div>
              )}
              {signal.border_permeability_score && (
                <div className="flex justify-between">
                  <span className="text-gray-400">Border Permeability:</span>
                  <span className="text-white font-semibold">{((signal.border_permeability_score ?? 0) * 100).toFixed(0)}%</span>
                </div>
              )}
              {signal.lakurawa_presence && (
                <div className="mt-2 pt-2 border-t border-red-700">
                  <p className="text-xs text-red-300">⚠️ Lakurawa presence confirmed - Sahelian jihadist expansion</p>
                </div>
              )}
              {signal.sophisticated_ied_usage && (
                <div className="mt-1">
                  <p className="text-xs text-red-300">⚠️ Sophisticated IED usage detected</p>
                </div>
              )}
            </div>
          </div>
        )}
        
        {/* Trigger Reason */}
        {signal.trigger_reason && (
          <div className="mb-6">
            <h3 className="text-sm font-bold text-gray-400 uppercase mb-3">Analysis</h3>
            <div className="bg-gray-800/50 border border-gray-700 rounded-lg p-3">
              <p className="text-sm text-gray-300 leading-relaxed">{signal.trigger_reason}</p>
            </div>
          </div>
        )}
        
        {/* Source */}
        {signal.source_url && (
          <div>
            <h3 className="text-sm font-bold text-gray-400 uppercase mb-3">Source</h3>
            <a
              href={signal.source_url}
              target="_blank"
              rel="noopener noreferrer"
              className="text-sm text-blue-400 hover:text-blue-300 underline break-all"
            >
              {signal.source_title || signal.source_url}
            </a>
          </div>
        )}
      </div>
    </div>
  )
}

SignalDetailPanel.propTypes = {
  signal: PropTypes.shape({
    state: PropTypes.string,
    lga: PropTypes.string,
    risk_score: PropTypes.number,
    risk_level: PropTypes.string,
    event_type: PropTypes.string,
    severity: PropTypes.string,
    fuel_price: PropTypes.number,
    inflation: PropTypes.number,
    flood_inundation_index: PropTypes.number,
    precipitation_anomaly: PropTypes.number,
    vegetation_health_index: PropTypes.number,
    mining_proximity_km: PropTypes.number,
    mining_site_name: PropTypes.string,
    informal_taxation_rate: PropTypes.number,
    high_funding_potential: PropTypes.bool,
    border_activity: PropTypes.string,
    group_affiliation: PropTypes.string,
    border_permeability_score: PropTypes.number,
    lakurawa_presence: PropTypes.bool,
    sophisticated_ied_usage: PropTypes.bool,
    trigger_reason: PropTypes.string,
    source_url: PropTypes.string,
    source_title: PropTypes.string
  }),
  onClose: PropTypes.func.isRequired
}

export default SignalDetailPanel
