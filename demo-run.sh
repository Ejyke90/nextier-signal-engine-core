#!/bin/bash

# ============================================================================
# DEMO RUN SCRIPT - Run this to START your demo
# ============================================================================
# Prerequisites: Docker Desktop must be running (use demo-prep.sh first)
# This script quickly starts all services for your demo
# ============================================================================

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m'

print_banner() {
    echo -e "${CYAN}"
    echo "╔════════════════════════════════════════════════════════════════╗"
    echo "║                                                                ║"
    echo "║   DEMO START - Step 2 of 2                                    ║"
    echo "║   Starting All Services                                       ║"
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
    echo -e "${MAGENTA}[STEP]${NC} $1"
}

# Quick Docker check
check_docker() {
    print_step "Checking Docker status..."
    
    if ! docker info >/dev/null 2>&1; then
        print_error "Docker is not running!"
        echo ""
        echo "Please run: ${GREEN}./demo-prep.sh${NC} first"
        echo "Or manually start Docker Desktop and wait 30 seconds"
        exit 1
    fi
    
    print_success "Docker is running"
}

# Clean up ports
cleanup_ports() {
    print_step "Cleaning up ports..."
    
    local ports=(8000 8001 8002 8080 5173)
    
    for port in "${ports[@]}"; do
        lsof -ti:$port 2>/dev/null | xargs kill -9 2>/dev/null || true
    done
    
    print_success "Ports cleaned"
}

# Stop old containers
stop_old() {
    print_step "Stopping old containers..."
    docker compose down 2>/dev/null || true
    print_success "Old containers stopped"
}

# Start infrastructure
start_infrastructure() {
    print_step "Starting MongoDB and RabbitMQ..."
    
    docker compose up -d mongodb rabbitmq
    
    print_status "Waiting for infrastructure (15 seconds)..."
    sleep 15
    
    print_success "Infrastructure ready"
}

# Start backend services
start_backends() {
    print_step "Starting backend services..."
    
    docker compose up -d scraper intelligence-api predictor
    
    print_status "Waiting for backends to initialize (20 seconds)..."
    sleep 20
    
    # Start service processes
    print_status "Starting Scraper API..."
    docker exec -d scraper-service bash -c "cd /app/scraper && pkill -f uvicorn || true && uvicorn main_fixed:app --host 0.0.0.0 --port 8000 --reload" 2>/dev/null || true
    
    print_status "Starting Intelligence API..."
    docker exec -d intelligence-api-service bash -c "cd /app/intelligence-api && pkill -f uvicorn || true && uvicorn main_working:app --host 0.0.0.0 --port 8001 --reload" 2>/dev/null || true
    
    print_status "Starting Predictor API..."
    docker exec -d predictor-service bash -c "cd /app/predictor && pkill -f uvicorn || true && uvicorn main_working:app --host 0.0.0.0 --port 8002 --reload" 2>/dev/null || true
    
    sleep 5
    print_success "Backend services started"
}

# Start UI
start_ui() {
    print_step "Starting UI Dashboard..."
    
    docker compose up -d ui
    
    print_status "Waiting for UI (10 seconds)..."
    sleep 10
    
    print_success "UI Dashboard started"
}

# Verify services
verify_services() {
    print_step "Verifying services..."
    
    local all_good=true
    
    # Check each service
    if curl -s -f http://localhost:8000/health >/dev/null 2>&1; then
        print_success "Scraper API responding"
    else
        print_error "Scraper API not responding"
        all_good=false
    fi
    
    if curl -s -f http://localhost:8001/health >/dev/null 2>&1; then
        print_success "Intelligence API responding"
    else
        print_error "Intelligence API not responding"
        all_good=false
    fi
    
    if curl -s -f http://localhost:8002/health >/dev/null 2>&1; then
        print_success "Predictor API responding"
    else
        print_error "Predictor API not responding"
        all_good=false
    fi
    
    if curl -s -f http://localhost:8080/health >/dev/null 2>&1; then
        print_success "UI Dashboard responding"
    else
        print_error "UI Dashboard not responding"
        all_good=false
    fi
    
    if [ "$all_good" = false ]; then
        echo ""
        echo -e "${YELLOW}⚠️  Some services may still be starting...${NC}"
        echo -e "${YELLOW}   Wait 30 seconds and check: http://localhost:8080/${NC}"
    fi
}

# Show status
show_status() {
    echo ""
    echo -e "${GREEN}╔════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║                    DEMO IS READY!                              ║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    
    echo -e "${CYAN}🌐 MAIN DASHBOARD:${NC}"
    echo -e "   ${GREEN}http://localhost:8080/${NC}"
    echo ""
    
    echo -e "${CYAN}📡 BACKEND APIS:${NC}"
    echo "   • Scraper:        http://localhost:8000/docs"
    echo "   • Intelligence:   http://localhost:8001/docs"
    echo "   • Predictor:      http://localhost:8002/docs"
    echo ""
    
    echo -e "${CYAN}🔧 INFRASTRUCTURE:${NC}"
    echo "   • RabbitMQ UI:    http://localhost:15672/ (admin/password)"
    echo ""
    
    echo -e "${YELLOW}📋 USEFUL COMMANDS:${NC}"
    echo "   • View logs:      docker compose logs -f"
    echo "   • Stop demo:      docker compose down"
    echo "   • Restart:        docker compose restart"
    echo ""
    
    echo -e "${GREEN}✨ Open http://localhost:8080/ in your browser!${NC}"
    echo ""
}

# Show logs option
show_logs() {
    if [ "$1" = "--logs" ] || [ "$1" = "-l" ]; then
        print_status "Showing logs (Ctrl+C to exit)..."
        docker compose logs -f
    fi
}

# Main
main() {
    print_banner
    
    check_docker
    cleanup_ports
    stop_old
    start_infrastructure
    start_backends
    start_ui
    verify_services
    show_status
    
    show_logs "$@"
}

# Help
if [ "$1" = "--help" ] || [ "$1" = "-h" ]; then
    echo "Demo Run Script"
    echo ""
    echo "Usage: ./demo-run.sh [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --logs, -l    Show service logs after startup"
    echo "  --help, -h    Show this help"
    echo ""
    echo "Prerequisites:"
    echo "  Run ./demo-prep.sh first to ensure Docker is ready"
    echo ""
    exit 0
fi

main "$@"
