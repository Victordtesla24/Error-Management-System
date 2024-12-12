#!/bin/bash

# Error Management System - Verification and Fix Script
# Main coordinator script that manages the verification and fix process

set -euo pipefail
trap 'echo "Error on line $LINENO. Exit code: $?"' ERR

# Constants
readonly SCRIPTS_DIR="scripts/core"
readonly LOGS_DIR="logs"
readonly VERIFY_LOG="$LOGS_DIR/verify.log"
readonly ERROR_PATTERNS_FILE="$LOGS_DIR/error_patterns.txt"
readonly MAX_RUNTIME=300  # 5 minutes timeout
readonly MAX_MEMORY=70    # 70% memory threshold
readonly MAX_CPU=70      # 70% CPU threshold

# Source utility functions
source "$SCRIPTS_DIR/utils.sh"

# Function to initialize logging
init_logging() {
    ensure_dir "$LOGS_DIR"
    
    # Create or rotate verify log
    if file_exists "$VERIFY_LOG" && [ "$(wc -l < "$VERIFY_LOG")" -gt 1000 ]; then
        mv "$VERIFY_LOG" "${VERIFY_LOG}.$(date '+%Y%m%d_%H%M%S')"
    fi
    
    # Create error patterns file if it doesn't exist
    if ! file_exists "$ERROR_PATTERNS_FILE"; then
        cat > "$ERROR_PATTERNS_FILE" << 'EOL'
# Format: ERROR_PATTERN|FIX_TYPE|FIX_ACTION
Failed to activate virtual environment|venv|fix_venv_activation
Read-only file system|permissions|fix_permissions
Resource usage too high|resources|adjust_resource_limits
No space left on device|disk|clean_disk_space
No such file or directory|paths|fix_paths
command not found|command|fix_missing_command
ModuleNotFoundError|python|fix_python_imports
SyntaxWarning|syntax|fix_syntax_warning
ImportError|imports|fix_import_error
PermissionError|permissions|fix_permissions
EOL
    fi
    
    # Start logging
    exec 1> >(tee -a "$VERIFY_LOG")
    exec 2> >(tee -a "$VERIFY_LOG" >&2)
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

# Function to analyze and fix script
analyze_and_fix() {
    log "Analyzing script execution..."
    
    local fixes_applied=0
    local total_errors=0
    
    # Read error patterns and apply fixes
    while IFS='|' read -r pattern fix_type fix_action; do
        # Skip comments and empty lines
        [[ "$pattern" =~ ^#.*$ || -z "$pattern" ]] && continue
        
        # Count matches
        local matches
        matches=$(grep -c "$pattern" "$VERIFY_LOG" || true)
        total_errors=$((total_errors + matches))
        
        if [ "$matches" -gt 0 ]; then
            log "Found $matches occurrences of '$pattern' ($fix_type)"
            
            case "$fix_type" in
                venv)
                    # Fix virtual environment issues
                    sed -i.bak 's|source "$VENV_DIR/bin/activate"|source "${VENV_DIR}/bin/activate" 2>/dev/null|g' "$SCRIPTS_DIR/python_setup.sh"
                    fixes_applied=$((fixes_applied + 1))
                    ;;
                    
                permissions)
                    # Fix permission issues
                    find . -type d -exec chmod 755 {} \;
                    find . -type f -exec chmod 644 {} \;
                    chmod +x scripts/*.sh scripts/core/*.sh
                    fixes_applied=$((fixes_applied + 1))
                    ;;
                    
                resources)
                    # Adjust resource limits
                    sed -i.bak "s/MAX_MEMORY=.*/MAX_MEMORY=60    # 60% memory threshold/" "$0"
                    sed -i.bak "s/MAX_CPU=.*/MAX_CPU=60      # 60% CPU threshold/" "$0"
                    fixes_applied=$((fixes_applied + 1))
                    ;;
                    
                disk)
                    # Clean disk space
                    clean_system
                    fixes_applied=$((fixes_applied + 1))
                    ;;
                    
                paths)
                    # Fix path issues
                    sed -i.bak 's|/\([^/]*\)"|"\1"|g' "$SCRIPTS_DIR"/*.sh
                    fixes_applied=$((fixes_applied + 1))
                    ;;
                    
                command)
                    # Fix missing commands
                    if grep -q "py3clean" "$VERIFY_LOG"; then
                        sed -i.bak '/py3clean/d' "$0"
                        fixes_applied=$((fixes_applied + 1))
                    fi
                    ;;
                    
                python)
                    # Fix Python import issues
                    if ! grep -q "PYTHONPATH" "$0"; then
                        sed -i.bak '1a\
export PYTHONPATH="$PWD:$PYTHONPATH"' "$0"
                        fixes_applied=$((fixes_applied + 1))
                    fi
                    ;;
                    
                syntax)
                    # Fix syntax warnings
                    if grep -q "is not.*literal" "$VERIFY_LOG"; then
                        find . -name "*.py" -type f -exec sed -i.bak 's/\(.*\) is not \([0-9.-][0-9.]*\)/\1 != \2/g' {} \;
                        fixes_applied=$((fixes_applied + 1))
                    fi
                    ;;
                    
                imports)
                    # Fix import errors
                    if ! grep -q "init_imports" "$0"; then
                        cat >> "$SCRIPTS_DIR/python_setup.sh" << 'EOL'
                        
# Function to initialize imports
init_imports() {
    local src_init="src/__init__.py"
    local tests_init="tests/__init__.py"
    
    # Create __init__.py files if they don't exist
    for init_file in "$src_init" "$tests_init"; do
        if [ ! -f "$init_file" ]; then
            mkdir -p "$(dirname "$init_file")"
            touch "$init_file"
        fi
    done
}
EOL
                        sed -i.bak '/verify_packages/i\    init_imports' "$SCRIPTS_DIR/python_setup.sh"
                        fixes_applied=$((fixes_applied + 1))
                    fi
                    ;;
            esac
        fi
    done < "$ERROR_PATTERNS_FILE"
    
    # Remove backup files
    find . -name "*.bak" -type f -delete
    
    # Report results
    log "Analysis complete: found $total_errors issues, applied $fixes_applied fixes"
    
    # Suggest restart if fixes were applied
    if [ "$fixes_applied" -gt 0 ]; then
        log "Fixes applied - please run the script again"
        return 1
    fi
    
    return 0
}

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

# Main execution
main() {
    log "Starting verification and fix process..."
    
    # Initialize logging
    init_logging
    
    # Clean system first
    clean_system
    
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
    local all_success=true
    for script in "${scripts[@]}"; do
        if [ -x "$script" ]; then
            log "Running $(basename "$script")..."
            if ! run_with_timeout "$script" "$MAX_RUNTIME"; then
                log "WARNING: $(basename "$script") failed or was terminated"
                all_success=false
                continue
            fi
        else
            log "WARNING: $script not found or not executable"
            all_success=false
        fi
    done
    
    log "Verification and fix process completed!"
    
    # Analyze and fix if there were any issues
    if ! $all_success; then
        analyze_and_fix
    fi
}

# Run main function with all arguments
main "$@"
