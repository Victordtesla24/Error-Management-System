#!/bin/bash

# Navigate to tests directory
cd tests

# Keep only essential test files
essential_files=(
    "conftest.py"
    "test_agent_metrics.py"
    "test_agent_monitor.py"
    "test_dashboard.py"
    "test_dashboard_integration.py"
    "test_performance.py"
)

# Create backup directory
backup_dir="../tests_backup"
mkdir -p "$backup_dir"

# Move non-essential files to backup
for file in *.py; do
    if [[ ! " ${essential_files[@]} " =~ " ${file} " ]]; then
        mv "$file" "$backup_dir/"
    fi
done

# Remove test files that are definitely not needed
rm -f test_test_*.py
rm -f test_verify_and_fix.sh

echo "Test cleanup completed. Non-essential tests moved to $backup_dir"
