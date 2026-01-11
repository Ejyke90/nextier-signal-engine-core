import { memo } from 'react'
import PropTypes from 'prop-types'
import { INDICATOR_THRESHOLDS } from '../constants'

const IndicatorBadge = memo(({ signal }) => {
  const hasClimate = signal.flood_inundation_index && signal.flood_inundation_index > INDICATOR_THRESHOLDS.FLOOD_INUNDATION
  const hasMining = signal.mining_proximity_km && signal.mining_proximity_km < INDICATOR_THRESHOLDS.MINING_PROXIMITY_KM
  const hasBorder = signal.border_activity && ['High', 'Critical'].includes(signal.border_activity)
  
  if (!hasClimate && !hasMining && !hasBorder) return null
  
  return (
    <div className="absolute -top-1 -right-1 flex gap-0.5">
      {hasClimate && (
        <span 
          className="w-4 h-4 rounded-full bg-blue-500 flex items-center justify-center text-[10px] border border-white shadow-sm"
          title={`Flooding: ${signal.flood_inundation_index?.toFixed(1)}% inundation`}
        >
          🌊
        </span>
      )}
      {hasMining && (
        <span 
          className="w-4 h-4 rounded-full bg-amber-500 flex items-center justify-center text-[10px] border border-white shadow-sm"
          title={`Mining: ${signal.mining_proximity_km?.toFixed(1)}km from ${signal.mining_site_name}`}
        >
          ⛏️
        </span>
      )}
      {hasBorder && (
        <span 
          className="w-4 h-4 rounded-full bg-red-500 flex items-center justify-center text-[10px] border border-white shadow-sm animate-pulse"
          title={`Border Activity: ${signal.border_activity} - ${signal.group_affiliation}`}
        >
          🚨
        </span>
      )}
    </div>
  )
})

IndicatorBadge.displayName = 'IndicatorBadge'

IndicatorBadge.propTypes = {
  signal: PropTypes.shape({
    flood_inundation_index: PropTypes.number,
    mining_proximity_km: PropTypes.number,
    mining_site_name: PropTypes.string,
    border_activity: PropTypes.string,
    group_affiliation: PropTypes.string
  }).isRequired
}

export default IndicatorBadge
