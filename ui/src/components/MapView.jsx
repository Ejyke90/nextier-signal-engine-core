import { useEffect, useRef, useState } from 'react'
import maplibregl from 'maplibre-gl'
import 'maplibre-gl/dist/maplibre-gl.css'
import { Satellite, Map as MapIcon } from 'lucide-react'

const MapView = ({ signals, onMapLoad }) => {
  const mapContainer = useRef(null)
  const map = useRef(null)
  const markers = useRef([])
  const [mapStyle, setMapStyle] = useState('dark')
  const [mapLoaded, setMapLoaded] = useState(false)

  useEffect(() => {
    if (map.current) return

    map.current = new maplibregl.Map({
      container: mapContainer.current,
      style: 'https://tiles.openfreemap.org/styles/dark',
      center: [8.6753, 9.0820],
      zoom: 6,
      attributionControl: true,
      failIfMajorPerformanceCaveat: false
    })

    map.current.addControl(new maplibregl.NavigationControl(), 'top-right')
    map.current.addControl(new maplibregl.FullscreenControl(), 'top-right')

    map.current.on('error', (e) => {
      console.error('Map error:', e)
    })

    map.current.on('styledata', () => {
      console.log('Map style loaded successfully')
    })

    map.current.on('load', () => {
      console.log('Map loaded successfully')
      setMapLoaded(true)
      onMapLoad(map.current)
      
      map.current.addSource('conflict-source', {
        type: 'geojson',
        data: {
          type: 'FeatureCollection',
          features: []
        }
      })

      // HEATMAP LAYER - Conflict Density Visualization
      map.current.addLayer({
        id: 'conflict-heatmap',
        type: 'heatmap',
        source: 'conflict-source',
        maxzoom: 15,
        paint: {
          // Weight based on risk_score
          'heatmap-weight': [
            'interpolate',
            ['linear'],
            ['get', 'risk_score'],
            0, 0,
            50, 0.5,
            80, 0.8,
            100, 1
          ],
          // Intensity increases with zoom
          'heatmap-intensity': [
            'interpolate',
            ['linear'],
            ['zoom'],
            0, 1,
            15, 3
          ],
          // Color ramp: transparent -> cyan -> yellow -> crimson
          'heatmap-color': [
            'interpolate',
            ['linear'],
            ['heatmap-density'],
            0, 'rgba(0, 0, 255, 0)',
            0.2, 'rgba(0, 255, 255, 0.4)',
            0.4, 'rgba(0, 255, 255, 0.7)',
            0.6, 'rgba(255, 255, 0, 0.8)',
            0.8, 'rgba(255, 165, 0, 0.9)',
            1, 'rgba(220, 20, 60, 1)'
          ],
          // Radius grows with zoom for visual clarity
          'heatmap-radius': [
            'interpolate',
            ['linear'],
            ['zoom'],
            0, 2,
            6, 20,
            10, 40,
            15, 60
          ],
          // Fade out heatmap at higher zoom levels
          'heatmap-opacity': [
            'interpolate',
            ['linear'],
            ['zoom'],
            7, 1,
            9, 0.5,
            10, 0.3
          ]
        }
      })

      // TACTICAL CIRCLE LAYER - Appears at zoom > 8
      map.current.addLayer({
        id: 'conflict-circles',
        type: 'circle',
        source: 'conflict-source',
        minzoom: 8,
        paint: {
          'circle-radius': [
            'interpolate',
            ['linear'],
            ['zoom'],
            8, 4,
            12, 8,
            16, 16
          ],
          'circle-color': [
            'interpolate',
            ['linear'],
            ['get', 'risk_score'],
            0, '#22c55e',
            40, '#eab308',
            60, '#f97316',
            80, '#ef4444',
            100, '#dc2626'
          ],
          'circle-opacity': 0.9,
          'circle-stroke-width': 2,
          'circle-stroke-color': '#ffffff',
          'circle-stroke-opacity': 0.8
        }
      })

      map.current.on('click', 'conflict-circles', (e) => {
        const coordinates = e.features[0].geometry.coordinates.slice()
        const properties = e.features[0].properties

        new maplibregl.Popup()
          .setLngLat(coordinates)
          .setHTML(`
            <div class="p-4 bg-gray-900 rounded-lg">
              <h3 class="font-bold text-lg mb-2 text-white">${properties.lga}, ${properties.state}</h3>
              <div class="space-y-1 text-sm">
                <div class="flex justify-between">
                  <span class="text-gray-400">Event Type:</span>
                  <span class="text-white font-semibold">${properties.event_type}</span>
                </div>
                <div class="flex justify-between">
                  <span class="text-gray-400">Risk Score:</span>
                  <span class="text-red-400 font-bold">${properties.risk_score}</span>
                </div>
                <div class="flex justify-between">
                  <span class="text-gray-400">Risk Level:</span>
                  <span class="text-orange-400">${properties.risk_level}</span>
                </div>
                <div class="flex justify-between">
                  <span class="text-gray-400">Severity:</span>
                  <span class="text-yellow-400">${properties.severity}</span>
                </div>
              </div>
            </div>
          `)
          .addTo(map.current)
      })

      map.current.on('mouseenter', 'conflict-circles', () => {
        map.current.getCanvas().style.cursor = 'pointer'
      })

      map.current.on('mouseleave', 'conflict-circles', () => {
        map.current.getCanvas().style.cursor = ''
      })
    })

    return () => {
      if (map.current) {
        map.current.remove()
      }
    }
  }, [onMapLoad])

  useEffect(() => {
    if (!map.current || !signals.length) return

    markers.current.forEach(marker => marker.remove())
    markers.current = []

    const nigeriaLGACoords = {
      'Maiduguri': [13.1571, 11.8333],
      'Ikeja': [3.3375, 6.5964],
      'Kano': [8.5167, 12.0000],
      'Kaduna': [7.4333, 10.5167],
      'Port Harcourt': [7.0167, 4.7833],
      'Abuja': [7.4951, 9.0579],
      'Lagos': [3.3792, 6.5244],
      'Ibadan': [3.8964, 7.3775],
      'Benin City': [5.6258, 6.3350]
    }

    const features = signals.map(signal => {
      const coords = nigeriaLGACoords[signal.lga] || [8.6753, 9.0820]
      
      if (signal.risk_score >= 80) {
        const el = document.createElement('div')
        el.className = 'pulse-marker'
        el.style.width = '24px'
        el.style.height = '24px'
        el.style.borderRadius = '50%'
        el.style.backgroundColor = signal.risk_score >= 90 ? '#dc2626' : '#ef4444'
        el.style.position = 'relative'
        
        const pulseEl = document.createElement('div')
        pulseEl.className = signal.risk_score >= 90 ? 'pulse-critical' : 'pulse-high'
        pulseEl.style.position = 'absolute'
        pulseEl.style.top = '0'
        pulseEl.style.left = '0'
        pulseEl.style.width = '100%'
        pulseEl.style.height = '100%'
        pulseEl.style.borderRadius = '50%'
        pulseEl.style.backgroundColor = signal.risk_score >= 90 ? '#dc2626' : '#ef4444'
        
        el.appendChild(pulseEl)
        
        const marker = new maplibregl.Marker({ element: el })
          .setLngLat(coords)
          .addTo(map.current)
        
        markers.current.push(marker)
      }

      return {
        type: 'Feature',
        geometry: {
          type: 'Point',
          coordinates: coords
        },
        properties: {
          ...signal,
          risk_score: signal.risk_score || 0
        }
      }
    })

    const source = map.current.getSource('conflict-source')
    if (source) {
      source.setData({
        type: 'FeatureCollection',
        features
      })
    }
  }, [signals])

  const toggleMapStyle = () => {
    if (!map.current) return
    
    const newStyle = mapStyle === 'dark' ? 'bright' : 'dark'
    const styleUrl = newStyle === 'dark' 
      ? 'https://tiles.openfreemap.org/styles/dark'
      : 'https://tiles.openfreemap.org/styles/bright'
    
    map.current.setStyle(styleUrl)
    setMapStyle(newStyle)
    
    // Re-add layers after style change
    map.current.once('styledata', () => {
      if (!map.current.getSource('conflict-source')) {
        map.current.addSource('conflict-source', {
          type: 'geojson',
          data: {
            type: 'FeatureCollection',
            features: signals.map(signal => {
              const nigeriaLGACoords = {
                'Maiduguri': [13.1571, 11.8333],
                'Ikeja': [3.3375, 6.5964],
                'Kano': [8.5167, 12.0000],
                'Kaduna': [7.4333, 10.5167],
                'Port Harcourt': [7.0167, 4.7833],
                'Abuja': [7.4951, 9.0579],
                'Lagos': [3.3792, 6.5244],
                'Ibadan': [3.8964, 7.3775],
                'Benin City': [5.6258, 6.3350]
              }
              const coords = nigeriaLGACoords[signal.lga] || [8.6753, 9.0820]
              
              return {
                type: 'Feature',
                geometry: {
                  type: 'Point',
                  coordinates: coords
                },
                properties: {
                  ...signal,
                  risk_score: signal.risk_score || 0
                }
              }
            })
          }
        })

        // Re-add heatmap layer
        map.current.addLayer({
          id: 'conflict-heatmap',
          type: 'heatmap',
          source: 'conflict-source',
          maxzoom: 15,
          paint: {
            'heatmap-weight': [
              'interpolate',
              ['linear'],
              ['get', 'risk_score'],
              0, 0,
              50, 0.5,
              80, 0.8,
              100, 1
            ],
            'heatmap-intensity': [
              'interpolate',
              ['linear'],
              ['zoom'],
              0, 1,
              15, 3
            ],
            'heatmap-color': [
              'interpolate',
              ['linear'],
              ['heatmap-density'],
              0, 'rgba(0, 0, 255, 0)',
              0.2, 'rgba(0, 255, 255, 0.4)',
              0.4, 'rgba(0, 255, 255, 0.7)',
              0.6, 'rgba(255, 255, 0, 0.8)',
              0.8, 'rgba(255, 165, 0, 0.9)',
              1, 'rgba(220, 20, 60, 1)'
            ],
            'heatmap-radius': [
              'interpolate',
              ['linear'],
              ['zoom'],
              0, 2,
              6, 20,
              10, 40,
              15, 60
            ],
            'heatmap-opacity': [
              'interpolate',
              ['linear'],
              ['zoom'],
              7, 1,
              9, 0.5,
              10, 0.3
            ]
          }
        })

        // Re-add tactical circles
        map.current.addLayer({
          id: 'conflict-circles',
          type: 'circle',
          source: 'conflict-source',
          minzoom: 8,
          paint: {
            'circle-radius': [
              'interpolate',
              ['linear'],
              ['zoom'],
              8, 4,
              12, 8,
              16, 16
            ],
            'circle-color': [
              'interpolate',
              ['linear'],
              ['get', 'risk_score'],
              0, '#22c55e',
              40, '#eab308',
              60, '#f97316',
              80, '#ef4444',
              100, '#dc2626'
            ],
            'circle-opacity': 0.9,
            'circle-stroke-width': 2,
            'circle-stroke-color': '#ffffff',
            'circle-stroke-opacity': 0.8
          }
        })

        // Re-add click handlers
        map.current.on('click', 'conflict-circles', (e) => {
          const coordinates = e.features[0].geometry.coordinates.slice()
          const properties = e.features[0].properties

          new maplibregl.Popup()
            .setLngLat(coordinates)
            .setHTML(`
              <div class="p-4 bg-gray-900 rounded-lg">
                <h3 class="font-bold text-lg mb-2 text-white">${properties.lga}, ${properties.state}</h3>
                <div class="space-y-1 text-sm">
                  <div class="flex justify-between">
                    <span class="text-gray-400">Event Type:</span>
                    <span class="text-white font-semibold">${properties.event_type}</span>
                  </div>
                  <div class="flex justify-between">
                    <span class="text-gray-400">Risk Score:</span>
                    <span class="text-red-400 font-bold">${properties.risk_score}</span>
                  </div>
                  <div class="flex justify-between">
                    <span class="text-gray-400">Risk Level:</span>
                    <span class="text-orange-400">${properties.risk_level}</span>
                  </div>
                  <div class="flex justify-between">
                    <span class="text-gray-400">Severity:</span>
                    <span class="text-yellow-400">${properties.severity}</span>
                  </div>
                </div>
              </div>
            `)
            .addTo(map.current)
        })

        map.current.on('mouseenter', 'conflict-circles', () => {
          map.current.getCanvas().style.cursor = 'pointer'
        })

        map.current.on('mouseleave', 'conflict-circles', () => {
          map.current.getCanvas().style.cursor = ''
        })
      }
    })
  }

  return (
    <div className="relative w-full h-full">
      <div ref={mapContainer} className="w-full h-full" />
      
      {/* Satellite/Bright Toggle Button */}
      <div className="absolute top-4 right-4 z-10">
        <button
          onClick={toggleMapStyle}
          className="bg-gray-900/90 backdrop-blur-md border border-gray-700 rounded-lg p-3 hover:bg-gray-800 transition-all shadow-lg"
          title={mapStyle === 'dark' ? 'Switch to Bright Mode' : 'Switch to Dark Mode'}
        >
          {mapStyle === 'dark' ? (
            <Satellite className="w-5 h-5 text-blue-400" />
          ) : (
            <MapIcon className="w-5 h-5 text-gray-300" />
          )}
        </button>
      </div>

      {/* Quick Intel Panel */}
      <div className="absolute top-4 left-4 bg-gray-900/80 backdrop-blur-md border border-gray-700 rounded-lg p-4 max-w-xs">
        <h4 className="text-sm font-bold text-white mb-3">🔥 CONFLICT HEATMAP</h4>
        <div className="space-y-2 text-xs">
          <div className="flex justify-between">
            <span className="text-gray-400">Total Signals:</span>
            <span className="text-white font-bold">{signals.length}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-400">Hot Zones (≥80):</span>
            <span className="text-red-400 font-bold animate-pulse">
              {signals.filter(s => s.risk_score >= 80).length}
            </span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-400">States Affected:</span>
            <span className="text-white font-bold">
              {new Set(signals.map(s => s.state)).size}
            </span>
          </div>
        </div>
        <div className="mt-3 pt-3 border-t border-gray-700">
          <p className="text-xs text-gray-400 italic">
            {mapLoaded ? '✓ Heatmap Active' : '⏳ Loading...'}
          </p>
          <p className="text-xs text-gray-500 mt-1">
            Zoom in to see tactical markers
          </p>
        </div>
      </div>

      {/* Heatmap Legend */}
      <div className="absolute bottom-4 left-4 right-4 bg-gray-900/80 backdrop-blur-md border border-gray-700 rounded-lg p-3">
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
              Low Density
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
            🇳🇬 774 LGAs | OpenFreeMap
          </div>
        </div>
      </div>
    </div>
  )
}

export default MapView
