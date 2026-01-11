// Risk Thresholds
export const RISK_THRESHOLDS = {
  CRITICAL: 80,
  HIGH: 60,
  MEDIUM: 40,
  LOW: 20
}

// Indicator Thresholds
export const INDICATOR_THRESHOLDS = {
  FLOOD_INUNDATION: 20,
  MINING_PROXIMITY_KM: 10
}

// Nigeria LGA Coordinates
export const NIGERIA_LGA_COORDS = {
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

// Nigeria Center Coordinates
export const NIGERIA_CENTER = { lat: 9.0820, lng: 8.6753 }

// API Configuration
export const API_CONFIG = {
  BASE_URL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8002',
  ENDPOINTS: {
    RISK_OVERVIEW: '/api/v1/risk-overview',
    SIMULATE: '/api/v1/simulate',
    RISK_SIGNALS: '/api/v1/signals',
    CATEGORIZATION_STATS: '/api/v1/categorization-stats',
    TRIGGER_CATEGORIZATION: '/api/v1/categorize'
  }
}

// Polling Interval (milliseconds)
export const POLLING_INTERVAL = 5000

// Map Configuration
export const MAP_CONFIG = {
  DEFAULT_ZOOM: 6,
  DETAIL_ZOOM: 12,
  FLY_DURATION: 2
}

// Color Scheme
export const RISK_COLORS = {
  CRITICAL: '#dc143c',
  HIGH: '#ff8c00',
  MEDIUM: '#ffd700',
  LOW: '#00ffff'
}

// Circle Radius by Risk Level
export const CIRCLE_RADIUS = {
  CRITICAL: 15,
  HIGH: 12,
  MEDIUM: 10,
  LOW: 8
}
