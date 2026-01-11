# Deployment Guide - Nextier Signal Engine Dashboard

## 🚀 Quick Start

### Option 1: Development Mode (Recommended for Testing)

```bash
cd ui
npm install
npm run dev
```

Access at: `http://localhost:5173`

### Option 2: Production Build (Local)

```bash
cd ui
npm install
npm run build
npm run preview
```

Access at: `http://localhost:4173`

### Option 3: Docker Deployment (Production)

```bash
cd ui
docker build -f Dockerfile.new -t nextier-ui:latest .
docker run -d -p 80:80 --name nextier-dashboard nextier-ui:latest
```

Access at: `http://localhost`

## 🐳 Docker Compose Integration

### Update docker-compose.yml

Replace the existing `ui` service with:

```yaml
services:
  ui:
    build:
      context: ./ui
      dockerfile: Dockerfile.new
    container_name: nextier-ui
    ports:
      - "80:80"
    networks:
      - nextier-network
    depends_on:
      - predictor
      - scraper
      - intelligence-api
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "wget", "--quiet", "--tries=1", "--spider", "http://localhost/"]
      interval: 30s
      timeout: 10s
      retries: 3
```

### Full Stack Deployment

```bash
# From project root
docker-compose down
docker-compose up --build -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f ui
```

## 🔧 Configuration

### Environment Variables

Create `.env` file in `ui/` directory:

```bash
# API Endpoints
VITE_PREDICTOR_API=http://localhost:8003
VITE_SCRAPER_API=http://localhost:8001
VITE_INTELLIGENCE_API=http://localhost:8002

# Map Configuration
VITE_MAP_STYLE=https://tiles.openfreemap.org/styles/dark
VITE_MAP_CENTER_LNG=8.6753
VITE_MAP_CENTER_LAT=9.0820
VITE_MAP_ZOOM=6

# Polling Interval (milliseconds)
VITE_POLL_INTERVAL=5000
```

### Update App.jsx to use environment variables

```javascript
const API_BASE = import.meta.env.VITE_PREDICTOR_API || 'http://localhost:8003'
const POLL_INTERVAL = import.meta.env.VITE_POLL_INTERVAL || 5000

const fetchRiskSignals = async () => {
  const response = await fetch(`${API_BASE}/data/risk_signals.json`)
  // ...
}
```

## 🌐 Production Deployment

### AWS EC2 / Azure VM

1. **Install Docker**
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
```

2. **Clone Repository**
```bash
git clone https://github.com/your-org/nextier-signal-engine-core.git
cd nextier-signal-engine-core
```

3. **Deploy**
```bash
docker-compose up -d
```

4. **Configure Firewall**
```bash
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### Nginx Reverse Proxy (Optional)

If running behind another Nginx:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:80;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

### SSL/TLS with Let's Encrypt

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

## 📊 Monitoring

### Health Checks

```bash
# Check UI health
curl http://localhost/

# Check all services
docker-compose ps
```

### Logs

```bash
# UI logs
docker-compose logs -f ui

# All services
docker-compose logs -f

# Last 100 lines
docker-compose logs --tail=100 ui
```

### Resource Usage

```bash
# Container stats
docker stats nextier-ui

# Disk usage
docker system df
```

## 🔄 Updates & Maintenance

### Update Application

```bash
# Pull latest code
git pull origin main

# Rebuild and restart
docker-compose down
docker-compose up --build -d
```

### Clear Cache

```bash
# Clear Docker build cache
docker builder prune -a

# Clear npm cache
cd ui && npm cache clean --force
```

### Backup

```bash
# Backup configuration
tar -czf nextier-backup-$(date +%Y%m%d).tar.gz \
  docker-compose.yml \
  ui/src \
  ui/package.json \
  ui/vite.config.js

# Backup data
docker exec mongodb mongodump --out /backup
```

## 🐛 Troubleshooting

### Issue: Map not loading

**Symptoms**: Blank map area, console errors about tiles

**Solutions**:
1. Check internet connectivity to OpenFreeMap
2. Verify CORS is enabled
3. Try alternative style: `https://tiles.openfreemap.org/styles/bright`
4. Check browser console for specific errors

