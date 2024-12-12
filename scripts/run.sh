#!/bin/bash

# Error Management System - Run Script
# Handles deployment, monitoring, and runtime management

set -e
trap 'echo "Error on line $LINENO"' ERR

# Environment Setup
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
export LOG_LEVEL=${LOG_LEVEL:-INFO}
export AUTO_FIX=${AUTO_FIX:-1}
export MONITOR_ENABLED=${MONITOR_ENABLED:-1}

# Constants
LOG_DIR="logs"
VENV_DIR="venv"
STREAMLIT_PORT=8502

# Load environment variables
if [ -f ".env" ]; then
    set -a
    source .env
    set +a
fi

# Function to initialize logging
init_logs() {
    echo "Initializing logs..."
    mkdir -p "$LOG_DIR"
    for service in "dashboard" "error_manager" "agent" "monitor"; do
        touch "$LOG_DIR/${service}.log"
        chmod 644 "$LOG_DIR/${service}.log"
    done
}

# Function to setup environment
setup_env() {
    echo "Setting up environment..."
    
    # Create and activate virtual environment
    if [ ! -d "$VENV_DIR" ]; then
        python3 -m venv "$VENV_DIR"
    fi
    source "$VENV_DIR/bin/activate"
    
    # Install dependencies
    pip install -r requirements.txt
    
    # Run verify_and_fix script
    ./scripts/verify_and_fix.sh --all
}

# Function to start Streamlit dashboard
start_dashboard() {
    echo "Starting Streamlit dashboard..."
    streamlit run src/pages/1_🏠_Home.py \
        --server.port=$STREAMLIT_PORT \
        --server.address=localhost \
        --server.baseUrlPath="" \
        --server.enableCORS=false \
        --server.enableXsrfProtection=true \
        --server.maxUploadSize=200 \
        --browser.gatherUsageStats=false \
        --logger.level=$LOG_LEVEL \
        2>&1 | tee -a "$LOG_DIR/dashboard.log" &
    echo $! > "$LOG_DIR/dashboard.pid"
}

# Function to start error management system
start_error_system() {
    echo "Starting error management system..."
    python3 -m src.core.error_manager \
        2>&1 | tee -a "$LOG_DIR/error_manager.log" &
    echo $! > "$LOG_DIR/error_manager.pid"
}

# Function to monitor system health
monitor_system() {
    echo "Starting system monitoring..."
    while true; do
        # Check dashboard
        if ! pgrep -f "streamlit run" > /dev/null; then
            echo "Dashboard down, restarting..."
            start_dashboard
        fi
        
        # Check error system
        if ! pgrep -f "src.core.error_manager" > /dev/null; then
            echo "Error system down, restarting..."
            start_error_system
        fi
        
        # Show recent logs
        echo -e "\nRecent logs:"
        for log in dashboard error_manager; do
            echo -e "\n=== $log ==="
            tail -n 3 "$LOG_DIR/${log}.log" 2>/dev/null || true
        done
        
        sleep 30
    done
}

# Function to cleanup
cleanup() {
    echo "Cleaning up..."
    pkill -f "streamlit run" || true
    pkill -f "src.core.error_manager" || true
    rm -f "$LOG_DIR"/*.pid
}

# Main execution
main() {
    # Cleanup any existing processes
    cleanup
    
    # Initialize system
    init_logs
    setup_env
    
    # Start components
    start_dashboard
    start_error_system
    
    # Monitor system
    monitor_system
}

# Handle interrupts
trap cleanup EXIT

# Run main function
main 