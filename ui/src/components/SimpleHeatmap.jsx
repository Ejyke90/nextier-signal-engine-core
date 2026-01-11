import { useEffect } from 'react'
import { MapContainer, TileLayer, useMap } from 'react-leaflet'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import 'leaflet.heat'

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
      gradient: {
        0.0: 'rgba(0, 255, 255, 0)',
        0.2: 'rgba(0, 255, 255, 0.4)',
        0.4: 'rgba(0, 255, 255, 0.7)',
        0.6: 'rgba(255, 255, 0, 0.8)',
        0.8: 'rgba(255, 165, 0, 0.9)',
        1.0: 'rgba(220, 20, 60, 1)'
      }
    }).addTo(map)

    return () => {
      map.removeLayer(heat)
    }
  }, [map, points])

  return null
}

const SimpleHeatmap = ({ signals }) => {
  const nigeriaLGACoords = {
    'Maiduguri': { lat: 11.8333, lng: 13.1571 },
    'Ikeja': { lat: 6.5964, lng: 3.3375 },
    'Kano': { lat: 12.0000, lng: 8.5167 },
    'Kaduna': { lat: 10.5167, lng: 7.4333 },
    'Port Harcourt': { lat: 4.7833, lng: 7.0167 },
    'Abuja': { lat: 9.0579, lng: 7.4951 },
    'Lagos': { lat: 6.5244, lng: 3.3792 },
    'Ibadan': { lat: 7.3775, lng: 3.8964 },
    'Benin City': { lat: 6.3350, lng: 5.6258 }
  }

  const heatmapPoints = signals.map(signal => {
    const coords = nigeriaLGACoords[signal.lga] || { lat: 9.0820, lng: 8.6753 }
    return {
      lat: coords.lat,
      lng: coords.lng,
      intensity: signal.risk_score / 100
    }
  })

  return (
    <div className="relative w-full h-full">
      <MapContainer
        center={[9.0820, 8.6753]}
        zoom={6}
        style={{ height: '100%', width: '100%' }}
        zoomControl={true}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        <HeatmapLayer points={heatmapPoints} />
      </MapContainer>

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

export default SimpleHeatmap
