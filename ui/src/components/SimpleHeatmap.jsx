import { useEffect } from 'react'
import { MapContainer, TileLayer, CircleMarker, Popup, useMap } from 'react-leaflet'
import L from 'leaflet'
import PropTypes from 'prop-types'
import 'leaflet/dist/leaflet.css'
import 'leaflet.heat'
import IndicatorLegend from './IndicatorLegend'
import LayerToggle from './LayerToggle'
import { NIGERIA_LGA_COORDS, NIGERIA_CENTER, MAP_CONFIG, RISK_COLORS, CIRCLE_RADIUS, RISK_THRESHOLDS, INDICATOR_THRESHOLDS } from '../constants'

const HeatmapLayer = ({ points }) => {
  const map = useMap()

  useEffect(() => {
    if (!points || points.length === 0) return

    const heatPoints = points.map(point => [
      point.lat,
      point.lng,
      point.intensity
    ])

    const heat = L.heatLayer(heatPoints, {
      radius: 25,
      blur: 15,
      maxZoom: 17,
      max: 1.0,
      minOpacity: 0.4,
      gradient: {
        0.0: 'rgba(0, 255, 255, 0)',
        0.2: 'rgba(0, 255, 255, 0.4)',
        0.4: 'rgba(0, 255, 255, 0.7)',
        0.6: 'rgba(255, 255, 0, 0.8)',
        0.8: 'rgba(255, 165, 0, 0.9)',
        1.0: 'rgba(220, 20, 60, 1)'
      }
    })
    
    heat.addTo(map)
    
    // Patch canvas context after layer is added to suppress performance warning
    setTimeout(() => {
      if (heat._canvas) {
        const oldGetContext = heat._canvas.getContext.bind(heat._canvas)
        heat._canvas.getContext = function(type, attributes) {
          return oldGetContext(type, { ...attributes, willReadFrequently: true })
        }
      }
    }, 0)

    return () => {
      map.removeLayer(heat)
    }
  }, [map, points])

  return null
}

