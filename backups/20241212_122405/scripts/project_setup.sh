#!/bin/bash

# Set error handling
set -e
trap 'echo "Error on line $LINENO"' ERR

# Set up logging
LOG_DIR="logs"
mkdir -p "$LOG_DIR"

# Logging function
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_DIR/setup.log"
}

# Initialize project structure
log "Initializing project structure..."
mkdir -p src/{error_management,dashboard/{metrics,monitoring},agent} \
         tests \
         docs \
         logs \
         backups \
         reports

# Create documentation files
log "Creating documentation files..."
cat > docs/architecture.md << EOL
# System Architecture

## Components
1. Error Management System
2. Agent Monitor
3. Dashboard Integration
4. Testing Infrastructure

## Design Patterns
- Factory Pattern for error handlers
- Observer Pattern for monitoring
- Strategy Pattern for error resolution
EOL

cat > docs/implementation_plans.md << EOL
# Implementation Plans

## Phase 1: Core Infrastructure
- Error Management System
- Basic Monitoring
- Initial Tests

## Phase 2: Advanced Features
- Dashboard Integration
- Advanced Error Resolution
- Performance Optimization
EOL

cat > docs/testing_architecture.md << EOL
# Testing Architecture

## Test Levels
1. Unit Tests
2. Integration Tests
3. System Tests
4. Performance Tests

## Test Coverage Goals
- Line Coverage: 90%
- Branch Coverage: 85%
- Function Coverage: 95%
EOL

# Setup automated error handling
log "Setting up error handling..."
cat > src/error_management/__init__.py << EOL
from .error_manager import ErrorManager
from .error_report import ErrorReport
from .models import ErrorTask

__all__ = ['ErrorManager', 'ErrorReport', 'ErrorTask']
EOL

# Generate requirements.txt if not exists
log "Updating requirements.txt..."
cat > requirements.txt << EOL
pytest>=7.4.3
pytest-cov>=4.1.0
pytest-asyncio>=0.21.1
black>=23.11.0
isort>=5.12.0
flake8>=6.1.0
sentry-sdk>=1.35.0
structlog>=23.2.0
streamlit>=1.29.0
grpcio>=1.59.3
protobuf>=4.25.1
pyyaml>=6.0.1
EOL

# Create pyproject.toml
log "Creating pyproject.toml..."
cat > pyproject.toml << EOL
[tool.black]
line-length = 88
target-version = ['py311']
include = '\.pyi?$'

[tool.isort]
profile = "black"
multi_line_output = 3
include_trailing_comma = true
force_grid_wrap = 0
use_parentheses = true
ensure_newline_before_comments = true
line_length = 88

[tool.pytest.ini_options]
minversion = "6.0"
addopts = "-ra -q --cov=src --cov-report=term-missing"
testpaths = ["tests"]
EOL

# Setup test infrastructure
log "Setting up test infrastructure..."
cat > pytest.ini << EOL
[pytest]
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --cov=src --cov-report=term-missing
testpaths = tests
markers =
    slow: marks tests as slow
    integration: marks tests as integration tests
    performance: marks tests as performance tests
EOL

# Initialize git repository if not already initialized
if [ ! -d ".git" ]; then
    log "Initializing git repository..."
    git init
    git add .
    git commit -m "Initial project setup"
fi

# Make scripts executable
log "Making scripts executable..."
chmod +x scripts/*.sh

log "Project setup completed successfully"
