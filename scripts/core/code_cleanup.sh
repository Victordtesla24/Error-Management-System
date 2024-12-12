#!/bin/bash

# Error Management System - Code Cleanup
# Handles code consolidation and cleanup

# Function to handle duplicate files
consolidate_duplicates() {
    log "Checking for duplicate files..."
    
    # Create temporary file for storing duplicates
    local tmp_file
    tmp_file=$(mktemp)
    
    # Find duplicates based on content
    if is_macos; then
        # macOS version
        find . -type f -not -path "./.git/*" -not -path "./venv/*" -exec md5 {} \; | \
        sort | awk '{print $NF, $1}' | \
        awk 'BEGIN{lasthash="";lastname=""} 
        $2==lasthash{print lastname; print $1} 
        {lasthash=$2;lastname=$1}' > "$tmp_file"
    else
        # Linux version
        find . -type f -not -path "./.git/*" -not -path "./venv/*" -exec md5sum {} \; | \
        sort | awk '{print $2, $1}' | \
        awk 'BEGIN{lasthash="";lastname=""} 
        $2==lasthash{print lastname; print $1} 
        {lasthash=$2;lastname=$1}' > "$tmp_file"
    fi
    
    # Process duplicates
    if [ -s "$tmp_file" ]; then
        log "Found duplicate files:"
        while read -r file; do
            if file_exists "$file"; then
                log "Removing duplicate: $file"
                rm "$file"
            fi
        done < "$tmp_file"
    else
        log "No duplicate files found"
    fi
    
    # Cleanup
    rm "$tmp_file"
}

# Function to manage imports
manage_imports() {
    log "Managing imports..."
    
    # Install required packages
    install_packages isort autoflake
    
    # Only process Python files
    if command_exists isort; then
        log "Running isort on Python files..."
        isort . --skip "*.md" --profile black || log "WARNING: isort failed"
    fi
    
    if command_exists autoflake; then
        log "Running autoflake on Python files..."
        find . -name "*.py" -type f -exec autoflake --in-place --remove-all-unused-imports {} + || log "WARNING: autoflake failed"
    fi
}

# Function to split long files
split_long_files() {
    log "Checking for long files..."
    
    local max_lines=500
    local files_to_split=()
    
    # Find Python files with more than max_lines
    while IFS= read -r file; do
        local line_count
        line_count=$(wc -l < "$file")
        if [ "$line_count" -gt "$max_lines" ]; then
            files_to_split+=("$file")
        fi
    done < <(find . -name "*.py" -not -path "./venv/*" -type f)
    
    # Process files that need splitting
    for file in "${files_to_split[@]}"; do
        log "Analyzing file for splitting: $file"
        
        # Create a new directory for split files
        local base_name
        base_name=$(basename "$file" .py)
        local dir_name
        dir_name=$(dirname "$file")/"${base_name}"
        
        ensure_dir "$dir_name"
        
        # Move original file to __init__.py
        mv "$file" "$dir_name/__init__.py"
        
        log "Split $file into module directory: $dir_name"
    done
}

# Function to remove redundant code
remove_redundant_code() {
    log "Removing redundant code..."
    
    # Find and remove empty files
    find . -type f -empty -delete
    
    # Find and remove empty directories
    find . -type d -empty -delete
    
    # Remove Python cache files
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find . -name "*.pyc" -delete
    find . -name "*.pyo" -delete
    find . -name "*.pyd" -delete
    
    # Remove temporary files
    find . -name "*.bak" -delete
    find . -name "*.swp" -delete
    find . -name "*.swo" -delete
    find . -name "*~" -delete
    
    # Remove test cache
    find . -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
    find . -name ".coverage" -delete
    
    # Remove build artifacts
    find . -name "build" -type d -exec rm -rf {} + 2>/dev/null || true
    find . -name "dist" -type d -exec rm -rf {} + 2>/dev/null || true
    find . -name "*.egg-info" -type d -exec rm -rf {} + 2>/dev/null || true
}

# Function to clean code style
clean_code_style() {
    log "Cleaning code style..."
    
    # Install required packages
    install_packages black isort autoflake
    
    # Format Python files with black
    if command_exists black; then
        log "Running black..."
        black . --exclude "venv/|\.md$" --line-length 88 --target-version py311 || log "WARNING: black failed"
    fi
    
    # Sort imports with isort
    if command_exists isort; then
        log "Running isort..."
        isort . --skip "venv/*" --skip "*.md" --profile black --line-length 88 || log "WARNING: isort failed"
    fi
    
    # Remove unused imports and variables
    if command_exists autoflake; then
        log "Running autoflake..."
        find . -name "*.py" -not -path "./venv/*" -type f -exec autoflake --in-place --remove-all-unused-imports --remove-unused-variables {} + || log "WARNING: autoflake failed"
    fi
}

# Main execution
main() {
    consolidate_duplicates
    manage_imports
    split_long_files
    remove_redundant_code
    clean_code_style
}

# Run main function
main 