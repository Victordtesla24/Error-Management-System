#!/bin/bash

# Cleanup script for Error Management System
# Removes unnecessary files and consolidates codebase

# Set error handling
set -e
trap 'echo "Error on line $LINENO"' ERR

# Function to log messages
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

# Files and directories to keep
KEEP_FILES=(
    "src/"
    "tests/"
    "docs/"
    "scripts/start.sh"
    "scripts/cleanup.sh"
    "requirements.txt"
    "pytest.ini"
    "README.md"
    ".env"
    ".gitignore"
    "pyproject.toml"
    ".streamlit/"
)

# Function to check if file/directory should be kept
should_keep() {
    local path="$1"
    for keep in "${KEEP_FILES[@]}"; do
        if [[ "$path" == "$keep" ]] || [[ "$path" == "$keep"* ]]; then
            return 0
        fi
    done
    return 1
}

# Function to clean up backups
cleanup_backups() {
    log "Cleaning up backup files..."
    
    # Remove backup directories except the latest
    if [ -d "backups" ]; then
        cd backups
        # Keep only the latest backup
        ls -t | tail -n +2 | xargs rm -rf
        cd ..
    fi
    
    # Remove test backups
    rm -rf tests_backup/
}

# Function to clean up unnecessary files
cleanup_files() {
    log "Cleaning up unnecessary files..."
    
    # Remove Python cache files
    find . -type f -name "*.pyc" -delete
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
    
    # Remove temporary files
    find . -type f -name "*.tmp" -delete
    find . -type f -name "*.log" -not -path "./logs/*" -delete
    find . -type f -name "*.bak" -delete
    
    # Remove old reports
    find . -type f -name "*report*.txt" -delete
    
    # Remove duplicate configuration files
    find . -type f -name "*config*.yaml" -not -name "config.yaml" -delete
    
    # Remove old scripts
    cd scripts
    for file in *; do
        if [[ "$file" != "start.sh" ]] && [[ "$file" != "cleanup.sh" ]]; then
            rm -f "$file"
        fi
    done
    cd ..
    
    # Remove unnecessary directories
    rm -rf k8s/ kubernetes/ .vscode/ reports/
    
    # Remove Go files (not needed for Python/Streamlit app)
    rm -f go.mod main.go
    
    # Remove unnecessary build files
    rm -f Makefile setup.cfg setup.py
}

# Function to consolidate requirements
consolidate_requirements() {
    log "Consolidating requirements files..."
    
    # Combine all requirements into one file
    cat requirements*.txt | sort -u > requirements.tmp
    mv requirements.tmp requirements.txt
    rm -f requirements-*.txt
}

# Function to clean up Docker files
cleanup_docker() {
    log "Cleaning up Docker files..."
    
    # Keep only necessary Docker files
    rm -f Dockerfile.* docker-compose.*.yml
    
    # Clean up .devcontainer
    if [ -d ".devcontainer" ]; then
        cd .devcontainer
        rm -f devcontainer.*.json
        cd ..
    fi
}

# Function to verify Streamlit structure
verify_streamlit_structure() {
    log "Verifying Streamlit structure..."
    
    # Ensure proper Streamlit directory structure
    mkdir -p src/dashboard/pages
    mkdir -p src/dashboard/components
    mkdir -p src/dashboard/utils
    mkdir -p .streamlit
    
    # Create Streamlit config if it doesn't exist
    if [ ! -f ".streamlit/config.toml" ]; then
        cat > .streamlit/config.toml << EOL
[theme]
primaryColor="#F63366"
backgroundColor="#FFFFFF"
secondaryBackgroundColor="#F0F2F6"
textColor="#262730"
font="sans serif"

[server]
enableCORS=false
enableXsrfProtection=true

[browser]
gatherUsageStats=false
EOL
    fi
}

# Main execution
main() {
    log "Starting cleanup process..."
    
    # Create backup of current state
    log "Creating backup..."
    timestamp=$(date +%Y%m%d_%H%M%S)
    mkdir -p "backups/$timestamp"
    cp -r src tests docs scripts requirements.txt pytest.ini README.md .env "backups/$timestamp/"
    
    # Run cleanup functions
    cleanup_backups
    cleanup_files
    consolidate_requirements
    cleanup_docker
    verify_streamlit_structure
    
    # Set proper permissions
    find . -type d -exec chmod 755 {} \;
    find . -type f -exec chmod 644 {} \;
    chmod +x scripts/*.sh
    
    log "Cleanup complete!"
}

# Run main function
main
