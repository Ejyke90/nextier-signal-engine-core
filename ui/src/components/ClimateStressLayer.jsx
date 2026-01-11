import { useEffect } from 'react'
import { useMap } from 'react-leaflet'
import L from 'leaflet'
import PropTypes from 'prop-types'

const ClimateStressLayer = ({ enabled }) => {
  const map = useMap()

  useEffect(() => {
    if (!enabled) return

    let geoJsonLayer = null

    fetch('/data/climate_indicators.geojson')
      .then(response => response.json())
      .then(data => {
        geoJsonLayer = L.geoJSON(data, {
          style: (feature) => {
            const recessionIndex = feature.properties.recession_index || 0
            const impactZone = feature.properties.impact_zone || 'Unknown'
            
            let fillColor = '#8B4513'
            let fillOpacity = 0.2
            
            if (impactZone === 'High') {
              fillColor = '#D2691E'
              fillOpacity = 0.4 + (recessionIndex * 0.3)
            } else if (impactZone === 'Medium-High') {
              fillColor = '#CD853F'
              fillOpacity = 0.3 + (recessionIndex * 0.2)
            } else if (impactZone === 'Medium') {
              fillColor = '#DEB887'
              fillOpacity = 0.2 + (recessionIndex * 0.15)
            }
            
            return {
              fillColor: fillColor,
              fillOpacity: fillOpacity,
              color: '#8B4513',
              weight: 2,
              opacity: 0.6,
              dashArray: '5, 5'
            }
          },
          onEachFeature: (feature, layer) => {
            const props = feature.properties
            
            layer.on({
              mouseover: (e) => {
                const layer = e.target
                layer.setStyle({
                  fillOpacity: 0.7,
                  weight: 3,
                  dashArray: ''
                })
                
                const popup = L.popup()
                  .setLatLng(e.latlng)
                  .setContent(`
                    <div class="bg-amber-900/95 text-white p-3 rounded-lg border-2 border-orange-500 shadow-lg">
                      <div class="font-bold text-sm mb-2 flex items-center gap-2">
                        <span class="text-lg">🌡️</span>
                        <span>CLIMATE STRESS ZONE</span>
                      </div>
                      <div class="text-xs space-y-1.5">
                        <div class="bg-amber-800/50 p-2 rounded">
                          <div><span class="font-semibold">Region:</span> ${props.region}</div>
                          <div><span class="font-semibold">Indicator:</span> ${props.indicator}</div>
                        </div>
                        <div class="bg-orange-900/50 p-2 rounded">
                          <div><span class="font-semibold">Recession Index:</span> ${(props.recession_index * 100).toFixed(0)}%</div>
                          <div><span class="font-semibold">Impact Zone:</span> <span class="font-bold text-orange-300">${props.impact_zone}</span></div>
                        </div>
                        <div class="mt-2 pt-2 border-t border-orange-600 text-orange-200 text-xs">
                          <div class="font-semibold mb-1">⚠️ Conflict Driver:</div>
                          <div class="italic">${props.conflict_correlation}</div>
                        </div>
                      </div>
                    </div>
                  `)
                  .openOn(map)
              },
              mouseout: (e) => {
                const layer = e.target
                const recessionIndex = feature.properties.recession_index || 0
                const impactZone = feature.properties.impact_zone || 'Unknown'
                
                let fillOpacity = 0.2
                if (impactZone === 'High') {
                  fillOpacity = 0.4 + (recessionIndex * 0.3)
                } else if (impactZone === 'Medium-High') {
                  fillOpacity = 0.3 + (recessionIndex * 0.2)
                } else if (impactZone === 'Medium') {
                  fillOpacity = 0.2 + (recessionIndex * 0.15)
                }
                
                layer.setStyle({
                  fillOpacity: fillOpacity,
                  weight: 2,
                  dashArray: '5, 5'
                })
                map.closePopup()
              }
            })
          }
        }).addTo(map)
      })
      .catch(error => {
        console.error('Error loading climate indicators:', error)
      })

    return () => {
      if (geoJsonLayer) {
        map.removeLayer(geoJsonLayer)
      }
    }
  }, [map, enabled])

  return null
}

ClimateStressLayer.propTypes = {
  enabled: PropTypes.bool.isRequired
}

export default ClimateStressLayer
