import { useState } from 'react'
import PropTypes from 'prop-types'

const LayerToggle = ({ layers, onLayerChange }) => {
  const [isExpanded, setIsExpanded] = useState(false)
  
  const toggleLayer = (layerName) => {
    const newLayers = { ...layers, [layerName]: !layers[layerName] }
    if (onLayerChange) {
      onLayerChange(newLayers)
    }
  }
  
  return (
    <div className="absolute top-20 right-4 z-[1000]">
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        aria-label="Toggle map layers"
        aria-expanded={isExpanded}
        className="glassmorphism px-3 py-2 rounded-lg text-white hover:bg-white/20 transition-all duration-300 flex items-center gap-2 border border-white/20 mb-2"
      >
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
        </svg>
        Layers
      </button>
      
      {isExpanded && (
        <div className="glassmorphism rounded-lg border border-white/20 p-3 min-w-[200px]">
          <div className="text-xs font-bold text-white mb-2">MAP LAYERS</div>
          <div className="space-y-2">
            <label className="flex items-center gap-2 cursor-pointer text-sm text-gray-200 hover:text-white">
              <input
                type="checkbox"
                checked={layers.heatmap}
                onChange={() => toggleLayer('heatmap')}
                className="w-4 h-4 rounded"
              />
              <span>Risk Heatmap</span>
            </label>
            <label className="flex items-center gap-2 cursor-pointer text-sm text-gray-200 hover:text-white">
              <input
                type="checkbox"
                checked={layers.markers}
                onChange={() => toggleLayer('markers')}
                className="w-4 h-4 rounded"
              />
              <span>Event Markers</span>
            </label>
            <div className="border-t border-gray-600 my-2"></div>
            <div className="text-xs font-semibold text-gray-400 mb-1">INDICATORS</div>
            <label className="flex items-center gap-2 cursor-pointer text-sm text-gray-200 hover:text-white">
              <input
                type="checkbox"
                checked={layers.climate}
                onChange={() => toggleLayer('climate')}
                className="w-4 h-4 rounded"
              />
              <span>🌊 Climate</span>
            </label>
            <label className="flex items-center gap-2 cursor-pointer text-sm text-gray-200 hover:text-white">
              <input
                type="checkbox"
                checked={layers.mining}
                onChange={() => toggleLayer('mining')}
                className="w-4 h-4 rounded"
              />
              <span>⛏️ Mining</span>
            </label>
            <label className="flex items-center gap-2 cursor-pointer text-sm text-gray-200 hover:text-white">
              <input
                type="checkbox"
                checked={layers.border}
                onChange={() => toggleLayer('border')}
                className="w-4 h-4 rounded"
              />
              <span>🚨 Border</span>
            </label>
          </div>
        </div>
      )}
    </div>
  )
}

LayerToggle.propTypes = {
  layers: PropTypes.shape({
    heatmap: PropTypes.bool,
    markers: PropTypes.bool,
    climate: PropTypes.bool,
    mining: PropTypes.bool,
    border: PropTypes.bool
  }).isRequired,
  onLayerChange: PropTypes.func.isRequired
}

export default LayerToggle