const SimpleHeatmap = ({ signals, onMapReady, onSignalClick, layers, onLayerChange }) => {
  const getCircleColor = (riskScore) => {
    if (riskScore >= RISK_THRESHOLDS.CRITICAL) return RISK_COLORS.CRITICAL
    if (riskScore >= RISK_THRESHOLDS.HIGH) return RISK_COLORS.HIGH
    if (riskScore >= RISK_THRESHOLDS.MEDIUM) return RISK_COLORS.MEDIUM
    return RISK_COLORS.LOW
  }

  const getCircleRadius = (riskScore) => {
    if (riskScore >= RISK_THRESHOLDS.CRITICAL) return CIRCLE_RADIUS.CRITICAL
    if (riskScore >= RISK_THRESHOLDS.HIGH) return CIRCLE_RADIUS.HIGH
    if (riskScore >= RISK_THRESHOLDS.MEDIUM) return CIRCLE_RADIUS.MEDIUM
    return CIRCLE_RADIUS.LOW
  }

  const getIndicatorBadges = (signal) => {
    const badges = []
    if (layers?.climate && signal.flood_inundation_index && signal.flood_inundation_index > INDICATOR_THRESHOLDS.FLOOD_INUNDATION) {
      badges.push('🌊')
    }
    if (layers?.mining && signal.mining_proximity_km && signal.mining_proximity_km < INDICATOR_THRESHOLDS.MINING_PROXIMITY_KM) {
      badges.push('⛏️')
    }
    if (layers?.border && signal.border_activity && ['High', 'Critical'].includes(signal.border_activity)) {
      badges.push('🚨')
    }
    return badges
  }

  const heatmapPoints = signals.map(signal => {
    const coords = NIGERIA_LGA_COORDS[signal.lga] || NIGERIA_CENTER
    // Use veracity_score as multiplier for heatmap intensity
    // High-veracity events (multiple sources) appear sharper on the map
    const veracityMultiplier = signal.veracity_score || 0.5
    const baseIntensity = signal.risk_score / 100
    return {
      lat: coords.lat,
      lng: coords.lng,
      intensity: Math.min(1.0, baseIntensity * (1 + veracityMultiplier))
    }
  })

  return (
    <div className="relative w-full h-full">
      <MapContainer
        center={[NIGERIA_CENTER.lat, NIGERIA_CENTER.lng]}
        zoom={MAP_CONFIG.DEFAULT_ZOOM}
        style={{ height: '100%', width: '100%' }}
        zoomControl={true}
        whenReady={(map) => {
          if (onMapReady) {
            onMapReady(map.target)
          }
        }}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        {layers?.heatmap !== false && <HeatmapLayer points={heatmapPoints} />}
        
        {/* Circle Markers for each signal */}
        {layers?.markers !== false && signals.map((signal, idx) => {
          const coords = NIGERIA_LGA_COORDS[signal.lga] || NIGERIA_CENTER
          const badges = getIndicatorBadges(signal)
          return (
            <CircleMarker
              key={`${signal.state}-${signal.lga}-${idx}`}
              center={[coords.lat, coords.lng]}
              radius={getCircleRadius(signal.risk_score)}
              fillColor={getCircleColor(signal.risk_score)}
              color="#ffffff"
              weight={2}
              opacity={0.9}
              fillOpacity={0.7}
              eventHandlers={{
                click: () => {
                  if (onSignalClick) {
                    onSignalClick(signal)
                  }
                }
              }}
            >
              <Popup>
                <div className="text-gray-900 text-sm">
                  <div className="font-bold text-base mb-2 flex items-center gap-2">
                    <span>{signal.state} - {signal.lga}</span>
                    {badges.length > 0 && (
                      <span className="text-xs">{badges.join(' ')}</span>
                    )}
                  </div>
                  <div className="space-y-1">
                    <div><span className="font-semibold">Risk Score:</span> {signal.risk_score}</div>
                    <div><span className="font-semibold">Risk Level:</span> {signal.risk_level}</div>
                    <div><span className="font-semibold">Event Type:</span> {signal.event_type}</div>
                    <div><span className="font-semibold">Severity:</span> {signal.severity}</div>
                  </div>
                  <button
                    onClick={() => onSignalClick && onSignalClick(signal)}
                    className="mt-2 w-full bg-blue-600 text-white px-3 py-1 rounded text-xs hover:bg-blue-700"
                  >
                    View Full Details
                  </button>
                </div>
              </Popup>
            </CircleMarker>
          )
        })}
      </MapContainer>

      <IndicatorLegend />
      <LayerToggle layers={layers} onLayerChange={onLayerChange} />

      <div className="absolute top-4 left-4 bg-gray-900/80 backdrop-blur-md border border-gray-700 rounded-lg p-4 max-w-xs z-[1000]">
        <h4 className="text-sm font-bold text-white mb-3">🔥 CONFLICT HEATMAP</h4>
        <div className="space-y-2 text-xs">
          <div className="flex justify-between">
            <span className="text-gray-400">Total Signals:</span>
            <span className="text-white font-bold">{signals.length}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-400">Hot Zones (≥80):</span>
            <span className="text-red-400 font-bold animate-pulse">
              {signals.filter(s => s.risk_score >= RISK_THRESHOLDS.CRITICAL).length}
            </span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-400">States Affected:</span>
            <span className="text-white font-bold">
              {new Set(signals.map(s => s.state)).size}
            </span>
          </div>
        </div>
      </div>

      <div className="absolute bottom-4 left-4 right-4 bg-gray-900/80 backdrop-blur-md border border-gray-700 rounded-lg p-3 z-[1000]">
        <div className="flex items-center justify-between text-xs mb-2">
          <span className="font-bold text-white">CONFLICT DENSITY</span>
          <span className="text-gray-400">Safe → Hot</span>
        </div>
        <div className="flex items-center space-x-2 mb-3">
          <div className="flex-1 h-3 rounded-full" style={{
            background: 'linear-gradient(to right, rgba(0,255,255,0.4), rgba(0,255,255,0.7), rgba(255,255,0,0.8), rgba(255,165,0,0.9), rgba(220,20,60,1))'
          }}></div>
        </div>
        <div className="flex items-center justify-between text-xs">
          <div className="flex items-center space-x-4">
            <div className="flex items-center">
              <span className="w-3 h-3 bg-cyan-400 rounded-full mr-1.5"></span>
              Low
            </div>
            <div className="flex items-center">
              <span className="w-3 h-3 bg-yellow-400 rounded-full mr-1.5"></span>
              Medium
            </div>
            <div className="flex items-center">
              <span className="w-3 h-3 bg-orange-500 rounded-full mr-1.5"></span>
              High
            </div>
            <div className="flex items-center">
              <span className="w-3 h-3 bg-red-600 rounded-full mr-1.5 animate-pulse"></span>
              Critical
            </div>
          </div>
          <div className="font-semibold text-white">
            🇳🇬 774 LGAs | Free OSM
          </div>
        </div>
      </div>
    </div>
  )
}

SimpleHeatmap.propTypes = {
  signals: PropTypes.arrayOf(PropTypes.shape({
    state: PropTypes.string,
    lga: PropTypes.string,
    risk_score: PropTypes.number,
    risk_level: PropTypes.string,
    event_type: PropTypes.string,
    severity: PropTypes.string,
    flood_inundation_index: PropTypes.number,
    mining_proximity_km: PropTypes.number,
    border_activity: PropTypes.string,
    veracity_score: PropTypes.number
  })).isRequired,
  onMapReady: PropTypes.func,
  onSignalClick: PropTypes.func,
  layers: PropTypes.shape({
    heatmap: PropTypes.bool,
    markers: PropTypes.bool,
    climate: PropTypes.bool,
    mining: PropTypes.bool,
    border: PropTypes.bool
  }),
  onLayerChange: PropTypes.func
}

export default SimpleHeatmap
