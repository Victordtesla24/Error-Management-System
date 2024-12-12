#!/bin/bash

# Error Management System - Documentation
# Handles documentation management and updates

# Function to fix documentation
fix_docs() {
    log "Fixing documentation..."
    
    # Install doc tools one by one
    install_packages pydocstyle
    install_packages mdformat
    
    # Format markdown files
    log "Formatting markdown files..."
    if command_exists mdformat; then
        find "$DOCS_DIR" -name "*.md" -type f -exec mdformat {} \; || log "WARNING: mdformat failed"
    else
        log "WARNING: mdformat not found, skipping"
    fi
    
    # Update documentation timestamps without creating backups
    log "Updating timestamps..."
    if is_macos; then
        find "$DOCS_DIR" -name "*.md" -type f -exec sed -i '' "s/Last [Uu]pdated:.*/Last Updated: $(date)/" {} \;
    else
        find "$DOCS_DIR" -name "*.md" -type f -exec sed -i "s/Last [Uu]pdated:.*/Last Updated: $(date)/" {} \;
    fi
    
    # Fix docstring issues (Python files only)
    log "Running pydocstyle..."
    if command_exists pydocstyle; then
        pydocstyle . --match='(?!test_).*\.py' --ignore=D100,D101,D102,D103,D104,D105,D107 || log "WARNING: pydocstyle found issues"
    else
        log "WARNING: pydocstyle not found, skipping"
    fi
}

# Function to consolidate documentation
consolidate_docs() {
    log "Consolidating documentation..."
    
    # Create necessary directories
    ensure_dir "$DOCS_DIR"/{implementation,api,user}
    
    # Move and organize documentation files
    if dir_exists "$DOCS_DIR"; then
        # Consolidate implementation docs
        if dir_exists "$DOCS_DIR/implementation_plans"; then
            cat "$DOCS_DIR/implementation_plans/phase"*_*.md > "$DOCS_DIR/implementation/development_plan_new.md" 2>/dev/null
            mv "$DOCS_DIR/implementation/development_plan_new.md" "$DOCS_DIR/implementation/development_plan.md" 2>/dev/null
            rm -rf "$DOCS_DIR/implementation_plans" 2>/dev/null
        fi
        
        # Clean up empty files
        find "$DOCS_DIR" -type f -name "*.md" -size 0 -delete 2>/dev/null
        
        # Remove redundant documentation
        rm -f "$DOCS_DIR/final_report.md" "$DOCS_DIR/AUTHORS.md" 2>/dev/null
    fi
}

# Function to generate API documentation
generate_api_docs() {
    log "Generating API documentation..."
    
    # Install required package
    install_packages pdoc3
    
    if command_exists pdoc3; then
        # Generate API documentation
        pdoc3 --html --output-dir "$DOCS_DIR/api" src/ || log "WARNING: pdoc3 failed"
        
        # Create API index
        {
            echo "# API Documentation"
            echo "Last Updated: $(date)"
            echo
            echo "## Modules"
            find "$DOCS_DIR/api" -name "*.html" | while read -r file; do
                local module
                module=$(basename "$file" .html)
                echo "- [$module]($file)"
            done
        } > "$DOCS_DIR/api/README.md"
    else
        log "WARNING: pdoc3 not found, skipping API documentation generation"
    fi
}

