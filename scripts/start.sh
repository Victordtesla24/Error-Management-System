#!/bin/bash

# Consolidated startup script for Error Management System
# Handles all initialization, monitoring, and management

# Set error handling
set -e
trap 'echo "Error on line $LINENO"' ERR

# Set up logging
LOG_DIR="logs"
mkdir -p "$LOG_DIR"

# Set environment variables
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
export LOG_LEVEL=INFO
export AUTO_FIX=1
export MONITOR_ENABLED=1
export ERROR_DETECTION_ENABLED=1

# Load environment variables
if [ -f ".env" ]; then
    export $(cat .env | xargs)
fi

# Function to check if process is running
check_process() {
    pgrep -f "$1" >/dev/null
}

# Function to start autonomous agent
start_agent() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Starting autonomous agent..."
    python3 -c "
import asyncio
import os
from src.error_management.autonomous_agent import autonomous_agent
from src.error_management.log_monitor import log_monitor

async def main():
    try:
        # Initialize and start log monitor
        await log_monitor.start()
        
        # Initialize and start agent
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            raise ValueError('ANTHROPIC_API_KEY not found')
            
        await autonomous_agent.initialize(api_key)
        await autonomous_agent.start()
        
        # Keep running
        while True:
            await asyncio.sleep(1)
    except Exception as e:
        print(f'Error starting agent: {e}')
        raise

asyncio.run(main())
" &
    AGENT_PID=$!
    echo $AGENT_PID > "$LOG_DIR/agent.pid"
    echo "Agent started with PID: $AGENT_PID"
}

# Function to start dashboard
start_dashboard() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Starting dashboard..."
    streamlit run src/dashboard/error_dashboard.py \
        --server.port=8502 \
        --server.address=localhost \
        --server.baseUrlPath="" \
        --server.enableCORS=false \
        --server.enableXsrfProtection=true \
        --server.maxUploadSize=200 \
        --browser.serverAddress=localhost \
        --browser.gatherUsageStats=false \
        --logger.level=info \
        2>&1 | tee -a "$LOG_DIR/dashboard.log" &
    DASHBOARD_PID=$!
    echo $DASHBOARD_PID > "$LOG_DIR/dashboard.pid"
    echo "Dashboard started with PID: $DASHBOARD_PID"
}

# Function to verify and fix project structure
verify_and_fix() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Verifying project structure..."
    
    # Ensure required directories exist
    for dir in "src" "tests" "logs" "docs"; do
        mkdir -p "$dir"
    done
    
    # Ensure required files exist
    touch README.md
    touch requirements.txt
    touch pytest.ini
    touch .env
    
    # Set proper permissions
    find . -type d -exec chmod 755 {} \;
    find . -type f -exec chmod 644 {} \;
    chmod +x scripts/*.sh
    
    # Clean up unnecessary files
    find . -type f -name "*.pyc" -delete
    find . -type d -name "__pycache__" -exec rm -r {} + 2>/dev/null || true
    find . -type d -name ".pytest_cache" -exec rm -r {} + 2>/dev/null || true
}

# Function to clean up old processes
cleanup_processes() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Cleaning up existing processes..."
    pkill -f "streamlit run" || true
    pkill -f "python -m" || true
    sleep 2
}

# Function to setup virtual environment
setup_venv() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Setting up virtual environment..."
    
    # Create and activate virtual environment if needed
    if [ ! -f "venv/bin/activate" ]; then
        python -m venv venv
    fi
    source venv/bin/activate
    
    # Install dependencies
    pip install -r requirements.txt
}

# Function to initialize logs
init_logs() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Initializing logs..."
    
    # Initialize log files
    for service in "dashboard" "error_manager" "agent_manager" "task_manager" "log_monitor"; do
        touch "$LOG_DIR/${service}.log"
        chmod 644 "$LOG_DIR/${service}.log"
    done
}

# Main execution
main() {
    cleanup_processes
    verify_and_fix
    setup_venv
    init_logs
    
    start_agent
    sleep 2
    start_dashboard
    
    # Monitor processes
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Monitoring system components..."
    while true; do
        if ! check_process "autonomous_agent.py"; then
            echo "Agent died, restarting..."
            start_agent
        fi
        
        if ! check_process "streamlit"; then
            echo "Dashboard died, restarting..."
            start_dashboard
        fi
        
        # Show recent log entries
        for log in "log_monitor" "agent" "dashboard"; do
            echo -e "\nRecent ${log} log:"
            tail -n 5 "$LOG_DIR/${log}.log" 2>/dev/null || true
        done
        
        sleep 10
    done
}

# Run main function
main 