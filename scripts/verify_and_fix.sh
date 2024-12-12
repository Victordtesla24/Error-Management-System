#!/bin/bash

# Error Management System - Verification and Fix Script
# Main coordinator script that manages the verification and fix process

set -euo pipefail
trap 'echo "Error on line $LINENO. Exit code: $?"' ERR

# Constants
readonly SCRIPTS_DIR="scripts/core"
readonly LOGS_DIR="logs"
readonly MAX_RUNTIME=300  # 5 minutes timeout
readonly MAX_MEMORY=70    # 70% memory threshold
readonly MAX_CPU=70      # 70% CPU threshold

# Source utility functions
source "$SCRIPTS_DIR/utils.sh"

# Function to check resource usage
check_resources() {
    local memory_usage
    local cpu_usage
    
    if is_macos; then
        memory_usage=$(vm_stat | perl -ne '/page size of (\d+)/ and $size=$1; /Pages active:\s+(\d+)/ and printf("%.2f", $1 * $size / 1048576 / 1024 * 100);')
        cpu_usage=$(ps -A -o %cpu | awk '{s+=$1} END {print s}')
    else
        memory_usage=$(free | grep Mem | awk '{print $3/$2 * 100.0}')
        cpu_usage=$(top -bn1 | grep "Cpu(s)" | sed "s/.*, *\([0-9.]*\)%* id.*/\1/" | awk '{print 100 - $1}')
    fi
    
    if [ "${memory_usage%.*}" -gt "$MAX_MEMORY" ] || [ "${cpu_usage%.*}" -gt "$MAX_CPU" ]; then
        log "WARNING: Resource usage too high. Memory: ${memory_usage}%, CPU: ${cpu_usage}%"
        log "Attempting to free resources..."
        
        # Clean up temporary files
        find . -type f -name "*.pyc" -delete
        find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
        
        # Clear Python cache
        py3clean .
        
        # Clear system cache (requires sudo)
        # sudo purge
        
        return 1
    fi
    
    return 0
}

# Function to run script with timeout
run_with_timeout() {
    local script="$1"
    local timeout="$2"
    
    # Run script in background
    "$script" &
    local pid=$!
    
    # Wait for script with timeout
    local count=0
    while kill -0 $pid 2>/dev/null; do
        if [ $count -ge "$timeout" ]; then
            log "WARNING: Script $script timed out after ${timeout}s"
            kill -TERM $pid 2>/dev/null || true
            kill -KILL $pid 2>/dev/null || true
            return 1
        fi
        sleep 1
        ((count++))
        
        # Check resources every 5 seconds
        if [ $((count % 5)) -eq 0 ] && ! check_resources; then
            log "WARNING: Script $script terminated due to high resource usage"
            kill -TERM $pid 2>/dev/null || true
            kill -KILL $pid 2>/dev/null || true
            return 1
        fi
    done
    
    wait $pid
    return $?
}

# Function to ensure required directories exist
init_directories() {
    mkdir -p "$LOGS_DIR"
    chmod 755 "$LOGS_DIR"
}

# Function to clean system
clean_system() {
    log "Cleaning system..."
    
    # Remove Python cache
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find . -name "*.pyc" -delete
    
    # Remove test cache
    find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
    find . -name ".coverage" -delete
    
    # Remove build artifacts
    find . -type d -name "build" -exec rm -rf {} + 2>/dev/null || true
    find . -type d -name "dist" -exec rm -rf {} + 2>/dev/null || true
    find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
    
    # Clear disk cache (if possible)
    if command_exists purge && is_macos; then
        sudo purge
    fi
}

# Main execution
main() {
    log "Starting verification and fix process..."
    
    # Clean system first
    clean_system
    
    # Initialize directories
    init_directories
    
    # Array of scripts to run
    local scripts=(
        "$SCRIPTS_DIR/python_setup.sh"
        "$SCRIPTS_DIR/project_structure.sh"
        "$SCRIPTS_DIR/code_cleanup.sh"
        "$SCRIPTS_DIR/error_monitoring.sh"
        "$SCRIPTS_DIR/linting.sh"
        "$SCRIPTS_DIR/documentation.sh"
        "$SCRIPTS_DIR/testing.sh"
        "$SCRIPTS_DIR/git_management.sh"
    )
    
    # Run each script with timeout and resource checks
    for script in "${scripts[@]}"; do
        if [ -x "$script" ]; then
            log "Running $(basename "$script")..."
            if ! run_with_timeout "$script" "$MAX_RUNTIME"; then
                log "WARNING: $(basename "$script") failed or was terminated"
                continue
            fi
        else
            log "WARNING: $script not found or not executable"
        fi
    done
    
    log "Verification and fix process completed!"
}

# Run main function with all arguments
main "$@"
