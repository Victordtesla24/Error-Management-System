#!/bin/bash

# Function to handle errors
handle_error() {
    local error_file=$1
    local error_line=$2
    local error_msg=$3
    
    echo "[$(date)] Error in $error_file:$error_line - $error_msg" >> /app/logs/container.log
    
    # Run verify and fix script
    /app/scripts/verify_and_fix.sh
    
    # Run tests
    python -m pytest tests/
    
    # Restart affected services
    pkill -f "python -m" || true
    sleep 2
    
    # Start services again
    python -m src.error_management &
    python -m src.agent.main &
}

# Set up error trap
trap 'handle_error "${BASH_SOURCE}" "${LINENO}" "${BASH_COMMAND}"' ERR

# Start file monitoring
inotifywait -m -r -e modify,create,delete /app/src /app/tests | while read path action file; do
    echo "[$(date)] File change detected: $path$file" >> /app/logs/container.log
    /app/scripts/verify_and_fix.sh
done &

# Start error management service
python -m src.error_management &

# Start agent
python -m src.agent.main &

# Start autonomous agent
/app/scripts/start_autonomous_agent.sh &

# Start dashboard
streamlit run src/dashboard/error_dashboard.py --server.port=8502 --server.address=0.0.0.0 &

# Keep container running and monitor logs
tail -f /app/logs/*.log
