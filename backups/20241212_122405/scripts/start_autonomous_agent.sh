#!/bin/bash

# Set error handling
set -e
trap 'echo "Error on line $LINENO"' ERR

# Set up logging
LOG_DIR="logs"
mkdir -p "$LOG_DIR"

# Logging function
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_DIR/autonomous_agent.log"
}

# Set Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Load environment variables from .env file
if [ -f ".env" ]; then
    export $(cat .env | xargs)
fi

# Check if API key exists
if [ -z "$ANTHROPIC_API_KEY" ]; then
    log "Error: ANTHROPIC_API_KEY not found in .env file"
    exit 1
fi

# Start the autonomous agent
log "Starting autonomous agent..."
PYTHONPATH="$(pwd)" python3 -c "
import asyncio
import os
import sys
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('logs/autonomous_agent.log')
    ]
)

sys.path.insert(0, os.getcwd())

from src.error_management.autonomous_agent import autonomous_agent

async def main():
    try:
        await autonomous_agent.initialize('$ANTHROPIC_API_KEY')
        await autonomous_agent.start()
    except Exception as e:
        logging.error(f'Error starting agent: {str(e)}')
        raise

asyncio.run(main())" 