#!/bin/bash

# Error Management System - Git Management
# Handles version control operations

# Function to handle git operations
handle_git() {
    log "Setting up git repository..."
    
    # Initialize git if needed
    if [ ! -d ".git" ]; then
        git init
        log "Git repository initialized"
    fi
    
    # Configure git user if not set
    if [ -z "$(git config --get user.email)" ]; then
        git config user.email "melbvicduque@gmail.com"
        git config user.name "Victordtesla24"
        log "Git user configured"
    fi
    
    # Check if remote exists, if not add it
    if ! git remote | grep -q "origin"; then
        git remote add origin "$GITHUB_REPO"
        log "Remote origin added"
    fi
    
    # Ensure we're on main branch
    if ! git rev-parse --verify main >/dev/null 2>&1; then
        git branch -M main
        log "Created and switched to main branch"
    else
        git checkout main
        log "Switched to main branch"
    fi
}

# Function to generate commit message
generate_commit_message() {
    log "Generating commit message..."
    
    local commit_msg="Update: $(date)\n\nChanges:"
    local has_changes=false
    
    # Check for modified files
    if git status --porcelain | grep -q "^M"; then
        commit_msg+="\n- Modified files:"
        while IFS= read -r file; do
            commit_msg+="\n  * $file"
        done < <(git status --porcelain | grep "^M" | cut -c4-)
        has_changes=true
    fi
    
    # Check for added files
    if git status --porcelain | grep -q "^A"; then
        commit_msg+="\n- Added files:"
        while IFS= read -r file; do
            commit_msg+="\n  * $file"
        done < <(git status --porcelain | grep "^A" | cut -c4-)
        has_changes=true
    fi
    
    # Check for deleted files
    if git status --porcelain | grep -q "^D"; then
        commit_msg+="\n- Removed files:"
        while IFS= read -r file; do
            commit_msg+="\n  * $file"
        done < <(git status --porcelain | grep "^D" | cut -c4-)
        has_changes=true
    fi
    
    # Check for renamed files
    if git status --porcelain | grep -q "^R"; then
        commit_msg+="\n- Renamed files:"
        while IFS= read -r file; do
            commit_msg+="\n  * $file"
        done < <(git status --porcelain | grep "^R" | cut -c4-)
        has_changes=true
    fi
    
    # Add error fixes if any
    if [ -f "$ERROR_LOG" ]; then
        local error_count
        error_count=$(wc -l < "$ERROR_LOG")
        if [ "$error_count" -gt 0 ]; then
            commit_msg+="\n\nFixed Errors:"
            commit_msg+="\n- Total errors fixed: $error_count"
            commit_msg+="\n- See logs/error.log for details"
        fi
    fi
    
    echo "$commit_msg"
    [ "$has_changes" = true ]
}

# Function to stage changes
stage_changes() {
    log "Staging changes..."
    
    # Add all files except those in .gitignore
    git add .
    
    # Remove any files that should be ignored
    if file_exists ".gitignore"; then
        git rm -r --cached . >/dev/null 2>&1
        git add .
    fi
    
    log "Changes staged"
}

# Function to commit changes
commit_changes() {
    log "Committing changes..."
    
    local commit_msg
    if ! commit_msg=$(generate_commit_message); then
        log "No changes to commit"
        return 1
    fi
    
    # Commit with generated message
    if ! git commit -m "$commit_msg"; then
        log "ERROR: Failed to commit changes"
        return 1
    fi
    
    log "Changes committed"
    return 0
}

# Function to push changes
push_changes() {
    log "Pushing changes..."
    
    # Try to push changes
    if git push -u origin main 2>/dev/null; then
        log "Successfully pushed to remote"
        return 0
    else
        log "WARNING: Push failed. Manual push required:"
        log "git push -u origin main"
        log "Or if force push is needed:"
        log "git push -u origin main --force"
        return 1
    fi
}

# Function to create .gitignore
create_gitignore() {
    log "Creating .gitignore..."
    
    local gitignore=".gitignore"
    if ! file_exists "$gitignore"; then
        cat > "$gitignore" << EOL
# Python
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

# Virtual Environment
venv/
ENV/
env/

# IDE
.idea/
.vscode/
*.swp
*.swo
*~

# Testing
.pytest_cache/
.coverage
htmlcov/
.tox/
.nox/
.coverage.*
coverage.xml
*.cover
*.py,cover
.hypothesis/

# Logs
logs/
*.log

# Environment variables
.env
.env.*

# System
.DS_Store
Thumbs.db
EOL
        log "Created .gitignore"
    fi
}

# Function to verify git state
verify_git_state() {
    log "Verifying git state..."
    
    # Check if we're in a git repository
    if ! git rev-parse --git-dir > /dev/null 2>&1; then
        log "ERROR: Not in a git repository"
        return 1
    fi
    
    # Check if we have uncommitted changes
    if ! git diff --quiet HEAD; then
        log "WARNING: Uncommitted changes found"
    fi
    
    # Check if we're behind remote
    if git remote | grep -q "origin"; then
        git fetch origin
        local behind
        behind=$(git rev-list HEAD..origin/main --count 2>/dev/null)
        if [ "$behind" -gt 0 ]; then
            log "WARNING: Local branch is behind remote by $behind commits"
        fi
    fi
    
    return 0
}

# Main execution
main() {
    create_gitignore
    handle_git
    verify_git_state
    stage_changes
    commit_changes && push_changes
}

# Run main function
main 