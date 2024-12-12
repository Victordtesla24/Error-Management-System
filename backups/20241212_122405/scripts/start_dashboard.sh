#!/bin/bash

# Start Dashboard Script
# This script starts the dashboard service with proper initialization

# Set error handling
set -e
trap 'echo "Error on line $LINENO"' ERR

# Set up logging
LOG_DIR="logs"
mkdir -p "$LOG_DIR"

# Set environment variables
export PYTHONPATH=/Users/admin/cursor/error-management-system
export LOG_LEVEL=INFO
export DASHBOARD_PORT=8502

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Cleaning up existing processes..."
pkill -f "streamlit run" || true
sleep 2

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Starting dashboard..."

# Ensure virtual environment is activated
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
fi

# Install dependencies if needed
if [ ! -f "venv/bin/activate" ] || ! pip freeze | grep -q streamlit; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Installing dependencies..."
    python -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
fi

# Initialize logs
for service in "dashboard" "error_manager" "agent_manager" "task_manager"; do
    touch "$LOG_DIR/${service}.log"
    chmod 644 "$LOG_DIR/${service}.log"
done

# Start dashboard with proper logging
streamlit run src/dashboard/error_dashboard.py \
    --server.port=$DASHBOARD_PORT \
    --server.address=localhost \
    --server.baseUrlPath="" \
    --server.enableCORS=false \
    --server.enableXsrfProtection=true \
    --server.maxUploadSize=200 \
    --browser.serverAddress=localhost \
    --browser.gatherUsageStats=false \
    --logger.level=info \
    2>&1 | tee -a "$LOG_DIR/dashboard.log"