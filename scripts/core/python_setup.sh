#!/bin/bash

# Error Management System - Python Setup
# Handles Python version management and virtual environment setup

# Function to check Python version
check_python() {
    log "Checking Python version..."
    
    # Check if homebrew is installed
    if ! command_exists brew; then
        log "ERROR: Homebrew not found. Please install Homebrew first:"
        log "  /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
        exit 1
    fi
    
    # Install Python 3.11 via homebrew if not present
    if ! command_exists python3.11; then
        log "Installing Python 3.11 via homebrew..."
        brew install python@3.11
    fi
    
    # Set Python command
    export PYTHON_CMD="python3.11"
    
    # Verify Python version
    local version
    version=$($PYTHON_CMD -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
    log "Python version $version is compatible"
}

# Function to setup virtual environment
setup_venv() {
    log "Setting up virtual environment..."
    
    # Remove existing venv
    if dir_exists "$VENV_DIR"; then
        log "Removing existing virtual environment..."
        rm -rf "$VENV_DIR"
    fi
    
    # Create new venv with Python 3.11
    log "Creating new virtual environment..."
    python3.11 -m venv "$VENV_DIR"
    
    # Activate venv
    if ! source "${VENV_DIR}/bin/activate"; then
        log "ERROR: Failed to activate virtual environment"
        exit 1
    fi
    
    # Install base packages using pip
    log "Installing base packages..."
    pip install --upgrade pip setuptools wheel
}

# Function to install Python packages
install_packages() {
    local packages=("$@")
    log "Installing required packages: ${packages[*]}"
    
    # Ensure we're in venv
    if ! in_venv; then
        setup_venv
    fi
    
    # Install packages using homebrew's pip
    for package in "${packages[@]}"; do
        log "Installing $package..."
        if ! /opt/homebrew/bin/pip3.11 install "$package"; then
            log "WARNING: Failed to install $package"
        fi
    done
}

# Function to verify Python packages
verify_packages() {
    log "Verifying Python packages..."
    
    local required_packages=(
        "streamlit"
        "pandas"
        "numpy"
        "plotly"
        "python-dotenv"
        "gitpython"
        "watchdog"
        "black"
        "flake8"
        "isort"
        "pytest"
        "pytest-cov"
    )
    
    for package in "${required_packages[@]}"; do
        if ! package_installed "$package"; then
            log "Installing missing package: $package"
            install_packages "$package"
        fi
    done
}

# Main execution
main() {
    check_python
    setup_venv
    verify_packages
}

# Run main function
main 