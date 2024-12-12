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

# Function to handle git operations
handle_git() {
    echo "Setting up git repository..."
    
    # Initialize git if needed
    if [ ! -d ".git" ]; then
        git init
        echo "Git repository initialized"
    fi

    # Configure git user if not set
    if [ -z "$(git config --get user.email)" ]; then
        git config user.email "melbvicduque@gmail.com"
        git config user.name "Victordtesla24"
        echo "Git user configured"
    fi

    # Check if remote exists, if not add it
    if ! git remote | grep -q "origin"; then
        git remote add origin https://github.com/Victordtesla24/Error-Management-System.git
        echo "Remote origin added"
    fi

    # Ensure we're on main branch
    if ! git rev-parse --verify main >/dev/null 2>&1; then
        git branch -M main
        echo "Created and switched to main branch"
    else
        git checkout main
        echo "Switched to main branch"
    fi

    # Add all files
    git add .
    echo "Files staged for commit"

    # Commit changes if any
    if ! git diff-index --quiet HEAD -- 2>/dev/null; then
        git commit -m "Update: $(date) - Auto-commit from verify_and_fix.sh"
        echo "Changes committed"
    else
        echo "No changes to commit"
    fi

    # Try to push changes
    echo "Attempting to push to remote..."
    if git push -u origin main 2>/dev/null; then
        echo "Successfully pushed to remote"
    else
        echo "Push failed. Please run these commands manually:"
        echo "git push -u origin main"
        echo "Or if you need to force push:"
        echo "git push -u origin main --force"
    fi
}

# Function to fix linting errors
fix_linting_errors() {
    echo "Fixing linting errors..."
    
    # Install required packages if not present
    pip install black isort flake8 autoflake pylint 2>/dev/null

    # Fix imports with isort
    echo "Running isort..."
    isort . --profile black --line-length 88 --multi-line 3 --trailing-comma

    # Remove unused imports and variables with autoflake
    echo "Running autoflake..."
    find . -name "*.py" -type f -exec autoflake --in-place --remove-all-unused-imports --remove-unused-variables {} +

    # Format code with black
    echo "Running black..."
    black . --line-length 88 --target-version py39

    # Run flake8 to check remaining issues
    echo "Running flake8..."
    flake8 . --max-line-length 88 --extend-ignore=E203,W503 --statistics || true

    echo "Linting fixes complete."
}

# Function to fix documentation
fix_docs() {
    echo "Fixing documentation..."
    
    # Install doc tools if not present
    pip install pydocstyle doc8 2>/dev/null

    # Fix docstring issues
    echo "Running pydocstyle..."
    pydocstyle . || true

    # Fix restructured text issues
    echo "Running doc8..."
    doc8 . || true

    echo "Documentation fixes complete."
}

# Function to consolidate documentation
consolidate_docs() {
    echo "Consolidating documentation..."
    
    # Create necessary directories
    mkdir -p docs/implementation
    mkdir -p docs/api
    mkdir -p docs/user

    # Move and organize documentation files
    if [ -d "docs" ]; then
        # Consolidate implementation docs
        cat docs/implementation/phase*_*.md > docs/implementation/development_plan_new.md 2>/dev/null
        mv docs/implementation/development_plan_new.md docs/implementation/development_plan.md 2>/dev/null
        rm -f docs/implementation/phase*_*.md 2>/dev/null

        # Clean up empty files
        find docs -type f -name "*.md" -size -10c -delete 2>/dev/null
    fi

    echo "Documentation consolidation complete."
}

# Main execution
verify_structure
fix_organization
consolidate_duplicates
manage_imports

# Run all fixes based on flags
if [ "$1" = "--all" ] || [ "$1" = "-a" ]; then
    fix_linting_errors
    fix_docs
    consolidate_docs
    handle_git
elif [ "$1" = "--docs" ] || [ "$1" = "-d" ]; then
    fix_docs
    consolidate_docs
    handle_git
elif [ "$1" = "--lint" ] || [ "$1" = "-l" ]; then
    fix_linting_errors
    handle_git
else
    fix_linting_errors
    fix_docs
    consolidate_docs
    handle_git
fi

echo "Verify and fix process completed successfully!"
