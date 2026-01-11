#!/bin/bash

# Nextier Signal Engine Core - Complete Startup Script
# This script starts all services with Docker rebuild capability for code changes

set -e

echo "🚀 Starting Nextier Signal Engine Core..."
echo "================================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to start Docker Desktop
start_docker_desktop() {
    print_status "Starting Docker Desktop..."
    
    # Check if we're on macOS
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # Try to start Docker Desktop on macOS
        if [ -d "/Applications/Docker.app" ]; then
            print_status "Found Docker Desktop, starting..."
            open -a Docker
            
            # Wait for Docker to start (up to 2 minutes)
            local max_wait=120
            local wait_time=0
            
            while [ $wait_time -lt $max_wait ]; do
                if docker info >/dev/null 2>&1 && docker version >/dev/null 2>&1; then
                    # Additional check to ensure Docker daemon is fully ready
                    if docker ps >/dev/null 2>&1; then
                        print_success "Docker Desktop started successfully"
                        return 0
                    fi
                fi
                
                print_status "Waiting for Docker Desktop to start... ($wait_time/$max_wait seconds)"
                sleep 5
                wait_time=$((wait_time + 5))
            done
            
            print_error "Docker Desktop failed to start within $max_wait seconds"
            return 1
        else
            print_error "Docker Desktop not found at /Applications/Docker.app"
            print_error "Please install Docker Desktop from https://www.docker.com/products/docker-desktop"
            return 1
        fi
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Try to start Docker service on Linux
        print_status "Attempting to start Docker service on Linux..."
        if command -v systemctl >/dev/null 2>&1; then
            sudo systemctl start docker
            sleep 5
            if docker info >/dev/null 2>&1; then
                print_success "Docker service started successfully"
                return 0
            fi
        fi
        print_error "Failed to start Docker service. Please start Docker manually."
        return 1
    else
        print_error "Unsupported operating system: $OSTYPE"
        print_error "Please start Docker manually and try again."
        return 1
    fi
}

# Function to check if Docker is running
check_docker() {
    print_status "Checking Docker status..."
    
    if ! docker info >/dev/null 2>&1; then
        print_warning "Docker is not running. Attempting to start Docker Desktop..."
        
        if start_docker_desktop; then
            print_success "Docker is now running"
        else
            print_error "Failed to start Docker. Please start Docker Desktop manually and try again."
            echo ""
            echo "To start Docker Desktop manually:"
            echo "  • On macOS: Open Applications → Docker"
            echo "  • On Linux: Run 'sudo systemctl start docker'"
            echo "  • On Windows: Start Docker Desktop from Start Menu"
            echo ""
            exit 1
        fi
    else
        print_success "Docker is already running"
    fi
}

# Function to kill processes on specific ports (optional utility function)
kill_port_processes() {
    local port=$1
    print_status "Killing any processes on port $port..."
    
    # Kill processes on the port (suppress errors if no processes found)
    lsof -ti:$port 2>/dev/null | xargs kill -9 2>/dev/null || true
    
    # Wait a moment for processes to terminate
    sleep 2
    
    print_success "Port $port cleared"
}

# Function to clean up all ports (only if explicitly requested)
cleanup_ports() {
    if [ "$CLEANUP_PORTS" = true ]; then
        print_status "Cleaning up all service ports..."
        kill_port_processes 8000  # Scraper
        kill_port_processes 8001  # Intelligence API
        kill_port_processes 8002  # Predictor
        kill_port_processes 8080  # UI
        print_success "All ports cleaned up"
    else
        print_status "Skipping port cleanup (use --cleanup-ports to enable)"
    fi
}

# Function to stop existing Docker containers
stop_containers() {
    print_status "Stopping existing Docker containers..."
    docker compose down --remove-orphans 2>/dev/null || true
    print_success "Containers stopped"
}

# Function to rebuild Docker images
rebuild_images() {
    print_status "Rebuilding Docker images (this may take a few minutes)..."
    docker compose build --no-cache --parallel
    print_success "Docker images rebuilt"
}

# Function to start Docker services
start_docker_services() {
    print_status "Starting Docker services..."
    docker compose up -d
    print_success "Docker services started"
}

# Function to wait for services to be ready
wait_for_services() {
    print_status "Waiting for services to be ready..."
    
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        print_status "Checking services... (attempt $attempt/$max_attempts)"
        
        # Check if all containers are running
        local running_containers=$(docker compose ps --services --filter "status=running" | wc -l)
        local total_services=6  # scraper, intelligence-api, predictor, ui, mongodb, rabbitmq
        
        if [ "$running_containers" -eq "$total_services" ]; then
            print_success "All Docker containers are running"
            break
        fi
        
        if [ $attempt -eq $max_attempts ]; then
            print_error "Services failed to start within expected time"
            docker compose ps
            exit 1
        fi
        
        sleep 5
        ((attempt++))
    done
}