### Issue: API data not loading

**Symptoms**: No signals appearing, empty sidebar

**Solutions**:
1. Verify backend services are running: `docker-compose ps`
2. Check API endpoint in browser: `http://localhost:8003/data/risk_signals.json`
3. Review CORS configuration in backend
4. Check network tab in browser DevTools

### Issue: Build fails

**Symptoms**: Docker build errors, npm errors

**Solutions**:
```bash
# Clear node_modules
rm -rf ui/node_modules ui/package-lock.json

# Rebuild
cd ui
npm install
npm run build

# If Docker build fails
docker system prune -a
docker-compose build --no-cache ui
```

### Issue: Port conflicts

**Symptoms**: "Port already in use" errors

**Solutions**:
```bash
# Find process using port 80
sudo lsof -i :80

# Kill process
sudo kill -9 <PID>

# Or use different port in docker-compose.yml
ports:
  - "8080:80"
```

## 📈 Performance Tuning

### Nginx Optimization

Update `ui/nginx.conf`:

```nginx
# Increase worker connections
events {
    worker_connections 2048;
}

# Enable HTTP/2
listen 443 ssl http2;

# Optimize buffer sizes
client_body_buffer_size 10K;
client_header_buffer_size 1k;
client_max_body_size 8m;
large_client_header_buffers 2 1k;
```

### Vite Build Optimization

Update `vite.config.js`:

```javascript
export default defineConfig({
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          'maplibre': ['maplibre-gl'],
          'charts': ['recharts'],
          'icons': ['lucide-react']
        }
      }
    },
    chunkSizeWarningLimit: 1000
  }
})
```

## 🔐 Security Hardening

### 1. Update Nginx Headers

```nginx
add_header X-Frame-Options "DENY" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Referrer-Policy "no-referrer-when-downgrade" always;
add_header Content-Security-Policy "default-src 'self' https://tiles.openfreemap.org; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com;" always;
```

### 2. Disable Directory Listing

```nginx
autoindex off;
```

### 3. Rate Limiting

```nginx
limit_req_zone $binary_remote_addr zone=one:10m rate=10r/s;

location / {
    limit_req zone=one burst=20;
}
```

## 📱 Mobile Optimization

### Responsive Breakpoints

Update `tailwind.config.js`:

```javascript
theme: {
  extend: {
    screens: {
      'xs': '475px',
      '3xl': '1920px',
    }
  }
}
```

### Touch Optimization

Add to `App.css`:

```css
@media (hover: none) and (pointer: coarse) {
  .maplibregl-canvas {
    touch-action: pan-x pan-y;
  }
}
```

## 🌍 Offline Deployment

### Pre-download Tiles

```bash
# Install tile downloader
npm install -g mbutil

# Download Nigeria tiles (zoom 0-12)
# This requires a tile server setup
# Contact OpenFreeMap for bulk download options
```

### Update Map Style

```javascript
// In MapView.jsx
style: {
  version: 8,
  sources: {
    'local-tiles': {
      type: 'raster',
      tiles: ['http://localhost:8080/tiles/{z}/{x}/{y}.png'],
      tileSize: 256
    }
  },
  layers: [{
    id: 'local-tiles',
    type: 'raster',
    source: 'local-tiles'
  }]
}
```

## ✅ Pre-Deployment Checklist

- [ ] All dependencies installed (`npm install`)
- [ ] Environment variables configured
- [ ] Backend services running and accessible
- [ ] Build completes successfully (`npm run build`)
- [ ] Docker image builds without errors
- [ ] Health checks passing
- [ ] SSL/TLS configured (production)
- [ ] Firewall rules configured
- [ ] Monitoring and logging set up
- [ ] Backup strategy in place
- [ ] Documentation updated
- [ ] Team trained on deployment process

## 📞 Support

For deployment issues:
1. Check logs: `docker-compose logs -f ui`
2. Review this guide
3. Check GitHub issues
4. Contact DevOps team

---

**Last Updated**: January 10, 2026  
**Maintained By**: Nextier DevOps Team
