#!/bin/bash
set -e

# Function for logging with timestamps
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1"
}

# Function to handle errors
handle_error() {
    log "Error occurred in main.sh at line $1"
    exit 1
}

trap 'handle_error $LINENO' ERR

# Function to check script existence
check_script() {
    local script="$1"
    if [ ! -f "$script" ]; then
        log "ERROR: Required script not found: $script"
        exit 1
    fi
}

# Function to run script with error handling
run_script() {
    local script="$1"
    local description="$2"
    
    log "Starting: $description"
    
    if ! bash "$script"; then
        log "ERROR: Failed to execute $script"
        exit 1
    fi
    
    log "Completed: $description"
}

# Function to generate final report
generate_report() {
    log "Generating final report..."
    
    cat > final_report.md << EOL
# Project Verification and Fix Report
Generated: $(date)

## Actions Performed

1. Project Structure
   - Verified directory structure
   - Created missing directories
   - Set up Streamlit configuration

2. File Consolidation
   - Analyzed code similarity
   - Consolidated similar files
   - Organized by file type
   $([ -f "consolidation_report.txt" ] && echo "   See consolidation_report.txt for details")

3. Code Cleanup
   - Removed redundant files
   - Cleaned up unused code
   - Removed empty directories
   $([ -f "cleanup_report.txt" ] && echo "   See cleanup_report.txt for details")

4. Streamlit Organization
   - Organized pages and components
   - Fixed imports
   - Verified Streamlit setup

## Project Statistics

\`\`\`
Total Files: $(find . -type f | wc -l)
Python Files: $(find . -name "*.py" | wc -l)
Directories: $(find . -type d | wc -l)
\`\`\`

## Directory Structure

\`\`\`
$(tree src/)
\`\`\`

## Next Steps

1. Review the generated reports in:
   - consolidation_report.txt
   - cleanup_report.txt
   - final_report.md

2. Run tests to verify functionality:
   \`\`\`bash
   python -m pytest
   \`\`\`

3. Start the Streamlit application:
   \`\`\`bash
   cd src/dashboard && streamlit run Home.py
   \`\`\`
EOL

    log "Final report generated: final_report.md"
}

# Main execution
log "Starting project verification and fixes..."

# Check required scripts
required_scripts=(
    "scripts/project_structure.sh"
    "scripts/consolidate_files.sh"
    "scripts/cleanup.sh"
    "scripts/streamlit_fixes.sh"
)

for script in "${required_scripts[@]}"; do
    check_script "$script"
done

# Execute scripts in order
run_script "scripts/project_structure.sh" "Project Structure Verification"
run_script "scripts/consolidate_files.sh" "File Consolidation"
run_script "scripts/cleanup.sh" "Code Cleanup"
run_script "scripts/streamlit_fixes.sh" "Streamlit Organization"

# Generate final report
generate_report

log "All tasks completed successfully. See final_report.md for details."
