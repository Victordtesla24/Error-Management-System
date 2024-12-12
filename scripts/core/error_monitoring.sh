#!/bin/bash

# Error Management System - Error Monitoring
# Handles real-time error detection and monitoring

# Constants
readonly ERROR_LOG="logs/error.log"
readonly MONITOR_LOG="logs/monitor.log"
readonly MEMORY_THRESHOLD=90  # Memory usage threshold (%)
readonly DISK_THRESHOLD=90    # Disk usage threshold (%)
readonly CPU_THRESHOLD=90     # CPU usage threshold (%)

# Function to monitor system resources
monitor_resources() {
    log "Monitoring system resources..."
    
    # Check memory usage
    local memory_usage
    if is_macos; then
        memory_usage=$(vm_stat | perl -ne '/page size of (\d+)/ and $size=$1; /Pages active:\s+(\d+)/ and printf("%.2f", $1 * $size / 1048576 / 1024 * 100);')
    else
        memory_usage=$(free | grep Mem | awk '{print $3/$2 * 100.0}')
    fi
    
    # Check disk usage
    local disk_usage
    disk_usage=$(df -h . | tail -1 | awk '{print $5}' | sed 's/%//')
    
    # Check CPU usage
    local cpu_usage
    if is_macos; then
        cpu_usage=$(ps -A -o %cpu | awk '{s+=$1} END {print s}')
    else
        cpu_usage=$(top -bn1 | grep "Cpu(s)" | sed "s/.*, *\([0-9.]*\)%* id.*/\1/" | awk '{print 100 - $1}')
    fi
    
    # Log resource usage
    {
        echo "$(date '+%Y-%m-%d %H:%M:%S') MEMORY: ${memory_usage}%"
        echo "$(date '+%Y-%m-%d %H:%M:%S') DISK: ${disk_usage}%"
        echo "$(date '+%Y-%m-%d %H:%M:%S') CPU: ${cpu_usage}%"
    } >> "$MONITOR_LOG"
    
    # Check thresholds
    if [ "${memory_usage%.*}" -gt "$MEMORY_THRESHOLD" ]; then
        log "WARNING: High memory usage detected: ${memory_usage}%"
    fi
    
    if [ "${disk_usage%.*}" -gt "$DISK_THRESHOLD" ]; then
        log "WARNING: High disk usage detected: ${disk_usage}%"
    fi
    
    if [ "${cpu_usage%.*}" -gt "$CPU_THRESHOLD" ]; then
        log "WARNING: High CPU usage detected: ${cpu_usage}%"
    fi
}

# Function to monitor Python errors
monitor_python_errors() {
    log "Monitoring Python errors..."
    
    # Find all Python files
    local python_files
    python_files=$(find . -name "*.py" -not -path "./venv/*" -type f)
    
    # Check each file for syntax errors
    for file in $python_files; do
        if ! python3 -m py_compile "$file" 2>/dev/null; then
            log "ERROR: Syntax error in $file"
            python3 -m py_compile "$file" 2>> "$ERROR_LOG"
        fi
    done
}

# Function to monitor log files
monitor_logs() {
    log "Monitoring log files..."
    
    # Check for error patterns in logs
    local error_patterns=(
        "ERROR"
        "CRITICAL"
        "FATAL"
        "Exception"
        "Traceback"
        "Failed"
    )
    
    # Search for error patterns in all log files
    find logs -type f -name "*.log" | while read -r log_file; do
        for pattern in "${error_patterns[@]}"; do
            if grep -H "$pattern" "$log_file" >> "$ERROR_LOG"; then
                log "Found error pattern '$pattern' in $log_file"
            fi
        done
    done
}

# Function to monitor dependencies
monitor_dependencies() {
    log "Monitoring dependencies..."
    
    # Check if requirements.txt exists
    if file_exists "requirements.txt"; then
        # Check each package
        while read -r package; do
            # Skip empty lines and comments
            [[ -z "$package" || "$package" =~ ^# ]] && continue
            
            # Extract package name without version
            local pkg_name
            pkg_name=$(echo "$package" | cut -d'=' -f1 | cut -d'>' -f1 | cut -d'<' -f1 | tr -d ' ')
            
            # Check if package is installed
            if ! package_installed "$pkg_name"; then
                log "WARNING: Required package not installed: $pkg_name"
                echo "$(date '+%Y-%m-%d %H:%M:%S') MISSING DEPENDENCY: $pkg_name" >> "$ERROR_LOG"
            fi
        done < "requirements.txt"
    fi
}

# Function to monitor file changes
monitor_file_changes() {
    log "Monitoring file changes..."
    
    # Store current state of files
    find . -type f -not -path "./venv/*" -not -path "./.git/*" -exec md5sum {} \; > "logs/file_state.tmp"
    
    # Compare with previous state if exists
    if file_exists "logs/file_state.prev"; then
        # Check for changes
        if ! diff "logs/file_state.prev" "logs/file_state.tmp" > /dev/null; then
            log "Detected file changes"
            diff "logs/file_state.prev" "logs/file_state.tmp" | grep "^[<>]" >> "$MONITOR_LOG"
        fi
    fi
    
    # Update previous state
    mv "logs/file_state.tmp" "logs/file_state.prev"
}

# Function to analyze errors
analyze_errors() {
    log "Analyzing errors..."
    
    if file_exists "$ERROR_LOG"; then
        # Count error types
        log "Error summary:"
        {
            echo "=== Error Analysis $(date '+%Y-%m-%d %H:%M:%S') ==="
            echo "Syntax Errors: $(grep -c "SyntaxError" "$ERROR_LOG")"
            echo "Import Errors: $(grep -c "ImportError" "$ERROR_LOG")"
            echo "Runtime Errors: $(grep -c "RuntimeError" "$ERROR_LOG")"
            echo "Attribute Errors: $(grep -c "AttributeError" "$ERROR_LOG")"
            echo "Type Errors: $(grep -c "TypeError" "$ERROR_LOG")"
            echo "Name Errors: $(grep -c "NameError" "$ERROR_LOG")"
            echo "=== End Analysis ==="
        } >> "$MONITOR_LOG"
    fi
}

# Main execution
main() {
    # Ensure log directory exists
    ensure_dir "logs"
    
    # Initialize or rotate logs
    for log_file in "$ERROR_LOG" "$MONITOR_LOG"; do
        if file_exists "$log_file" && [ "$(wc -l < "$log_file")" -gt 1000 ]; then
            mv "$log_file" "${log_file}.$(date '+%Y%m%d_%H%M%S')"
        fi
        touch "$log_file"
    done
    
    # Run monitoring functions
    monitor_resources
    monitor_python_errors
    monitor_logs
    monitor_dependencies
    monitor_file_changes
    analyze_errors
}

# Run main function
main 