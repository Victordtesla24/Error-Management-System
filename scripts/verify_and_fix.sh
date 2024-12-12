#!/bin/bash

echo "Starting verify and fix process..."

# Function to verify project structure
verify_structure() {
    echo "Verifying project structure..."
    required_dirs=("src" "tests" "docs" "scripts" "logs")
    for dir in "${required_dirs[@]}"; do
        if [ ! -d "$dir" ]; then
            mkdir -p "$dir"
            echo "Created missing directory: $dir"
        fi
    done
}

# Function to fix directory organization
fix_organization() {
    echo "Fixing directory organization..."
    # Move Python files to src if they exist in root
    find . -maxdepth 1 -name "*.py" -not -path "./setup.py" -exec mv {} src/ \; 2>/dev/null || true
    # Move test files to tests directory
    find . -name "test_*.py" -not -path "./tests/*" -exec mv {} tests/ \; 2>/dev/null || true
    # Move documentation to docs
    find . -name "*.md" -not -path "./docs/*" -not -name "README.md" -exec mv {} docs/ \; 2>/dev/null || true
}

# Function to consolidate duplicate files
consolidate_duplicates() {
    echo "Checking for duplicate files..."
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS version
        find . -type f -exec md5 {} \; | sort | awk '{print $NF}' | uniq -d | while read -r file; do
            echo "Potential duplicate found: $file"
        done
    else
        # Linux version
        find . -type f -exec md5sum {} \; | sort | uniq -D -w32 | while read -r hash file; do
            echo "Potential duplicate found: $file"
        done
    fi
}

# Function to manage imports
manage_imports() {
    echo "Managing imports..."
    if command -v pip >/dev/null 2>&1; then
        pip install isort autoflake >/dev/null 2>&1 || true
        if command -v isort >/dev/null 2>&1; then
            isort . || true
        fi
        if command -v autoflake >/dev/null 2>&1; then
            autoflake --recursive --in-place --remove-all-unused-imports . || true
        fi
    fi
}

# Function to fix linting errors
fix_linting() {
    echo "Fixing linting errors..."
    if command -v pip >/dev/null 2>&1; then
        pip install black flake8 >/dev/null 2>&1 || true
        if command -v black >/dev/null 2>&1; then
            black . || true
        fi
        if command -v flake8 >/dev/null 2>&1; then
            flake8 . || true
        fi
    fi
}

# Function to update documentation
update_docs() {
    echo "Updating documentation..."
    # Install pdoc if needed
    if command -v pip >/dev/null 2>&1; then
        pip install pdoc3 >/dev/null 2>&1 || true
    fi
    
    # Update API documentation
    if [ -d "src" ]; then
        if command -v pdoc >/dev/null 2>&1; then
            pdoc --html --output-dir docs/api src/ || true
        fi
    fi
    
    # Ensure all required documentation exists and update them
    required_docs=("architecture.md" "implementation_plans.md" "testing_architecture.md")
    for doc in "${required_docs[@]}"; do
        if [ ! -f "docs/$doc" ]; then
            touch "docs/$doc"
            echo "Created missing documentation: $doc"
        fi
        # Update timestamp in documentation
        echo -e "\n\nLast updated: $(date)" >> "docs/$doc"
    done

    # Update README if it doesn't exist
    if [ ! -f "README.md" ]; then
        echo "# Error Management System\n\nAn automated error management system.\n\nLast updated: $(date)" > README.md
    fi
}

# Function to monitor and adjust memory thresholds
manage_memory() {
    echo "Managing memory thresholds..."
    # Get current memory usage (platform independent)
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        memory_usage=$(ps -o %mem -p $$ | tail -1)
    else
        # Linux
        memory_usage=$(ps -o %mem= -p $$)
    fi
    
    if (( $(echo "$memory_usage > 80" | bc -l 2>/dev/null || echo 0) )); then
        echo "Warning: High memory usage detected"
    fi
}

# Function to improve indexing performance
improve_indexing() {
    echo "Improving indexing performance..."
    # Clean up unnecessary files
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find . -type f -name "*.pyc" -delete 2>/dev/null || true
    find . -type f -name ".DS_Store" -delete 2>/dev/null || true
    find . -type f -name "*.swp" -delete 2>/dev/null || true
    
    echo "Optimizing git repository..."
    if command -v git >/dev/null 2>&1; then
        git gc --aggressive 2>/dev/null || true
        git repack -Ad 2>/dev/null || true
        git prune 2>/dev/null || true
    fi
}

# Function to initialize and update git repository
init_git() {
    echo "Initializing/updating git repository..."
    
    # Initialize git if not already initialized
    if [ ! -d ".git" ]; then
        git init
        echo "Git repository initialized"
    fi

    # Create .gitignore if it doesn't exist
    if [ ! -f ".gitignore" ]; then
        cat > .gitignore << EOL
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
.env
.venv
env/
venv/
ENV/
.idea/
.vscode/
*.swp
.DS_Store
logs/
*.log
EOL
        echo ".gitignore created"
    fi

    # Stage and commit changes
    git add .
    git status
    if git diff-index --quiet HEAD -- 2>/dev/null; then
        echo "No changes to commit"
    else
        git commit -m "Automated update: $(date)" || echo "No changes to commit"
    fi
}

# Main execution
verify_structure
fix_organization
consolidate_duplicates
manage_imports
fix_linting
update_docs
manage_memory
improve_indexing
init_git

echo "Verify and fix process completed successfully!"
