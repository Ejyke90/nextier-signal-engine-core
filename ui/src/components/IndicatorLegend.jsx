import { memo } from 'react'
import { INDICATOR_THRESHOLDS } from '../constants'

const IndicatorLegend = memo(() => {
  return (
    <div className="absolute bottom-24 left-4 bg-gray-900/90 backdrop-blur-md border border-gray-700 rounded-lg p-3 z-[1000] max-w-xs">
      <div className="text-xs font-bold text-white mb-2">📊 INDICATOR LEGEND</div>
      <div className="space-y-1.5 text-xs">
        <div className="flex items-center gap-2">
          <span className="w-4 h-4 rounded-full bg-blue-500 flex items-center justify-center text-[10px]">🌊</span>
          <span className="text-gray-300">Climate Risk (Flooding &gt;{INDICATOR_THRESHOLDS.FLOOD_INUNDATION}%)</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="w-4 h-4 rounded-full bg-amber-500 flex items-center justify-center text-[10px]">⛏️</span>
          <span className="text-gray-300">Mining Proximity (&lt;{INDICATOR_THRESHOLDS.MINING_PROXIMITY_KM}km)</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="w-4 h-4 rounded-full bg-red-500 flex items-center justify-center text-[10px]">🚨</span>
          <span className="text-gray-300">High Border Activity</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="w-4 h-4 rounded-full bg-blue-400 flex items-center justify-center text-[10px] animate-pulse">🛡️</span>
          <span className="text-gray-300">Verified Pulse (Multi-Source)</span>
        </div>
      </div>
    </div>
  )
})

IndicatorLegend.displayName = 'IndicatorLegend'

export default IndicatorLegend
