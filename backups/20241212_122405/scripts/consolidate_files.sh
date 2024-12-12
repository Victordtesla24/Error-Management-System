#!/bin/bash
set -e

# Function for logging with timestamps
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1"
}

# Function to handle errors
handle_error() {
    log "Error occurred in consolidate_files.sh at line $1"
    exit 1
}

trap 'handle_error $LINENO' ERR

# Function to verify required directories exist
verify_directories() {
    log "Verifying required directories..."
    
    required_dirs=(
        "src/dashboard/components"
        "src/dashboard/services"
        "src/dashboard/static/style"
        "src/dashboard/static/assets"
        "src/dashboard/static/src"
    )
    
    for dir in "${required_dirs[@]}"; do
        if [ ! -d "$dir" ]; then
            mkdir -p "$dir"
            log "Created directory: $dir"
        fi
    done
}

# Function to consolidate files using Python FileConsolidator
consolidate_files() {
    log "Consolidating files..."
    
    # First verify directories exist
    verify_directories
    
    # Create Python script using existing FileConsolidator
    cat > /tmp/run_consolidation.py << 'EOL'
import os
import sys
import logging
from pathlib import Path

# Add project root to Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.dashboard.utils.file_consolidator import FileConsolidator

def main():
    """Run file consolidation process."""
    try:
        # Initialize consolidator with current directory
        consolidator = FileConsolidator(Path('.'))
        
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s [%(levelname)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Run consolidation
        logging.info("Starting file consolidation process...")
        consolidator.run()
        
        # Report statistics
        logging.info("Consolidation Statistics:")
        logging.info(f"- Files processed: {len(consolidator.processed_files)}")
        logging.info(f"- Duplicate sets found: {len([files for files in consolidator.file_hashes.values() if len(files) > 1])}")
        
        # Generate report
        with open('consolidation_report.txt', 'w') as f:
            f.write("File Consolidation Report\n")
            f.write("=======================\n\n")
            
            f.write("Duplicate Files:\n")
            for hash_value, files in consolidator.file_hashes.items():
                if len(files) > 1:
                    f.write(f"\nDuplicate Group:\n")
                    for file in files:
                        f.write(f"  - {file}\n")
            
            f.write("\nProcessed Files:\n")
            for file in sorted(consolidator.processed_files):
                f.write(f"  - {file}\n")

    except Exception as e:
        logging.error(f"Error during consolidation: {e}", exc_info=True)
        sys.exit(1)

if __name__ == '__main__':
    main()
EOL

    # Run consolidation script
    python3 /tmp/run_consolidation.py
    rm /tmp/run_consolidation.py
    
    # Check if report was generated
    if [ -f "consolidation_report.txt" ]; then
        log "Consolidation report generated successfully"
        log "See consolidation_report.txt for details"
    else
        log "Warning: Consolidation report was not generated"
    fi
}

# Function to verify consolidated files
verify_consolidation() {
    log "Verifying consolidated files..."
    
    # Create verification script
    cat > /tmp/verify_consolidation.py << 'EOL'
import os
import sys
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def verify_consolidated_files():
    """Verify consolidated files are properly organized."""
    consolidated_patterns = [
        ('src/dashboard/components', '*_component.py'),
        ('src/dashboard/utils', '*_utils.py'),
        ('src/dashboard/services', '*_service.py'),
        ('src/dashboard/static/style', '*.css'),
        ('src/dashboard/static/assets', '*.{png,jpg,svg,gif}'),
        ('src/dashboard/static/src', '*.{ts,tsx,js,jsx}')
    ]
    
    issues = []
    
    for directory, pattern in consolidated_patterns:
        dir_path = Path(directory)
        if not dir_path.exists():
            issues.append(f"Directory not found: {directory}")
            continue
            
        consolidated_file = next(dir_path.glob('consolidated_*'), None)
        if not consolidated_file:
            issues.append(f"No consolidated file found in {directory}")
            continue
            
        # Check if any unconsolidated files remain
        unconsolidated = list(dir_path.glob(pattern))
        unconsolidated = [f for f in unconsolidated if 'consolidated_' not in str(f)]
        if unconsolidated:
            issues.append(f"Unconsolidated files found in {directory}:")
            for file in unconsolidated:
                issues.append(f"  - {file}")
    
    return issues

if __name__ == '__main__':
    issues = verify_consolidated_files()
    if issues:
        logger.warning("Consolidation verification found issues:")
        for issue in issues:
            logger.warning(issue)
        sys.exit(0)  # Don't fail on verification issues
    else:
        logger.info("Consolidation verification passed")
EOL

    # Run verification script
    python3 /tmp/verify_consolidation.py
    rm /tmp/verify_consolidation.py
}

# Execute
log "Starting file consolidation process..."
consolidate_files
verify_consolidation
log "File consolidation completed"
