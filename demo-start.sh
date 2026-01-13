#!/bin/bash

# ============================================================================
# NEXTIER NIGERIA VIOLENT CONFLICTS DATABASE - DEMO MASTER STARTUP SCRIPT
# ============================================================================
# This script starts ALL services required for the demo with a single command
# Author: Nextier Signal Engine Team
# Last Updated: 2026-01-13
# ============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m' # No Color

# Banner
print_banner() {
    echo -e "${CYAN}"
    echo "╔════════════════════════════════════════════════════════════════╗"
    echo "║                                                                ║"
    echo "║   NEXTIER NIGERIA VIOLENT CONFLICTS DATABASE                  ║"
    echo "║   Demo Environment Startup                                    ║"
    echo "║                                                                ║"
    echo "╚════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

# Print functions
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[⚠]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

print_step() {
    echo -e "${MAGENTA}[STEP]${NC} $1"
}

# Function to check prerequisites
check_prerequisites() {
    print_step "Checking prerequisites..."
    
    local missing_deps=()
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        missing_deps+=("Docker")
    fi
    
    # Check Docker Compose
    if ! docker compose version &> /dev/null; then
        missing_deps+=("Docker Compose")
    fi
    
    # Check Node.js
    if ! command -v node &> /dev/null; then
        missing_deps+=("Node.js")
    fi
    
    # Check npm
    if ! command -v npm &> /dev/null; then
        missing_deps+=("npm")
    fi
    
    if [ ${#missing_deps[@]} -ne 0 ]; then
        print_error "Missing required dependencies:"
        for dep in "${missing_deps[@]}"; do
            echo "  - $dep"
        done
        exit 1
    fi
    
    print_success "All prerequisites installed"
}

# Function to start Docker Desktop
start_docker_desktop() {
    print_status "Starting Docker Desktop..."
    
    if [[ "$OSTYPE" == "darwin"* ]]; then
        if [ -d "/Applications/Docker.app" ]; then
            print_status "Found Docker Desktop, starting..."
            open -a Docker
            
            local max_wait=180
            local wait_time=0
            
            while [ $wait_time -lt $max_wait ]; do
                if docker info >/dev/null 2>&1 && docker version >/dev/null 2>&1; then
                    # Additional check to ensure Docker daemon is fully ready
                    if docker ps >/dev/null 2>&1; then
                        # Extra verification: try to pull a tiny image to ensure daemon is truly ready
                        if docker images >/dev/null 2>&1; then
                            print_success "Docker Desktop started successfully"
                            # Give daemon extra time to stabilize
                            sleep 5
                            return 0
                        fi
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
            return 1
        fi
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        print_status "Attempting to start Docker service on Linux..."
        if command -v systemctl >/dev/null 2>&1; then
            sudo systemctl start docker
            sleep 5
            if docker info >/dev/null 2>&1; then
                print_success "Docker service started successfully"
                return 0
            fi
        fi
        print_error "Failed to start Docker service"
        return 1
    fi
}

# Function to check Docker status
check_docker() {
    print_step "Checking Docker status..."
    
    if ! docker info >/dev/null 2>&1; then
        print_warning "Docker is not running. Attempting to start..."
        
        if start_docker_desktop; then
            print_success "Docker is now running"
        else
            print_error "Failed to start Docker. Please start Docker Desktop manually."
            exit 1
        fi
    else
        print_success "Docker is running"
    fi
    
    # Additional verification that daemon is fully operational
    print_status "Verifying Docker daemon is fully ready..."
    local verify_attempts=0
    while [ $verify_attempts -lt 6 ]; do
        if docker ps >/dev/null 2>&1 && docker images >/dev/null 2>&1; then
            print_success "Docker daemon is fully operational"
            return 0
        fi
        print_status "Waiting for Docker daemon to stabilize... (attempt $((verify_attempts + 1))/6)"
        sleep 5
        ((verify_attempts++))
    done
    
    print_error "Docker daemon not responding properly"
    exit 1
}

# Function to clean up ports
cleanup_ports() {
    print_step "Cleaning up ports..."
    
    local ports=(8000 8001 8002 8080 5173 5174)
    
    for port in "${ports[@]}"; do
        if lsof -ti:$port >/dev/null 2>&1; then
            print_status "Killing process on port $port..."
            lsof -ti:$port | xargs kill -9 2>/dev/null || true
        fi
    done
    
    sleep 2
    print_success "Ports cleaned up"
}

# Function to stop existing containers
stop_existing_containers() {
    print_step "Stopping existing Docker containers..."
    docker compose down --remove-orphans 2>/dev/null || true
    print_success "Existing containers stopped"
}

# Function to build Docker images
build_docker_images() {
    if [ "$SKIP_BUILD" = true ]; then
        print_warning "Skipping Docker image build (--skip-build flag)"
        return 0
    fi
    
    print_step "Building Docker images..."
    print_status "This may take a few minutes on first run..."
    
    if docker compose build --parallel; then
        print_success "Docker images built successfully"
    else
        print_error "Failed to build Docker images"
        exit 1
    fi
}

# Function to start infrastructure services
start_infrastructure() {
    print_step "Starting infrastructure services (MongoDB, RabbitMQ)..."
    
    docker compose up -d mongodb rabbitmq
    
    print_status "Waiting for infrastructure to initialize..."
    sleep 10
    
    # Wait for MongoDB
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if docker exec mongodb mongosh --eval "db.runCommand('ping')" >/dev/null 2>&1; then
            print_success "MongoDB is ready"
            break
        fi
        
        if [ $attempt -eq $max_attempts ]; then
            print_error "MongoDB failed to start"
            exit 1
        fi
        
        sleep 2
        ((attempt++))
    done
    
    # Wait for RabbitMQ
    attempt=1
    while [ $attempt -le $max_attempts ]; do
        if docker exec rabbitmq rabbitmq-diagnostics -q ping >/dev/null 2>&1; then
            print_success "RabbitMQ is ready"
            break
        fi
        
        if [ $attempt -eq $max_attempts ]; then
            print_error "RabbitMQ failed to start"
            exit 1
        fi
        
        sleep 2
        ((attempt++))
    done
}

# Function to start backend services
start_backend_services() {
    print_step "Starting backend services (Scraper, Intelligence API, Predictor)..."
    
    docker compose up -d scraper intelligence-api predictor
    
    print_status "Waiting for backend services to initialize..."
    sleep 15
    
    # Start service processes inside containers
    print_status "Starting Scraper service..."
    docker exec -d scraper-service bash -c "cd /app/scraper && pkill -f uvicorn || true && uvicorn main_fixed:app --host 0.0.0.0 --port 8000 --reload" 2>/dev/null || true
    
    print_status "Starting Intelligence API service..."
    docker exec -d intelligence-api-service bash -c "cd /app/intelligence-api && pkill -f uvicorn || true && uvicorn main_working:app --host 0.0.0.0 --port 8001 --reload" 2>/dev/null || true
    
    print_status "Starting Predictor service..."
    docker exec -d predictor-service bash -c "cd /app/predictor && pkill -f uvicorn || true && uvicorn main_working:app --host 0.0.0.0 --port 8002 --reload" 2>/dev/null || true
    
    sleep 5
    print_success "Backend services started"
}

# Function to start UI service
start_ui_service() {
    print_step "Starting UI Dashboard..."
    
    if [ "$DEV_MODE" = true ]; then
        print_status "Starting UI in development mode with Vite..."
        cd ui
        
        if [ ! -d "node_modules" ]; then
            print_status "Installing UI dependencies..."
            npm install
        fi
        
        print_success "UI will start in development mode on port 5173"
        print_warning "Run 'cd ui && npm run dev' in a separate terminal to start the UI"
    else
        print_status "Starting UI in production mode..."
        docker compose up -d ui
        sleep 5
        print_success "UI Dashboard started on port 8080"
    fi
}

# Function to verify services
verify_services() {
    print_step "Verifying services are responding..."
    
    sleep 10  # Give services time to fully start
    
    local services=(
        "http://localhost:8000/health:Scraper API"
        "http://localhost:8001/health:Intelligence API"
        "http://localhost:8002/health:Predictor API"
    )
    
    if [ "$DEV_MODE" != true ]; then
        services+=("http://localhost:8080/health:UI Dashboard")
    fi
    
    for service in "${services[@]}"; do
        local url=$(echo $service | cut -d: -f1-2)
        local name=$(echo $service | cut -d: -f3)
        
        if curl -s -f "$url" >/dev/null 2>&1; then
            print_success "$name is responding"
        else
            print_warning "$name is not responding yet (may still be initializing)"
        fi
    done
}

# Function to show service status
show_status() {
    echo ""
    echo -e "${CYAN}╔════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║                    DEMO ENVIRONMENT READY                      ║${NC}"
    echo -e "${CYAN}╚════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    
    echo -e "${GREEN}🌐 MAIN DASHBOARD:${NC}"
    if [ "$DEV_MODE" = true ]; then
        echo "   http://localhost:5173/ (Development Mode - Run 'cd ui && npm run dev')"
    else
        echo "   http://localhost:8080/ (Production Mode)"
    fi
    echo ""
    
    echo -e "${GREEN}📡 BACKEND SERVICES:${NC}"
    echo "   • Scraper API:        http://localhost:8000/"
    echo "   • Intelligence API:   http://localhost:8001/"
    echo "   • Predictor API:      http://localhost:8002/"
    echo ""
    
    echo -e "${GREEN}📚 API DOCUMENTATION:${NC}"
    echo "   • Scraper Docs:       http://localhost:8000/docs"
    echo "   • Intelligence Docs:  http://localhost:8001/docs"
    echo "   • Predictor Docs:     http://localhost:8002/docs"
    echo ""
    
    echo -e "${GREEN}🔧 INFRASTRUCTURE:${NC}"
    echo "   • MongoDB:            mongodb://localhost:27017/"
    echo "   • RabbitMQ:           amqp://localhost:5672/"
    echo "   • RabbitMQ UI:        http://localhost:15672/ (admin/password)"
    echo ""
    
    echo -e "${GREEN}🔍 HEALTH CHECKS:${NC}"
    echo "   • Scraper:            http://localhost:8000/health"
    echo "   • Intelligence:       http://localhost:8001/health"
    echo "   • Predictor:          http://localhost:8002/health"
    if [ "$DEV_MODE" != true ]; then
        echo "   • UI:                 http://localhost:8080/health"
    fi
    echo ""
    
    echo -e "${YELLOW}📋 USEFUL COMMANDS:${NC}"
    echo "   • View logs:          docker compose logs -f"
    echo "   • Stop all:           docker compose down"
    echo "   • Restart service:    docker compose restart <service-name>"
    echo "   • Check status:       docker compose ps"
    echo ""
    
    echo -e "${CYAN}✨ Demo environment is ready for presentation!${NC}"
    echo ""
}

# Function to show logs
show_logs() {
    if [ "$SHOW_LOGS" = true ]; then
        print_status "Showing service logs (press Ctrl+C to exit)..."
        docker compose logs -f
    fi
}

# Main execution
main() {
    print_banner
    
    # Parse command line arguments
    SKIP_BUILD=false
    DEV_MODE=false
    SHOW_LOGS=false
    CLEANUP=true
    
    for arg in "$@"; do
        case $arg in
            --skip-build|-s)
                SKIP_BUILD=true
                ;;
            --dev|-d)
                DEV_MODE=true
                ;;
            --logs|-l)
                SHOW_LOGS=true
                ;;
            --no-cleanup)
                CLEANUP=false
                ;;
            --help|-h)
                show_help
                exit 0
                ;;
        esac
    done
    
    # Startup sequence
    check_prerequisites
    check_docker
    
    if [ "$CLEANUP" = true ]; then
        cleanup_ports
        stop_existing_containers
    fi
    
    build_docker_images
    start_infrastructure
    start_backend_services
    start_ui_service
    verify_services
    show_status
    
    # Show logs if requested
    show_logs
}

# Help function
show_help() {
    echo "Nextier Nigeria Violent Conflicts Database - Demo Startup Script"
    echo ""
    echo "Usage: ./demo-start.sh [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --skip-build, -s     Skip Docker image rebuild (faster startup)"
    echo "  --dev, -d            Start UI in development mode (Vite on port 5173)"
    echo "  --logs, -l           Show service logs after startup"
    echo "  --no-cleanup         Skip port cleanup and container stop"
    echo "  --help, -h           Show this help message"
    echo ""
    echo "Examples:"
    echo "  ./demo-start.sh                    # Full production startup"
    echo "  ./demo-start.sh --skip-build       # Quick startup without rebuild"
    echo "  ./demo-start.sh --dev              # Development mode with hot reload"
    echo "  ./demo-start.sh --logs             # Startup and show logs"
    echo "  ./demo-start.sh -s -l              # Quick startup with logs"
    echo ""
    echo "For demo presentations, use:"
    echo "  ./demo-start.sh --skip-build       # Fastest startup for demo"
    echo ""
}

# Run main function
main "$@"
