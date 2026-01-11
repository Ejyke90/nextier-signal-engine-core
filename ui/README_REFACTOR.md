# Nextier Signal Engine - Refactored Dashboard

## 🚀 Modern Stack

This is a complete refactor of the Nigeria Conflict Risk Monitor dashboard using:

- **MapLibre GL JS** - Open-source mapping library (no vendor lock-in)
- **OpenFreeMap** - Privacy-first, free tile service (no tracking, no API keys)
- **React 18** - Modern UI framework
- **Vite** - Lightning-fast build tool
- **Tailwind CSS** - Utility-first CSS framework
- **Recharts** - Composable charting library
- **Lucide React** - Beautiful icon library

## 🎯 Key Features

### 1. **Sovereign Intelligence Architecture**
- ✅ Zero vendor lock-in (no Mapbox, no Google Maps)
- ✅ Privacy-first (OpenFreeMap has no tracking cookies)
- ✅ 100% offline capable (can pre-download tiles)
- ✅ Low operational overhead (no per-map-view pricing)

### 2. **MapLibre GL JS Integration**
- Circle layer visualization with risk-based coloring
- Pulse animations for high-risk markers (Risk_Score > 80)
- Interactive popups with detailed event information
- Smooth flyTo animations when clicking signal cards
- Nigeria-centered view [9.0820, 8.6753] at zoom level 6

### 3. **Bento Grid Dark Mode UI**
- Responsive 3-column layout (2-7-3 grid)
- Live Signal Ticker (left sidebar)
- Interactive Map (center)
- National Risk Overview (right sidebar)

### 4. **Live Signal Ticker**
- Real-time streaming of risk signals
- Color-coded risk levels (Critical/High/Medium/Low)
- Click location icon to flyTo on map
- Displays fuel price and inflation data

### 5. **National Risk Overview**
- 7-day trend line chart (Recharts)
- Risk distribution pie chart
- Top affected states bar chart
- Quick action buttons
- Critical/High risk counters

## 🛠️ Development

### Install Dependencies
```bash
npm install
```

### Run Development Server
```bash
npm run dev
```

The app will be available at `http://localhost:5000`

### Build for Production
```bash
npm run build
```

### Preview Production Build
```bash
npm run preview
```

## 🐳 Docker Deployment

### Build Docker Image
```bash
docker build -f Dockerfile.new -t nextier-ui:latest .
```

### Run Container
```bash
docker run -p 80:80 nextier-ui:latest
```

## 📁 Project Structure

```
ui/
├── src/
│   ├── components/
│   │   ├── MapView.jsx           # MapLibre GL JS integration
│   │   ├── LiveSignalTicker.jsx  # Left sidebar with signals
│   │   ├── NationalRiskOverview.jsx  # Right sidebar with charts
│   │   └── ThreatStatusBar.jsx   # Top status bar
│   ├── App.jsx                   # Main application component
│   ├── App.css                   # Custom styles & animations
│   ├── main.jsx                  # React entry point
│   └── index.css                 # Tailwind imports
├── index_new.html                # HTML entry point
├── package.json                  # Dependencies
├── vite.config.js                # Vite configuration
├── tailwind.config.js            # Tailwind configuration
├── postcss.config.js             # PostCSS configuration
├── Dockerfile.new                # Multi-stage Docker build
└── nginx.conf                    # Nginx configuration
```

## 🎨 Color Scheme

- **Critical (≥80)**: Red (#ef4444)
- **High (60-79)**: Orange (#f97316)
- **Medium (40-59)**: Yellow (#eab308)
- **Low (<40)**: Green (#22c55e)

## 🗺️ Map Features

### Circle Layer
- Dynamic sizing based on risk score
- Color interpolation from green to red
- Stroke outline for visibility
- Click to show popup with details

### Pulse Markers
- Animated pulse effect for Risk_Score > 80
- Critical pulse (≥90): Faster, more intense
- High pulse (80-89): Moderate animation

### Interactive Elements
- Hover cursor changes
- Click for detailed popup
- FlyTo animation from sidebar clicks
- Quick intel overlay (top-left)
- Legend overlay (bottom)

## 🔒 Security & Privacy

### Why OpenFreeMap?
1. **No Tracking**: Unlike Google Maps or Mapbox, OpenFreeMap doesn't track users
2. **No API Keys**: No authentication required, reducing attack surface
3. **Sovereign Data**: Can host tiles locally for complete data sovereignty
4. **Open Source**: Transparent, auditable codebase

### Offline Mode
You can pre-download Nigeria tiles and serve them locally:
```bash
# Download tiles for Nigeria (zoom levels 0-12)
# Store in local tile server
# Update MapLibre style URL to point to local server
```

## 📊 Data Flow

1. **Fetch**: App fetches `/data/risk_signals.json` every 5 seconds
2. **Process**: Signals are mapped to LGA coordinates
3. **Render**: MapLibre displays circles and pulse markers
4. **Interact**: Users can click signals or map markers
5. **Visualize**: Charts update in real-time

## 🚀 Performance

- **Vite HMR**: Instant hot module replacement during development
- **Code Splitting**: Automatic chunking for optimal loading
- **Tree Shaking**: Removes unused code
- **Gzip Compression**: Nginx serves compressed assets
- **Asset Caching**: 1-year cache for static files

## 🎯 Client Presentation Points

When presenting to the client, emphasize:

1. **Zero Vendor Lock-in**: "We're not tied to American companies that can raise prices or cut off access"
2. **Privacy-First**: "No tracking cookies or external databases monitoring our patterns—essential for national security"
3. **Low Operational Overhead**: "Entire platform runs for the price of a small server; no per-map-view charges"
4. **Offline Capable**: "Can work 100% offline in areas with poor internet by pre-downloading tiles"
5. **Sovereign Intelligence**: "Complete control over our geospatial intelligence infrastructure"

## 🔧 Troubleshooting

### Map not loading?
- Check OpenFreeMap is accessible: `https://tiles.openfreemap.org/styles/dark`
- Verify CORS is enabled
- Check browser console for errors

### Signals not appearing?
- Verify `/data/risk_signals.json` is accessible
- Check API endpoint in `App.jsx`
- Ensure LGA coordinates are mapped correctly

### Build errors?
- Clear node_modules: `rm -rf node_modules && npm install`
- Clear Vite cache: `rm -rf node_modules/.vite`
- Check Node version: `node -v` (should be 18+)

## 📝 Migration Notes

The old `index.html` has been preserved as `index_backup.html`. To switch to the new React version:

1. Rename `index.html` to `index_old.html`
2. Rename `index_new.html` to `index.html`
3. Update docker-compose.yml to use `Dockerfile.new`
4. Rebuild containers

## 🎉 What's Next?

- [ ] Add real-time WebSocket updates
- [ ] Implement advanced filtering
- [ ] Add export to PDF/CSV
- [ ] Create mobile-responsive views
- [ ] Add user authentication
- [ ] Implement role-based access control
