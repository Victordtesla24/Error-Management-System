#!/bin/bash
set -e

# Function for logging with timestamps
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1"
}

# Function to handle errors
handle_error() {
    log "Error occurred in project_structure.sh at line $1"
    exit 1
}

trap 'handle_error $LINENO' ERR

# Function to verify project structure
verify_project_structure() {
    log "Verifying project structure..."
    
    # Create required directories
    directories=(
        "src/dashboard/pages"
        "src/dashboard/components"
        "src/dashboard/utils"
        "src/dashboard/static/style"
        "src/dashboard/static/assets"
        "src/dashboard/static/src"
        "src/dashboard/services"
        "src/dashboard/hooks"
        "src/dashboard/context"
        "src/dashboard/types"
        "src/dashboard/constants"
        "src/error_management"
        "src/agent"
        "src/security"
        "src/file_monitor"
        "docs/api"
        "docs/user_guide"
        "docs/developer_guide"
        "config"
        ".streamlit"
    )
    
    for dir in "${directories[@]}"; do
        if [ ! -d "$dir" ]; then
            log "Creating missing directory: $dir"
            mkdir -p "$dir"
        fi
    done

    # Create Streamlit config
    if [ ! -f ".streamlit/config.toml" ]; then
        log "Creating Streamlit config..."
        mkdir -p .streamlit
        cat > .streamlit/config.toml << EOL
[theme]
primaryColor = "#007bff"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f8f9fa"
textColor = "#212529"

[server]
port = 8501
address = "0.0.0.0"
enableCORS = false
enableXsrfProtection = true
maxUploadSize = 200
maxMessageSize = 200

[browser]
gatherUsageStats = false
serverAddress = "localhost"
serverPort = 8501

[logger]
level = "info"
messageFormat = "%(asctime)s %(levelname)s: %(message)s"

[runner]
magicEnabled = true
installTracer = false
fixMatplotlib = true

[client]
showErrorDetails = true
toolbarMode = "auto"
EOL
    fi
}

# Execute
log "Starting project structure verification..."
verify_project_structure
log "Project structure verification completed"
