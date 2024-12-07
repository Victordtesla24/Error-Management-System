#!/bin/bash
set -e

echo "Running run.sh..."

# Clean project environment
echo "Cleaning environment..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete
find . -type f -name "*.pyo" -delete
find . -type f -name "*.pyd" -delete
find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name ".coverage" -delete
find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Execute verify_and_fix.sh
echo "Running verify_and_fix.sh..."
bash scripts/verify_and_fix.sh

# Run test suite
echo "Running test suite..."

# Linter checks
echo "Running linter checks..."
if command -v black &> /dev/null; then
    echo "Running black..."
    black --check src tests
fi

if command -v flake8 &> /dev/null; then
    echo "Running flake8..."
    flake8 src tests
fi

if command -v isort &> /dev/null; then
    echo "Running isort..."
    isort --check-only src tests
fi

# Run pytest with coverage
echo "Running pytest..."
pytest -v --cov=src --cov-report=term-missing

# Generate test cases for failures
echo "Generating test cases for failures..."
failed_tests=$(pytest --collect-only -q 2>&1 | grep "FAILED" || true)
if [ ! -z "$failed_tests" ]; then
    echo "Failed tests detected, generating additional test cases..."
    for test in $failed_tests; do
        test_file=$(echo $test | cut -d':' -f1)
        test_name=$(echo $test | cut -d':' -f2)
        echo "Generating additional test case for $test_name in $test_file"
    done
fi

# Git operations
echo "Performing git operations..."
if git status --porcelain | grep -q '^'; then
    # Generate commit message
    commit_msg="Auto-commit: $(date)\n\nChanges:\n"
    commit_msg+="$(git status --porcelain | sed 's/^/- /')"
    
    # Stage and commit changes
    git add .
    git commit -m "$commit_msg"
    
    # Push to main branch
    if git remote -v | grep -q origin; then
        echo "Pushing to main branch..."
        git push origin main || echo "Failed to push to remote"
    else
        echo "No remote repository configured"
    fi
else
    echo "No changes to commit"
fi

# Deploy application
echo "Deploying application..."
if [ -f "docker-compose.yml" ]; then
    echo "Deploying with Docker Compose..."
    docker-compose up -d
elif [ -d "kubernetes" ]; then
    echo "Deploying to Kubernetes..."
    kubectl apply -f kubernetes/
else
    echo "No deployment configuration found"
fi

echo "run.sh completed successfully"
