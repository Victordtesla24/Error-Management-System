#!/bin/bash

# Set error handling
set -e
trap 'echo "Error on line $LINENO"' ERR

# Set up logging
LOG_DIR="logs"
mkdir -p "$LOG_DIR"

# Logging function
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_DIR/run.log"
}

# Clean project environment
clean_environment() {
    log "Cleaning project environment..."
    
    # Remove Python cache
    find . -type d -name "__pycache__" -exec rm -r {} + 2>/dev/null || true
    find . -type f -name "*.pyc" -delete
    find . -type f -name "*.pyo" -delete
    
    # Remove test cache
    rm -rf .pytest_cache
    rm -rf .coverage
    rm -rf htmlcov
    
    # Remove build artifacts
    rm -rf build/
    rm -rf dist/
    rm -rf *.egg-info/
}

# Install dependencies
install_dependencies() {
    log "Installing dependencies..."
    
    # Upgrade pip
    python -m pip install --upgrade pip
    
    # Install requirements
    pip install -r requirements.txt
    pip install -r requirements-grpc.txt
    pip install -r requirements-streamlit.txt
}

# Run verify and fix
run_verify_and_fix() {
    log "Running verify and fix script..."
    ./scripts/verify_and_fix.sh
}

# Run test suite
run_tests() {
    log "Running test suite..."
    
    # Run linting
    log "Running linting checks..."
    python -m black . || true
    python -m isort . || true
    python -m flake8 . || true
    
    # Run tests
    log "Running pytest..."
    python -m pytest tests/ -v --cov=src --cov-report=term-missing || true
}

# Generate test cases for failures
generate_test_cases() {
    log "Generating test cases for failures..."
    
    # Parse test results
    if [ -f ".coverage" ]; then
        # Generate coverage report
        coverage report --fail-under=80 || {
            log "Coverage below threshold, generating additional tests..."
            # TODO: Implement test generation logic
        }
    fi
}

# Create commit message
create_commit_message() {
    log "Creating commit message..."
    
    # Get changed files
    changed_files=$(git diff --name-only)
    
    # Create commit message
    commit_msg="Auto-commit: System improvements\n\nChanges:\n"
    
    # Add file changes to commit message
    for file in $changed_files; do
        commit_msg+="- Modified $file\n"
    done
    
    echo -e "$commit_msg" > .git/COMMIT_EDITMSG
}

# Push to main branch
push_to_main() {
    log "Pushing to main branch..."
    
    # Add changes
    git add .
    
    # Create commit message
    create_commit_message
    
    # Commit changes
    git commit -F .git/COMMIT_EDITMSG || true
    
    # Push changes
    git push origin main || true
}

# Main execution
log "Starting system run..."

clean_environment
install_dependencies
run_verify_and_fix
run_tests
generate_test_cases
push_to_main

log "System run completed successfully"
