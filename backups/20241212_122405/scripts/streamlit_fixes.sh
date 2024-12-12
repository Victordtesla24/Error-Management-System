#!/bin/bash
set -e

# Function for logging with timestamps
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1"
}

# Function to handle errors
handle_error() {
    log "Error occurred in streamlit_fixes.sh at line $1"
    exit 1
}

trap 'handle_error $LINENO' ERR

# Function to organize Streamlit files
organize_streamlit_files() {
    log "Organizing Streamlit files..."
    
    # Create Python script for Streamlit organization
    cat > /tmp/organize_streamlit.py << 'EOL'
import os
import shutil
import logging
from pathlib import Path
from typing import List, Dict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StreamlitOrganizer:
    def __init__(self, root_dir: str):
        self.root_dir = Path(root_dir)
        self.dashboard_dir = self.root_dir / 'src' / 'dashboard'
        
    def setup_directories(self) -> None:
        """Create Streamlit directory structure."""
        directories = [
            self.dashboard_dir,
            self.dashboard_dir / 'pages',
            self.dashboard_dir / 'components',
            self.dashboard_dir / 'utils',
            self.dashboard_dir / 'services',
            self.dashboard_dir / 'hooks',
            self.dashboard_dir / 'context',
            self.dashboard_dir / 'static' / 'style',
            self.dashboard_dir / 'static' / 'assets',
            self.dashboard_dir / 'static' / 'src'
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            (directory / '__init__.py').touch()
    
    def organize_pages(self) -> None:
        """Organize Streamlit pages."""
        # Move Home.py to dashboard root
        home_in_pages = self.dashboard_dir / 'pages' / 'Home.py'
        if home_in_pages.exists():
            shutil.move(str(home_in_pages), str(self.dashboard_dir / 'Home.py'))
        
        # Ensure all other pages are in pages directory
        for py_file in self.dashboard_dir.rglob('*.py'):
            if py_file.name[0].isupper() and py_file.name != 'Home.py':
                if py_file.parent != self.dashboard_dir / 'pages':
                    target = self.dashboard_dir / 'pages' / py_file.name
                    shutil.move(str(py_file), str(target))
    
    def organize_components(self) -> None:
        """Organize Streamlit components."""
        patterns = ['*_component.py', '*Component.py', '*Widget.py']
        for pattern in patterns:
            for file in self.dashboard_dir.rglob(pattern):
                if file.parent != self.dashboard_dir / 'components':
                    target = self.dashboard_dir / 'components' / file.name
                    shutil.move(str(file), str(target))
    
    def organize_static_files(self) -> None:
        """Organize static files."""
        static_patterns = {
            'style': ['*.css', '*.scss', '*.less'],
            'assets': ['*.png', '*.jpg', '*.jpeg', '*.gif', '*.svg', '*.ico'],
            'src': ['*.ts', '*.tsx', '*.js', '*.jsx']
        }
        
        for dir_name, patterns in static_patterns.items():
            target_dir = self.dashboard_dir / 'static' / dir_name
            for pattern in patterns:
                for file in self.dashboard_dir.rglob(pattern):
                    if file.parent != target_dir:
                        target = target_dir / file.name
                        shutil.move(str(file), str(target))
    
    def fix_imports(self) -> None:
        """Fix imports in Streamlit files."""
        for py_file in self.dashboard_dir.rglob('*.py'):
            try:
                with open(py_file, 'r') as f:
                    content = f.read()
                
                # Fix relative imports
                content = content.replace('from ..', 'from src')
                content = content.replace('from .', 'from src.dashboard')
                
                with open(py_file, 'w') as f:
                    f.write(content)
            except Exception as e:
                logger.error(f"Error fixing imports in {py_file}: {e}")
    
    def create_streamlit_config(self) -> None:
        """Create or update Streamlit config."""
        config_dir = self.root_dir / '.streamlit'
        config_dir.mkdir(exist_ok=True)
        
        config_file = config_dir / 'config.toml'
        if not config_file.exists():
            config_content = """
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
"""
            config_file.write_text(config_content)
    
    def verify_organization(self) -> List[str]:
        """Verify Streamlit organization."""
        issues = []
        
        # Check Home.py location
        if not (self.dashboard_dir / 'Home.py').exists():
            issues.append("Home.py not found in dashboard root")
        
        # Check page organization
        for py_file in self.dashboard_dir.rglob('*.py'):
            if py_file.name[0].isupper() and py_file.name != 'Home.py':
                if py_file.parent != self.dashboard_dir / 'pages':
                    issues.append(f"Page file {py_file.name} not in pages directory")
        
        # Check component organization
        component_patterns = ['*_component.py', '*Component.py', '*Widget.py']
        for pattern in component_patterns:
            for file in self.dashboard_dir.rglob(pattern):
                if file.parent != self.dashboard_dir / 'components':
                    issues.append(f"Component {file.name} not in components directory")
        
        return issues
    
    def run(self) -> None:
        """Run Streamlit organization process."""
        logger.info("Starting Streamlit organization...")
        
        self.setup_directories()
        self.organize_pages()
        self.organize_components()
        self.organize_static_files()
        self.fix_imports()
        self.create_streamlit_config()
        
        issues = self.verify_organization()
        if issues:
            logger.warning("Organization issues found:")
            for issue in issues:
                logger.warning(f"  - {issue}")
        else:
            logger.info("Streamlit organization completed successfully")

if __name__ == '__main__':
    organizer = StreamlitOrganizer('.')
    organizer.run()
EOL

    # Run Streamlit organization script
    python3 /tmp/organize_streamlit.py
    rm /tmp/organize_streamlit.py
}

# Function to verify Streamlit setup
verify_streamlit_setup() {
    log "Verifying Streamlit setup..."
    
    # Check if streamlit is installed
    if ! python3 -c "import streamlit" &> /dev/null; then
        log "Installing Streamlit..."
        pip install streamlit
    fi
    
    # Verify Streamlit can run
    if ! streamlit --version &> /dev/null; then
        log "ERROR: Streamlit installation verification failed"
        exit 1
    fi
    
    # Check required directories exist
    required_dirs=(
        "src/dashboard"
        "src/dashboard/pages"
        "src/dashboard/components"
        "src/dashboard/utils"
        "src/dashboard/static/style"
        "src/dashboard/static/assets"
        ".streamlit"
    )
    
    for dir in "${required_dirs[@]}"; do
        if [ ! -d "$dir" ]; then
            log "ERROR: Required directory missing: $dir"
            exit 1
        fi
    done
    
    # Check Home.py exists in correct location
    if [ ! -f "src/dashboard/Home.py" ]; then
        log "ERROR: Home.py not found in dashboard root"
        exit 1
    fi
    
    # Check Streamlit config exists
    if [ ! -f ".streamlit/config.toml" ]; then
        log "ERROR: Streamlit config missing"
        exit 1
    fi
    
    log "Streamlit setup verification completed"
}

# Execute
log "Starting Streamlit fixes..."
organize_streamlit_files
verify_streamlit_setup
log "Streamlit fixes completed"
