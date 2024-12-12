#!/bin/bash

# Error Management System - Core Utilities
# Common functions and constants used across all scripts

# Get absolute path to project root
readonly PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

# Constants
readonly VENV_DIR="$PROJECT_ROOT/venv"
readonly DOCS_DIR="$PROJECT_ROOT/docs"
readonly SRC_DIR="$PROJECT_ROOT/src"
readonly TESTS_DIR="$PROJECT_ROOT/tests"
readonly STREAMLIT_DIR="$PROJECT_ROOT/.streamlit"
readonly GITHUB_REPO="https://github.com/Victordtesla24/Error-Management-System.git"
readonly MIN_PYTHON_VERSION="3.11"
readonly MAX_PYTHON_VERSION="3.11"
readonly MAX_MEMORY_USAGE=80
readonly MAX_CPU_USAGE=80

# Function to log messages with timestamp
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to ensure a directory exists
ensure_dir() {
    local dir="$PROJECT_ROOT/$1"
    if [ ! -d "$dir" ]; then
        mkdir -p "$dir" || {
            log "ERROR: Failed to create directory: $1"
            return 1
        }
        log "Created directory: $1"
    fi
}

# Function to check if we're in a virtual environment
in_venv() {
    [ -n "${VIRTUAL_ENV:-}" ]
}

# Function to check if a file exists
file_exists() {
    [ -f "$PROJECT_ROOT/$1" ]
}

# Function to check if a directory exists
dir_exists() {
    [ -d "$PROJECT_ROOT/$1" ]
}

# Function to get OS type
get_os() {
    case "$OSTYPE" in
        darwin*)  echo "macos" ;;
        linux*)   echo "linux" ;;
        *)        echo "unknown" ;;
    esac
}

# Function to check if running on macOS
is_macos() {
    [ "$(get_os)" = "macos" ]
}

# Function to check if running on Linux
is_linux() {
    [ "$(get_os)" = "linux" ]
}

# Function to get Python version
get_python_version() {
    python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))'
}

# Function to check if a Python package is installed
package_installed() {
    python3 -c "import $1" 2>/dev/null
}

# Function to backup a file
backup_file() {
    local file="$PROJECT_ROOT/$1"
    if [ -f "$file" ]; then
        cp "$file" "${file}.bak" || {
            log "ERROR: Failed to create backup: $1"
            return 1
        }
        log "Created backup: $1.bak"
    fi
}

# Function to restore a file from backup
restore_file() {
    local file="$PROJECT_ROOT/$1"
    if [ -f "${file}.bak" ]; then
        mv "${file}.bak" "$file" || {
            log "ERROR: Failed to restore backup: $1"
            return 1
        }
        log "Restored from backup: $1"
    fi
}

# Function to remove backup files
cleanup_backups() {
    find "$PROJECT_ROOT" -name "*.bak" -type f -delete
    log "Removed backup files"
}

# Function to get file hash (MD5)
get_file_hash() {
    local file="$PROJECT_ROOT/$1"
    if is_macos; then
        md5 -q "$file"
    else
        md5sum "$file" | cut -d' ' -f1
    fi
}

# Function to check if a port is in use
port_in_use() {
    local port="$1"
    if is_macos; then
        lsof -i ":$port" >/dev/null 2>&1
    else
        netstat -tuln | grep -q ":$port "
    fi
}

# Function to find available port starting from base
find_available_port() {
    local port="$1"
    while port_in_use "$port"; do
        port=$((port + 1))
    done
    echo "$port"
}

# Function to check memory usage
check_memory() {
    if is_macos; then
        vm_stat | perl -ne '/page size of (\d+)/ and $size=$1; /Pages\s+([^:]+)[^\d]+(\d+)/ and printf("%-16s % 16.2f Mi\n", "$1:", $2 * $size / 1048576);'
    else
        free -m
    fi
}

# Function to check disk usage
check_disk() {
    df -h "$PROJECT_ROOT"
}

# Function to get current git branch
get_git_branch() {
    git -C "$PROJECT_ROOT" rev-parse --abbrev-ref HEAD 2>/dev/null
}

# Function to check if git repo is clean
git_is_clean() {
    git -C "$PROJECT_ROOT" diff --quiet HEAD 2>/dev/null
}

# Function to check resource usage
check_resources() {
    local memory_usage
    local cpu_usage
    
    if is_macos; then
        memory_usage=$(ps -o %mem= -p $$)
        cpu_usage=$(ps -o %cpu= -p $$)
    else
        memory_usage=$(free | grep Mem | awk '{print $3/$2 * 100.0}')
        cpu_usage=$(top -bn1 | grep "Cpu(s)" | sed "s/.*, *\([0-9.]*\)%* id.*/\1/" | awk '{print 100 - $1}')
    fi
    
    memory_usage=${memory_usage%.*}
    cpu_usage=${cpu_usage%.*}
    
    if [ "$memory_usage" -gt "$MAX_MEMORY_USAGE" ] || [ "$cpu_usage" -gt "$MAX_CPU_USAGE" ]; then
        log "WARNING: Resource usage too high. Memory: $memory_usage%, CPU: $cpu_usage%"
        return 1
    fi
    
    return 0
}

# Function to clean up resources
cleanup_resources() {
    log "Cleaning up resources..."
    
    # Clear Python cache
    find "$PROJECT_ROOT" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find "$PROJECT_ROOT" -type f -name "*.pyc" -delete 2>/dev/null || true
    
    # Clear temporary files
    find "$PROJECT_ROOT" -type f -name "*.tmp" -delete 2>/dev/null || true
    find "$PROJECT_ROOT" -type f -name "*.log" -mtime +7 -delete 2>/dev/null || true
    
    # Clear pip cache if in venv
    if in_venv && command -v pip &> /dev/null; then
        pip cache purge &> /dev/null || true
    fi
}

# Export functions
export -f log
export -f command_exists
export -f ensure_dir
export -f in_venv
export -f file_exists
export -f dir_exists
export -f get_os
export -f is_macos
export -f is_linux
export -f get_python_version
export -f package_installed
export -f backup_file
export -f restore_file
export -f cleanup_backups
export -f get_file_hash
export -f port_in_use
export -f find_available_port
export -f check_memory
export -f check_disk
export -f get_git_branch
export -f git_is_clean
export -f check_resources
export -f cleanup_resources 