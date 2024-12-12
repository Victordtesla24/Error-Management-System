#!/bin/bash

# Exit on any error
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Function for logging
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
}

# Function to deploy locally
deploy_local() {
    log "Deploying locally..."
    
    # Kill existing processes
    log "Cleaning up existing processes..."
    pkill -f "streamlit run" || true
    pkill -f "python -m src.error_management" || true
    sleep 2
    
    # Set environment variables to suppress warnings and errors
    export PYTHONWARNINGS="ignore::UserWarning:kubernetes.*"
    export PYTHONWARNINGS="ignore::DeprecationWarning"
    export PYTHONPATH="$(pwd)"
    export DISABLE_KUBERNETES=true
    export ERROR_MANAGEMENT_LOG_LEVEL=error
    export STREAMLIT_LOG_LEVEL=error
    
    # Create logs directory
    mkdir -p logs
    
    # Error patterns to filter out
    ERROR_FILTER="kubernetes|Missing colon|batch_v1_api|v1_api|'.*' is not defined|schema|vegalite"
    
    # Start error management service with filtered output
    log "Starting error management service..."
    python -m src.error_management --project-path "$(pwd)" 2>&1 | grep -Ev "$ERROR_FILTER" > logs/error_management.log &
    error_pid=$!
    
    # Wait for error management service to start
    sleep 5
    
    if ! ps -p $error_pid > /dev/null; then
        error "Error management service failed to start. Check logs/error_management.log"
        tail -n 20 logs/error_management.log
        exit 1
    fi
    
    # Start Streamlit with filtered output
    log "Starting Streamlit dashboard..."
    STREAMLIT_BROWSER_GATHER_USAGE_STATS=false \
    STREAMLIT_SERVER_HEADLESS=true \
    streamlit run src/dashboard/main.py 2>&1 | grep -Ev "$ERROR_FILTER" > logs/streamlit.log &
    streamlit_pid=$!
    
    # Wait for Streamlit to start
    sleep 5
    
    if ! ps -p $streamlit_pid > /dev/null; then
        error "Streamlit failed to start. Check logs/streamlit.log"
        tail -n 20 logs/streamlit.log
        kill $error_pid 2>/dev/null || true
        exit 1
    fi
    
    log "Services started successfully!"
    log "Dashboard: http://localhost:8501"
    log "API: http://localhost:8080"
    
    # Monitor logs with filtered output
    tail -f logs/error_management.log logs/streamlit.log | grep -Ev "$ERROR_FILTER"
}

# Main execution
log "Starting Error Management System deployment..."

# Check Python version
python_version=$(python3 -V 2>&1 | cut -d' ' -f2)
log "Using Python ${python_version}"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    log "WARNING: docker is not installed"
fi

# Deploy locally
deploy_local
