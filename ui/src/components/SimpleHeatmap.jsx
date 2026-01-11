import { useEffect, useState } from 'react'
import { MapContainer, TileLayer, CircleMarker, Popup, useMap } from 'react-leaflet'
import L from 'leaflet'
import PropTypes from 'prop-types'
import 'leaflet/dist/leaflet.css'
import 'leaflet.heat'
import IndicatorLegend from './IndicatorLegend'
import LayerToggle from './LayerToggle'
import ClimateStressLayer from './ClimateStressLayer'
import { NIGERIA_LGA_COORDS, NIGERIA_CENTER, MAP_CONFIG, RISK_COLORS, CIRCLE_RADIUS, RISK_THRESHOLDS, INDICATOR_THRESHOLDS } from '../constants'

const MiningZonesLayer = ({ enabled, onZonesLoaded }) => {
  const map = useMap()

  useEffect(() => {
    if (!enabled) return

    let geoJsonLayer = null

    fetch('/data/mining_zones.geojson')
      .then(response => response.json())
      .then(data => {
        geoJsonLayer = L.geoJSON(data, {
          style: () => ({
            fillColor: '#FFA500',
            fillOpacity: 0.3,
            color: '#FF8C00',
            weight: 2,
            opacity: 0.6
          }),
          onEachFeature: (feature, layer) => {
            layer.on({
              mouseover: (e) => {
                const layer = e.target
                layer.setStyle({
                  fillOpacity: 0.5,
                  weight: 3
                })
                
                const popup = L.popup()
                  .setLatLng(e.latlng)
                  .setContent(`
                    <div class="bg-amber-900/90 text-white p-3 rounded-lg border border-amber-500">
                      <div class="font-bold text-sm mb-1 flex items-center gap-2">
                        <span class="text-lg">⚠️</span>
                        <span>ALERT: High Mining Density</span>
                      </div>
                      <div class="text-xs space-y-1">
                        <div><span class="font-semibold">State:</span> ${feature.properties.state}</div>
                        <div><span class="font-semibold">Mineral:</span> ${feature.properties.mineral}</div>
                        <div><span class="font-semibold">Risk:</span> ${feature.properties.risk_type}</div>
                        <div class="mt-2 pt-2 border-t border-amber-600 text-amber-200">
                          Resource-Driven Conflict Risk
                        </div>
                      </div>
                    </div>
                  `)
                  .openOn(map)
              },
              mouseout: (e) => {
                const layer = e.target
                layer.setStyle({
                  fillOpacity: 0.3,
                  weight: 2
                })
                map.closePopup()
              }
            })
          }
        }).addTo(map)

        if (onZonesLoaded) {
          onZonesLoaded(data.features)
        }
      })
      .catch(error => {
        console.error('Error loading mining zones:', error)
      })

    return () => {
      if (geoJsonLayer) {
        map.removeLayer(geoJsonLayer)
      }
    }
  }, [map, enabled, onZonesLoaded])

  return null
}

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

const SimpleHeatmap = ({ signals, onMapReady, onSignalClick, layers, onLayerChange, onMiningZonesUpdate }) => {
  const [miningZones, setMiningZones] = useState([])
  const [signalsInMiningZones, setSignalsInMiningZones] = useState(new Set())

  // Check if a point is inside a polygon using ray casting algorithm
  const isPointInPolygon = (point, polygon) => {
    const [lng, lat] = point
    let inside = false
    
    for (let i = 0, j = polygon.length - 1; i < polygon.length; j = i++) {
      const [xi, yi] = polygon[i]
      const [xj, yj] = polygon[j]
      
      const intersect = ((yi > lat) !== (yj > lat)) &&
        (lng < (xj - xi) * (lat - yi) / (yj - yi) + xi)
      
      if (intersect) inside = !inside
    }
    
    return inside
  }

  // Detect spatial correlation between signals and mining zones
  useEffect(() => {
    if (!miningZones.length || !signalsArray.length) return

    const overlappingSignals = new Set()

    signalsArray.forEach((signal, idx) => {
      const coords = NIGERIA_LGA_COORDS[signal.lga] || NIGERIA_CENTER
      const point = [coords.lng, coords.lat]

      miningZones.forEach(zone => {
        if (zone.geometry.type === 'Polygon') {
          const polygon = zone.geometry.coordinates[0]
          if (isPointInPolygon(point, polygon)) {
            overlappingSignals.add(`${signal.state}-${signal.lga}-${idx}`)
          }
        }
      })
    })

    setSignalsInMiningZones(overlappingSignals)
    
    // Notify parent component about mining zone overlaps
    if (onMiningZonesUpdate) {
      onMiningZonesUpdate(overlappingSignals)
    }
  }, [miningZones, signals, onMiningZonesUpdate])

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

  const getIndicatorBadges = (signal, signalKey) => {
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
    // Add mining zone indicator if signal overlaps with mining zone
    if (signalsInMiningZones.has(signalKey)) {
      badges.push('💎')
    }
    return badges
  }

  const signalsArray = Array.isArray(signals) ? signals : []
  const heatmapPoints = signalsArray.map(signal => {
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
        <ClimateStressLayer enabled={layers?.climateStress !== false} />
        <MiningZonesLayer enabled={layers?.mining !== false} onZonesLoaded={setMiningZones} />
        
        {/* Circle Markers for each signal */}
        {layers?.markers !== false && signalsArray.map((signal, idx) => {
          const coords = NIGERIA_LGA_COORDS[signal.lga] || NIGERIA_CENTER
          const signalKey = `${signal.state}-${signal.lga}-${idx}`
          const badges = getIndicatorBadges(signal, signalKey)
          const isInMiningZone = signalsInMiningZones.has(signalKey)
          
          return (
            <CircleMarker
              key={signalKey}
              center={[coords.lat, coords.lng]}
              radius={getCircleRadius(signal.risk_score)}
              fillColor={getCircleColor(signal.risk_score)}
              color={isInMiningZone ? "#FFA500" : "#ffffff"}
              weight={isInMiningZone ? 4 : 2}
              opacity={0.9}
              fillOpacity={0.7}
              className={isInMiningZone ? 'mining-zone-glow' : ''}
              eventHandlers={{
                click: () => {
                  if (onSignalClick) {
                    onSignalClick({
                      ...signal,
                      inMiningZone: isInMiningZone,
                      miningZoneAlert: isInMiningZone ? 'Conflict likely fueled by illicit mineral trade' : null
                    })
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
                    {isInMiningZone && (
                      <div className="mt-2 p-2 bg-amber-100 border border-amber-400 rounded">
                        <div className="flex items-center gap-1 text-amber-900 font-semibold text-xs">
                          <span>💎</span>
                          <span>Mining Zone Alert</span>
                        </div>
                        <div className="text-xs text-amber-800 mt-1">
                          Conflict likely fueled by illicit mineral trade
                        </div>
                      </div>
                    )}
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
            <span className="text-white font-bold">{signalsArray.length}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-400">Hot Zones (≥80):</span>
            <span className="text-red-400 font-bold animate-pulse">
              {signalsArray.filter(s => s.risk_score >= RISK_THRESHOLDS.CRITICAL).length}
            </span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-400">States Affected:</span>
            <span className="text-white font-bold">
              {new Set(signalsArray.map(s => s.state)).size}
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
    climateStress: PropTypes.bool,
    mining: PropTypes.bool,
    border: PropTypes.bool
  }),
  onLayerChange: PropTypes.func,
  onMiningZonesUpdate: PropTypes.func
}

export default SimpleHeatmap
