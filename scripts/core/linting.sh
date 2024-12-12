#!/bin/bash

# Error Management System - Linting
# Handles code quality checks and fixes

# Source utility functions
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/utils.sh"

# Constants
readonly EXCLUDE_DIRS="venv/|\.git/|\.pytest_cache/|__pycache__/|\.mypy_cache/|\.coverage/|htmlcov/"
readonly MAX_FILES=100  # Maximum number of files to process at once

# Function to fix linting errors
fix_linting_errors() {
    log "Fixing linting errors..."
    
    # Install required packages one by one
    if ! in_venv; then
        log "ERROR: Must be run inside virtual environment"
        return 1
    fi
    
    # Fix imports with isort (Python files only)
    log "Running isort..."
    if command_exists isort; then
        isort . --skip-glob="*/$EXCLUDE_DIRS/*" --profile black --line-length 88 --multi-line 3 --trailing-comma || log "WARNING: isort failed"
    else
        log "WARNING: isort not found, skipping"
    fi
    
    # Remove unused imports and variables (Python files only)
    log "Running autoflake..."
    if command_exists autoflake; then
        find . -name "*.py" -not -regex ".*/$EXCLUDE_DIRS.*" -type f -print0 | xargs -0 -n "$MAX_FILES" autoflake --in-place --remove-all-unused-imports --remove-unused-variables || log "WARNING: autoflake failed"
    else
        log "WARNING: autoflake not found, skipping"
    fi
    
    # Format code with black (Python files only)
    log "Running black..."
    if command_exists black; then
        black . --exclude "$EXCLUDE_DIRS" --line-length 88 --target-version py311 || log "WARNING: black failed"
    else
        log "WARNING: black not found, skipping"
    fi
    
    # Run flake8 (Python files only)
    log "Running flake8..."
    if command_exists flake8; then
        flake8 . --exclude="$EXCLUDE_DIRS" --max-line-length 88 --extend-ignore=E203,W503 --statistics || log "WARNING: flake8 found issues"
    else
        log "WARNING: flake8 not found, skipping"
    fi
    
    # Run pylint
    log "Running pylint..."
    if command_exists pylint; then
        find . -name "*.py" -not -regex ".*/$EXCLUDE_DIRS.*" -type f -print0 | xargs -0 -n "$MAX_FILES" pylint || log "WARNING: pylint found issues"
    else
        log "WARNING: pylint not found, skipping"
    fi
}

# Function to check Python syntax
check_syntax() {
    log "Checking Python syntax..."
    
    local error_count=0
    local python_files
    
    # Find Python files excluding virtual environment and other generated directories
    python_files=$(find . -name "*.py" -not -regex ".*/$EXCLUDE_DIRS.*" -type f)
    
    for file in $python_files; do
        if ! python3 -m py_compile "$file" 2>/dev/null; then
            log "ERROR: Syntax error in $file"
            python3 -m py_compile "$file" 2>> "$ERROR_LOG"
            ((error_count++))
        fi
    done
    
    if [ "$error_count" -gt 0 ]; then
        log "Found $error_count files with syntax errors"
        return 1
    fi
    
    log "No syntax errors found"
    return 0
}

# Function to check code complexity
check_complexity() {
    log "Checking code complexity..."
    
    # Check if radon is installed
    if ! package_installed radon; then
        log "WARNING: radon not found, skipping complexity checks"
        return 0
    fi
    
    # Check cyclomatic complexity
    log "Running complexity analysis..."
    radon cc . --exclude "$EXCLUDE_DIRS" --min B --show-complexity --total-average || log "WARNING: complexity issues found"
    
    # Check maintainability index
    log "Running maintainability analysis..."
    radon mi . --exclude "$EXCLUDE_DIRS" --min B --show || log "WARNING: maintainability issues found"
}

# Function to generate linting report
generate_report() {
    log "Generating linting report..."
    
    local report_file="logs/linting_report.md"
    ensure_dir "$(dirname "$report_file")"
    
    {
        echo "# Code Quality Report"
        echo "Generated on: $(date '+%Y-%m-%d %H:%M:%S')"
        echo
        echo "## Summary"
        echo "- Files analyzed: $(find . -name "*.py" -not -regex ".*/$EXCLUDE_DIRS.*" -type f | wc -l)"
        echo "- Lines of code: $(find . -name "*.py" -not -regex ".*/$EXCLUDE_DIRS.*" -type f -exec cat {} \; | wc -l)"
        echo
        echo "## Issues Found"
        echo "### Flake8"
        flake8 . --exclude="$EXCLUDE_DIRS" --max-line-length 88 --extend-ignore=E203,W503 --statistics 2>/dev/null || true
        echo
        echo "### Pylint"
        find . -name "*.py" -not -regex ".*/$EXCLUDE_DIRS.*" -type f -print0 | xargs -0 -n "$MAX_FILES" pylint --reports=yes 2>/dev/null || true
        echo
        echo "### Security Issues"
        bandit -r . -x "$EXCLUDE_DIRS" -f txt 2>/dev/null || true
    } > "$report_file"
    
    log "Report generated: $report_file"
}

# Main execution
main() {
    # Ensure we're in a virtual environment
    if ! in_venv; then
        log "ERROR: Must be run inside virtual environment"
        exit 1
    fi
    
    # Ensure log directory exists
    ensure_dir "logs"
    
    # Run all checks
    check_syntax
    fix_linting_errors
    check_complexity
    generate_report
}

# Run main function
main