#!/bin/bash

# Start Container Script
# This script builds and starts the self-healing container

# Set error handling
set -e
trap 'echo "Error on line $LINENO"' ERR

# Set up logging
LOG_DIR="logs"
mkdir -p "$LOG_DIR"

# Logging function
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_DIR/container.log"
}

# Function to check Docker
check_docker() {
    if ! command -v docker &> /dev/null; then
        log "Docker not found. Please install Docker first."
        exit 1
    fi
    
    if ! docker info &> /dev/null; then
        log "Docker daemon not running. Please start Docker first."
        exit 1
    }
}

# Function to check Docker Compose
check_docker_compose() {
    if ! command -v docker-compose &> /dev/null; then
        log "Docker Compose not found. Please install Docker Compose first."
        exit 1
    }
}

# Function to prepare environment
prepare_environment() {
    log "Preparing environment"
    
    # Create necessary directories
    mkdir -p logs reports backups
    
    # Ensure scripts are executable
    chmod +x scripts/*.sh
    
    # Clean up old containers
    docker-compose down --remove-orphans || true
    
    # Remove old volumes
    docker volume prune -f || true
}

# Function to build container
build_container() {
    log "Building container"
    docker-compose build --no-cache
}

# Function to start container
start_container() {
    log "Starting container"
    docker-compose up -d
    
    # Wait for container to be ready
    sleep 5
    
    # Check container health
    if [ "$(docker-compose ps -q agent)" ]; then
        log "Container started successfully"
        
        # Show container logs
        log "Container logs:"
        docker-compose logs agent
        
        # Show dashboard URL
        log "Dashboard available at: http://localhost:8502"
    else
        log "Failed to start container"
        docker-compose logs agent
        exit 1
    fi
}

# Function to monitor container
monitor_container() {
    log "Monitoring container"
    
    while true; do
        # Check if container is running
        if ! docker-compose ps | grep -q "agent.*Up"; then
            log "Container stopped, restarting..."
            docker-compose up -d
        fi
        
        # Check container logs for errors
        if docker-compose logs --tail=100 agent | grep -i "error"; then
            log "Errors detected in container logs"
            # Container will fix itself due to self-healing capabilities
        fi
        
        # Sleep before next check
        sleep 10
    done
}

# Main execution
log "Starting self-healing container system"

# Check requirements
check_docker
check_docker_compose

# Prepare environment
prepare_environment

# Build container
build_container

# Start container
start_container

# Monitor container
monitor_container