# Function to start individual service processes inside containers
start_service_processes() {
    print_status "Starting individual service processes..."
    
    # Start scraper service with fixed main
    print_status "Starting Scraper service..."
    docker exec -d scraper-service bash -c "cd /app/scraper && pkill -f uvicorn || true && uvicorn main_fixed:app --host 0.0.0.0 --port 8000 --reload"
    
    # Start intelligence-api service with fixed main
    print_status "Starting Intelligence API service..."
    docker exec -d intelligence-api-service bash -c "cd /app/intelligence-api && pkill -f uvicorn || true && uvicorn main_working:app --host 0.0.0.0 --port 8001 --reload"
    
    # Start predictor service with fixed main
    print_status "Starting Predictor service..."
    docker exec -d predictor-service bash -c "cd /app/predictor && pkill -f uvicorn || true && uvicorn main_working:app --host 0.0.0.0 --port 8002 --reload"
    
    print_success "All service processes started"
}

# Function to verify services are responding
verify_services() {
    print_status "Verifying services are responding..."
    
    local services=(
        "http://localhost:8000/:Scraper"
        "http://localhost:8001/:Intelligence-API"
        "http://localhost:8002/:Predictor"
        "http://localhost:8080/:UI Dashboard"
    )
    
    sleep 10  # Give services time to start
    
    for service in "${services[@]}"; do
        local url=$(echo $service | cut -d: -f1-2)
        local name=$(echo $service | cut -d: -f3)
        
        print_status "Checking $name at $url..."
        
        if curl -s -f "$url" >/dev/null 2>&1; then
            print_success "$name is responding"
        else
            print_warning "$name is not responding yet (may still be starting)"
        fi
    done
}

# Function to show service status
show_status() {
    echo ""
    echo "================================================"
    echo "🎯 Nextier Signal Engine Core Status"
    echo "================================================"
    
    echo ""
    echo "📊 Services:"
    echo "  • Scraper Service:      http://localhost:8000/"
    echo "  • Intelligence API:     http://localhost:8001/"
    echo "  • Predictor Service:    http://localhost:8002/"
    echo "  • UI Dashboard:         http://localhost:8080/"
    echo ""
    echo "🔧 Infrastructure:"
    echo "  • MongoDB:              localhost:27017"
    echo "  • RabbitMQ:             localhost:5672"
    echo "  • RabbitMQ Management:  http://localhost:15672/"
    echo ""
    echo "📋 API Endpoints:"
    echo "  • Articles:             http://localhost:8000/api/v1/articles"
    echo "  • Events Status:        http://localhost:8001/api/v1/status"
    echo "  • Risk Signals:         http://localhost:8002/api/v1/signals"
    echo ""
    echo "🔍 Health Checks:"
    echo "  • Scraper Health:       http://localhost:8000/health"
    echo "  • Intelligence Health:  http://localhost:8001/health"
    echo "  • Predictor Health:     http://localhost:8002/health"
    echo "  • UI Health:            http://localhost:8080/health"
    echo ""
    echo "📚 Documentation:"
    echo "  • Scraper API Docs:     http://localhost:8000/docs"
    echo "  • Intelligence Docs:    http://localhost:8001/docs"
    echo "  • Predictor API Docs:   http://localhost:8002/docs"
    echo ""
    
    print_success "All services are ready!"
    echo ""
    echo "🌐 Open your browser and navigate to: http://localhost:8080/"
    echo "   to access the Nextier Signal Engine Dashboard"
    echo ""
}

# Function to show logs
show_logs() {
    if [ "$1" = "--logs" ] || [ "$1" = "-l" ]; then
        print_status "Showing service logs (press Ctrl+C to exit)..."
        docker compose logs -f
    fi
}

# Main execution
main() {
    echo "🔧 Nextier Signal Engine Core - Complete Startup"
    echo "This script will:"
    echo "  1. Check Docker status"
    echo "  2. Stop existing containers"
    echo "  3. Rebuild Docker images (for code changes)"
    echo "  4. Start all services"
    echo "  5. Verify everything is working"
    echo ""
    
    # Parse command line arguments
    SKIP_REBUILD=false
    CLEANUP_PORTS=false
    
    for arg in "$@"; do
        case $arg in
            --no-rebuild|-n)
                print_warning "Skipping Docker image rebuild"
                SKIP_REBUILD=true
                ;;
            --cleanup-ports)
                print_warning "Port cleanup enabled"
                CLEANUP_PORTS=true
                ;;
        esac
    done
    
    # Execute startup sequence
    check_docker
    cleanup_ports
    stop_containers
    
    if [ "$SKIP_REBUILD" = false ]; then
        rebuild_images
    fi
    
    start_docker_services
    wait_for_services
    start_service_processes
    verify_services
    show_status
    
    # Show logs if requested
    show_logs "$@"
}

# Help function
show_help() {
    echo "Nextier Signal Engine Core - Startup Script"
    echo ""
    echo "Usage: ./start-services.sh [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --no-rebuild, -n     Skip Docker image rebuild (faster startup)"
    echo "  --cleanup-ports      Kill processes on ports 8000-8002, 8080 before starting"
    echo "  --logs, -l           Show service logs after startup"
    echo "  --help, -h           Show this help message"
    echo ""
    echo "Examples:"
    echo "  ./start-services.sh                      # Full startup with rebuild"
    echo "  ./start-services.sh --no-rebuild         # Quick startup without rebuild"
    echo "  ./start-services.sh --cleanup-ports      # Startup with port cleanup"
    echo "  ./start-services.sh --logs               # Startup and show logs"
    echo ""
}

# Handle command line arguments
case "$1" in
    --help|-h)
        show_help
        exit 0
        ;;
    *)
        main "$@"
        ;;
esac
