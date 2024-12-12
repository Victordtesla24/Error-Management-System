#!/bin/bash
set -e

# Function for logging with timestamps
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1"
}

# Function to handle errors
handle_error() {
    log "Error occurred in update_documents.sh at line $1"
    exit 1
}

trap 'handle_error $LINENO' ERR

# Function to backup a file before updating
backup_file() {
    local file=$1
    if [ -f "$file" ]; then
        cp "$file" "${file}.bak"
    fi
}

# Function to restore from backup if update fails
restore_from_backup() {
    local file=$1
    if [ -f "${file}.bak" ]; then
        mv "${file}.bak" "$file"
    fi
}

# Function to cleanup backups
cleanup_backups() {
    find . -name "*.bak" -type f -delete
}

# Function to update architecture.md
update_architecture() {
    log "Updating architecture.md..."
    backup_file "docs/architecture.md"
    
    # Preserve existing content
    local existing_content=""
    if [ -f "docs/architecture.md" ]; then
        existing_content=$(cat "docs/architecture.md")
    fi
    
    # Generate new content while preserving existing
    {
        echo "# System Architecture"
        echo
        echo "## Directory Structure"
        echo "\`\`\`"
        tree -L 3 --dirsfirst --gitignore src/
        echo "\`\`\`"
        echo
        echo "## Components"
        echo
        # Extract component information from Python files
        find src/ -name "*.py" -type f -exec grep -l "^class" {} \; | while read -r file; do
            echo "### $(basename "$file" .py)"
            grep "^class" "$file" | sed 's/class /- /'
        done
        
        # Preserve existing sections that don't conflict
        echo "$existing_content" | grep -v "^# System Architecture" || true
    } > "docs/architecture.md.tmp"
    
    mv "docs/architecture.md.tmp" "docs/architecture.md"
}

# Function to update implementation_plans.md
update_implementation_plans() {
    log "Updating implementation_plans.md..."
    backup_file "docs/implementation_plans.md"
    
    # Preserve existing content
    local existing_content=""
    if [ -f "docs/implementation_plans.md" ]; then
        existing_content=$(cat "docs/implementation_plans.md")
    fi
    
    {
        echo "# Implementation Plans"
        echo
        echo "## Current Implementation Status"
        echo
        echo "### Completed Features"
        find src/ -type f -name "*.py" -o -name "*.tsx" -o -name "*.ts" | sort | while read -r file; do
            echo "- ${file#src/}"
        done
        echo
        echo "### In Progress"
        git ls-files --others --exclude-standard | grep -E "\.py$|\.tsx?$" | sort | while read -r file; do
            echo "- $file"
        done
        echo
        # Preserve existing sections that don't conflict
        echo "$existing_content" | grep -v "^# Implementation Plans" || true
    } > "docs/implementation_plans.md.tmp"
    
    mv "docs/implementation_plans.md.tmp" "docs/implementation_plans.md"
}

# Function to update testing_architecture.md
update_testing_architecture() {
    log "Updating testing_architecture.md..."
    backup_file "docs/testing_architecture.md"
    
    # Preserve existing content
    local existing_content=""
    if [ -f "docs/testing_architecture.md" ]; then
        existing_content=$(cat "docs/testing_architecture.md")
    fi
    
    {
        echo "# Testing Architecture"
        echo
        echo "## Current Test Coverage"
        echo
        echo "### Test Files"
        find tests/ -name "test_*.py" | sort | while read -r file; do
            echo "- $file"
        done
        echo
        echo "### Coverage Report"
        if command -v pytest >/dev/null 2>&1; then
            pytest --cov=src --cov-report=term-missing 2>/dev/null || true
        fi
        echo
        # Preserve existing sections that don't conflict
        echo "$existing_content" | grep -v "^# Testing Architecture" || true
    } > "docs/testing_architecture.md.tmp"
    
    mv "docs/testing_architecture.md.tmp" "docs/testing_architecture.md"
}

# Function to update development_plan.md
update_development_plan() {
    log "Updating development_plan.md..."
    backup_file "development_plan.md"
    
    # Preserve existing content
    local existing_content=""
    if [ -f "development_plan.md" ]; then
        existing_content=$(cat "development_plan.md")
    fi
    
    {
        echo "# Development Plan"
        echo
        echo "## Current Status"
        echo
        echo "### Implemented Features"
        find src/ -type f -name "*.py" -o -name "*.tsx" -o -name "*.ts" | sort | while read -r file; do
            echo "- ${file#src/}"
        done
        echo
        echo "### Pending Features"
        # Extract TODOs from code
        echo "TODOs found in code:"
        find src/ -type f -name "*.py" -o -name "*.tsx" -o -name "*.ts" -exec grep -l "TODO:" {} \; | while read -r file; do
            echo "#### ${file#src/}"
            grep -h "TODO:" "$file" | sed 's/[[:space:]]*#[[:space:]]*TODO:[[:space:]]*/- /'
        done
        echo
        # Preserve existing sections that don't conflict
        echo "$existing_content" | grep -v "^# Development Plan" || true
    } > "development_plan.md.tmp"
    
    mv "development_plan.md.tmp" "development_plan.md"
}

# Main execution
log "Starting document updates..."

# Create docs directory if it doesn't exist
mkdir -p docs

# Update all documents
update_architecture
update_implementation_plans
update_testing_architecture
update_development_plan

# Cleanup backups
cleanup_backups

log "Document updates completed successfully" 