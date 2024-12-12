#!/bin/bash

# Start Error Management Service Script
# This script starts the error management service with Sentry integration

# Set error handling
set -e
trap 'echo "Error on line $LINENO"' ERR

# Set up logging
LOG_DIR="logs"
mkdir -p "$LOG_DIR"

# Set environment variables
export PYTHONPATH=/Users/admin/cursor/error-management-system
export SENTRY_DSN="https://your-sentry-dsn@sentry.io/123456"  # Replace with actual DSN
export LOG_LEVEL=INFO
export AUTO_FIX=1
export MONITOR_ENABLED=1
export ERROR_DETECTION_ENABLED=1

# Install dependencies if needed
if [ ! -f "venv/bin/activate" ]; then
    echo "Creating virtual environment..."
    python -m venv venv
fi

source venv/bin/activate

echo "Installing dependencies..."
pip install -r requirements.txt

# Start error management service
echo "Starting error management service..."
python -c "
from src.error_management.service import error_management_service
error_management_service.start()
" &

# Store PID
echo $! > "$LOG_DIR/error_management.pid"

# Monitor logs
tail -f "$LOG_DIR/error_management.log" "$LOG_DIR/agent.log" "$LOG_DIR/monitor.log"
