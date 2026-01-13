#!/bin/bash

# ============================================================================
# DEMO PREPARATION SCRIPT - Run this BEFORE your demo
# ============================================================================
# This script ensures Docker is running and images are built
# Run this 10-15 minutes before your demo, then use demo-run.sh to start
# ============================================================================

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

print_banner() {
    echo -e "${CYAN}"
    echo "╔════════════════════════════════════════════════════════════════╗"
    echo "║                                                                ║"
    echo "║   DEMO PREPARATION - Step 1 of 2                              ║"
    echo "║   Preparing Docker and Images                                 ║"
    echo "║                                                                ║"
    echo "╚════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

print_step() {
    echo -e "${CYAN}[STEP]${NC} $1"
}

# Check if Docker Desktop is installed
check_docker_installed() {
    print_step "Checking Docker Desktop installation..."
    
    if [[ "$OSTYPE" == "darwin"* ]]; then
        if [ ! -d "/Applications/Docker.app" ]; then
            print_error "Docker Desktop not found!"
            echo "Please install Docker Desktop from: https://www.docker.com/products/docker-desktop"
            exit 1
        fi
    fi
    
    print_success "Docker Desktop is installed"
}

# Start Docker Desktop
start_docker() {
    print_step "Starting Docker Desktop..."
    
    if docker info >/dev/null 2>&1; then
        print_success "Docker Desktop is already running"
        return 0
    fi
    
    print_status "Opening Docker Desktop application..."
    open -a Docker
    
    echo ""
    echo -e "${YELLOW}⏳ Waiting for Docker Desktop to fully start...${NC}"
    echo -e "${YELLOW}   This may take 30-60 seconds${NC}"
    echo ""
    
    local max_wait=120
    local wait_time=0
    
    while [ $wait_time -lt $max_wait ]; do
        if docker info >/dev/null 2>&1; then
            if docker ps >/dev/null 2>&1; then
                print_success "Docker Desktop is running"
                # Extra wait to ensure stability
                print_status "Waiting for Docker to stabilize..."
                sleep 10
                return 0
            fi
        fi
        
        echo -ne "\r${BLUE}[INFO]${NC} Waiting... ($wait_time/$max_wait seconds)"
        sleep 5
        wait_time=$((wait_time + 5))
    done
    
    echo ""
    print_error "Docker Desktop did not start in time"
    exit 1
}

# Verify Docker is working
verify_docker() {
    print_step "Verifying Docker is operational..."
    
    if ! docker info >/dev/null 2>&1; then
        print_error "Docker daemon is not responding"
        exit 1
    fi
    
    if ! docker ps >/dev/null 2>&1; then
        print_error "Cannot list containers"
        exit 1
    fi
    
    if ! docker images >/dev/null 2>&1; then
        print_error "Cannot list images"
        exit 1
    fi
    
    print_success "Docker is fully operational"
}

# Build UI locally
build_ui() {
    print_step "Building React UI locally..."
    
    if [ ! -d "ui" ]; then
        print_error "UI directory not found"
        exit 1
    fi
    
    cd ui
    
    # Check if node_modules exists
    if [ ! -d "node_modules" ]; then
        print_status "Installing UI dependencies..."
        npm install
    fi
    
    # Build the React app
    print_status "Building React app with Vite..."
    npm run build
    
    cd ..
    
    print_success "React UI built successfully"
}

# Build or pull images
prepare_images() {
    print_step "Preparing Docker images..."
    
    if [ "$SKIP_BUILD" = true ]; then
        print_status "Checking if images exist..."
        
        local missing_images=false
        local images=("scraper" "intelligence-api" "predictor" "ui")
        
        for img in "${images[@]}"; do
            if ! docker images | grep -q "nextier-nigeria-violent-conflicts-database-${img}"; then
                print_error "Image for ${img} not found"
                missing_images=true
            fi
        done
        
        if [ "$missing_images" = true ]; then
            print_status "Some images missing, building..."
            docker compose build --parallel
        else
            print_success "All application images exist"
        fi
    else
        print_status "Building Docker images (this takes 5-10 minutes)..."
        docker compose build --parallel
        print_success "Images built successfully"
    fi
    
    # Pull base images
    print_status "Ensuring base images are available..."
    docker pull mongo:6.0 2>/dev/null || true
    docker pull rabbitmq:3-management 2>/dev/null || true
    print_success "Base images ready"
}

# Clean up old containers
cleanup() {
    print_step "Cleaning up old containers..."
    docker compose down --remove-orphans 2>/dev/null || true
    print_success "Cleanup complete"
}

# Main
main() {
    print_banner
    
    SKIP_BUILD=false
    
    for arg in "$@"; do
        case $arg in
            --skip-build|-s)
                SKIP_BUILD=true
                ;;
            --help|-h)
                echo "Demo Preparation Script"
                echo ""
                echo "Usage: ./demo-prep.sh [OPTIONS]"
                echo ""
                echo "Options:"
                echo "  --skip-build, -s    Skip building images (use existing)"
                echo "  --help, -h          Show this help"
                echo ""
                exit 0
                ;;
        esac
    done
    
    check_docker_installed
    start_docker
    verify_docker
    cleanup
    build_ui
    prepare_images
    
    echo ""
    echo -e "${GREEN}╔════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║                    PREPARATION COMPLETE                        ║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${CYAN}✅ Docker Desktop is running and ready${NC}"
    echo -e "${CYAN}✅ React UI built with latest changes${NC}"
    echo -e "${CYAN}✅ All Docker images are prepared${NC}"
    echo ""
    echo -e "${YELLOW}Next step:${NC}"
    echo -e "  Run: ${GREEN}./demo-run.sh${NC} to start all services"
    echo ""
    echo -e "${BLUE}💡 Tip: Keep Docker Desktop running until after your demo${NC}"
    echo ""
}

main "$@"