# Function to update README
update_readme() {
    log "Updating README..."
    
    local readme="README.md"
    if ! file_exists "$readme"; then
        cat > "$readme" << 'EOL'
# Error Management System

An autonomous, real-time error detection and fixing system.

## Features

- 🔍 Real-time error monitoring
- 🤖 Automated error detection and fixing
- 📊 Performance metrics and analytics
- 🧠 Intelligent error analysis
- ⚙️ Customizable error handling rules

## Requirements

- Python 3.11
- Homebrew (for macOS)
- Git

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/Victordtesla24/Error-Management-System.git
   cd Error-Management-System
   ```

2. Run the setup script:
   ```bash
   ./scripts/project_setup.sh
   ```

3. Start the system:
   ```bash
   ./scripts/run.sh
   ```

## Documentation

- [User Guide](docs/user/README.md)
- [API Documentation](docs/api/README.md)
- [Implementation Details](docs/implementation/README.md)

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
EOL
        log "Created README.md"
    fi
}

# Function to update user documentation
update_user_docs() {
    log "Updating user documentation..."
    
    local user_readme="$DOCS_DIR/user/README.md"
    if ! file_exists "$user_readme"; then
        ensure_dir "$DOCS_DIR/user"
        cat > "$user_readme" << 'EOL'
# User Guide

## Introduction

The Error Management System provides real-time error detection and automated fixing capabilities.

## Getting Started

1. Start the system:
   ```bash
   ./scripts/run.sh
   ```

2. Open the dashboard:
   http://localhost:8502

## Features

### Error Monitoring

The system continuously monitors:
- Python syntax errors
- Runtime errors
- System resource usage
- Dependencies
- File changes

### Automated Fixes

The system can automatically fix:
- Code style issues
- Import organization
- Common syntax errors
- Dependency issues

### Dashboard

The web dashboard provides:
- Real-time error monitoring
- System health metrics
- Error analysis
- Fix history

## Configuration

### Error Thresholds

Edit `.streamlit/config.toml` to adjust:
- Memory usage threshold
- CPU usage threshold
- Disk usage threshold

### Monitoring Rules

Customize monitoring rules in:
- `src/core/rules.py`
- `src/error_handlers/`

## Troubleshooting

### Common Issues

1. Dashboard not loading
   - Check if port 8502 is available
   - Ensure Streamlit is installed
   - Check logs in `logs/error.log`

2. Fixes not applying
   - Verify Python version (3.11 required)
   - Check permissions
   - Review `logs/monitor.log`

### Getting Help

- Check the [API Documentation](../api/README.md)
- Review the [Implementation Details](../implementation/README.md)
- Open an issue on GitHub
EOL
        log "Created user documentation"
    fi
}

# Function to update implementation documentation
update_implementation_docs() {
    log "Updating implementation documentation..."
    
    local impl_readme="$DOCS_DIR/implementation/README.md"
    if ! file_exists "$impl_readme"; then
        ensure_dir "$DOCS_DIR/implementation"
        cat > "$impl_readme" << 'EOL'
# Implementation Details

## Architecture

### Core Components

1. Error Monitoring
   - Real-time syntax checking
   - Runtime error detection
   - Resource monitoring
   - Dependency tracking

2. Error Analysis
   - Pattern recognition
   - Root cause analysis
   - Fix suggestion generation

3. Automated Fixes
   - Code style formatting
   - Import organization
   - Common error patterns
   - Resource optimization

4. Dashboard
   - Real-time metrics
   - Error visualization
   - System health monitoring
   - Fix history tracking

## Technologies

- Python 3.11
- Streamlit
- Git
- Shell scripting

## Directory Structure

```
.
├── docs/               # Documentation
├── logs/               # System logs
├── scripts/            # Shell scripts
├── src/                # Source code
│   ├── core/          # Core functionality
│   ├── error_handlers/ # Error handlers
│   ├── monitors/      # System monitors
│   └── dashboard/     # Streamlit app
└── tests/             # Test suites
```

## Development Workflow

1. Code Changes
   - Write tests first
   - Implement features
   - Run verify_and_fix.sh
   - Commit changes

2. Documentation
   - Update API docs
   - Update user guide
   - Update implementation details

3. Testing
   - Unit tests
   - Integration tests
   - System tests
   - Performance tests

## Performance Considerations

- Memory usage optimization
- CPU usage monitoring
- Disk I/O management
- Network efficiency

## Security Measures

- Code security scanning
- Dependency verification
- Access control
- Error data protection

## Future Improvements

1. Enhanced Analysis
   - Machine learning integration
   - Pattern recognition
   - Predictive fixes

2. Scalability
   - Distributed monitoring
   - Cloud integration
   - Load balancing

3. Integration
   - CI/CD pipelines
   - IDE plugins
   - API endpoints
EOL
        log "Created implementation documentation"
    fi
}

# Main execution
main() {
    fix_docs
    consolidate_docs
    generate_api_docs
    update_readme
    update_user_docs
    update_implementation_docs
}

# Run main function
main 