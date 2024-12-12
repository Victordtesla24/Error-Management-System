#!/bin/bash

# Error Management System - Project Setup Script
# Initializes project structure and dependencies

set -e
trap 'echo "Error on line $LINENO"' ERR

# Constants
VENV_DIR="venv"
PYTHON_VERSION="3.9"

# Function to check Python version
check_python() {
    echo "Checking Python version..."
    if ! command -v python3 >/dev/null; then
        echo "Python 3 not found. Please install Python $PYTHON_VERSION or later."
        exit 1
    fi
}

# Function to create project structure
create_structure() {
    echo "Creating project structure..."
    
    # Create main directories
    mkdir -p src/{core,analysis,dashboard,utils}
    mkdir -p src/dashboard/pages
    mkdir -p src/dashboard/components
    mkdir -p tests/{unit,integration}
    mkdir -p docs/{api,user,implementation}
    mkdir -p scripts
    mkdir -p logs
    mkdir -p .streamlit
    
    # Create necessary files
    touch README.md
    touch requirements.txt
    touch .env
    touch .gitignore
    touch pytest.ini
    touch setup.py
}

# Function to setup Streamlit configuration
setup_streamlit() {
    echo "Setting up Streamlit configuration..."
    
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
maxUploadSize=200

[browser]
gatherUsageStats=false

[logger]
level="info"
EOL
}

# Function to setup virtual environment
setup_venv() {
    echo "Setting up virtual environment..."
    
    # Create virtual environment
    python3 -m venv "$VENV_DIR"
    source "$VENV_DIR/bin/activate"
    
    # Upgrade pip
    pip install --upgrade pip
    
    # Install core dependencies
    pip install streamlit pandas numpy plotly python-dotenv pytest black flake8 isort
}

# Function to setup git
setup_git() {
    echo "Setting up git repository..."
    
    # Initialize git if not already initialized
    if [ ! -d ".git" ]; then
        git init
        git branch -M main
    fi
    
    # Create .gitignore
    cat > .gitignore << EOL
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environment
venv/
env/
ENV/

# IDE
.idea/
.vscode/
*.swp
*.swo
.DS_Store

# Streamlit
.streamlit/secrets.toml

# Testing
.coverage
htmlcov/
.pytest_cache/
.tox/

# Logs
*.log
logs/

# Environment variables
.env
.env.local

# Distribution
dist/
build/
EOL
    
    # Initial commit
    git add .
    git commit -m "Initial project setup"
}

# Function to create documentation
create_docs() {
    echo "Creating documentation..."
    
    # Create README
    cat > README.md << EOL
# Error Management System

A comprehensive error detection and management system built with Streamlit.

## Features
- Automated error detection
- Real-time monitoring
- Intelligent error analysis
- Interactive dashboard

## Setup
1. Run \`./scripts/project_setup.sh\` to initialize the project
2. Configure environment variables in \`.env\`
3. Run \`./scripts/run.sh\` to start the system

## Documentation
- User Guide: \`docs/user/\`
- API Documentation: \`docs/api/\`
- Implementation Details: \`docs/implementation/\`

## Development
- Python $PYTHON_VERSION+
- Streamlit
- Pytest for testing
EOL
    
    # Create basic documentation files
    touch docs/api/README.md
    touch docs/user/guide.md
    touch docs/implementation/architecture.md
}

# Main execution
main() {
    echo "Starting project setup..."
    
    check_python
    create_structure
    setup_streamlit
    setup_venv
    setup_git
    create_docs
    
    echo "Project setup complete!"
    echo "Next steps:"
    echo "1. Configure your environment variables in .env"
    echo "2. Run './scripts/run.sh' to start the system"
}

# Run main function
main 