#!/bin/bash

# Start Error Management System Script
# This script starts all components of the error management system

# Set error handling
set -e
trap 'echo "Error on line $LINENO"' ERR

# Set up logging
LOG_DIR="logs"
mkdir -p "$LOG_DIR"

# Set environment variables
export PYTHONPATH=/Users/admin/cursor/error-management-system
export LOG_LEVEL=INFO
export AUTO_FIX=1
export MONITOR_ENABLED=1
export ERROR_DETECTION_ENABLED=1

# Function to check if process is running
check_process() {
    pgrep -f "$1" >/dev/null
}

# Function to start autonomous agent
start_agent() {
    echo "Starting autonomous agent..."
    python3 -c "
import asyncio
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
    echo "Starting dashboard..."
    streamlit run src/dashboard/error_dashboard.py --server.port=8502 \
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

# Kill any existing processes
pkill -f "python -m" || true
pkill -f "streamlit run" || true

sleep 2

# Ensure virtual environment is activated
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
fi

# Install dependencies if needed
if [ ! -f "venv/bin/activate" ] || ! pip freeze | grep -q streamlit; then
    echo "Installing dependencies..."
    python -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
fi

# Initialize logs
for service in "dashboard" "error_manager" "agent_manager" "task_manager" "log_monitor"; do
    touch "$LOG_DIR/${service}.log"
    chmod 644 "$LOG_DIR/${service}.log"
done

# Start components
start_agent
sleep 2
start_dashboard

# Monitor processes
echo "Monitoring system components..."
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
    echo -e "\nRecent monitor log:"
    tail -n 5 "$LOG_DIR/log_monitor.log" 2>/dev/null || true
    
    echo -e "\nRecent agent log:"
    tail -n 5 "$LOG_DIR/agent.log" 2>/dev/null || true
    
    echo -e "\nRecent dashboard log:"
    tail -n 5 "$LOG_DIR/dashboard.log" 2>/dev/null || true
    
    sleep 10
done
