#!/bin/bash

# Error Management System - Project Structure
# Handles directory organization and Streamlit setup

# Function to verify project structure
verify_structure() {
    log "Verifying project structure..."
    
    local -a required_dirs=(
        "${SRC_DIR}/core"              # Core error management logic
        "${SRC_DIR}/error_handlers"    # Error handler implementations
        "${SRC_DIR}/monitors"          # System monitoring components
        "${SRC_DIR}/dashboard/pages"   # Streamlit pages
        "${SRC_DIR}/utils"             # Utility functions
        "${TESTS_DIR}/unit"            # Unit tests
        "${TESTS_DIR}/integration"     # Integration tests
        "${DOCS_DIR}/api"              # API documentation
        "${DOCS_DIR}/user"             # User guides
        "${DOCS_DIR}/implementation"   # Implementation details
        "scripts/core"                 # Core scripts
        "logs"                         # Log files
        "${STREAMLIT_DIR}"             # Streamlit configuration
    )
    
    for dir in "${required_dirs[@]}"; do
        ensure_dir "$dir"
    done
}

# Function to verify Streamlit configuration
verify_streamlit_config() {
    log "Verifying Streamlit configuration..."
    
    local config_file="$STREAMLIT_DIR/config.toml"
    if ! file_exists "$config_file"; then
        ensure_dir "$STREAMLIT_DIR"
        cat > "$config_file" << EOL
[theme]
primaryColor="#F63366"
backgroundColor="#FFFFFF"
secondaryBackgroundColor="#F0F2F6"
textColor="#262730"
font="sans serif"

[server]
enableCORS=false
enableXsrfProtection=true
maxUploadSize=200
port=8502
address="localhost"
baseUrlPath=""
maxMessageSize=200
enableWebsocketCompression=true

[browser]
gatherUsageStats=false
serverAddress="localhost"
serverPort=8502

[runner]
magicEnabled=true
installTracer=true
fixMatplotlib=true

[client]
showErrorDetails=true
toolbarMode="auto"

[logger]
level="info"
messageFormat="%(asctime)s %(message)s"
EOL
        log "Created Streamlit config file"
    fi
}

# Function to verify Streamlit app
verify_streamlit_app() {
    log "Verifying Streamlit application..."
    
    local home_page="$SRC_DIR/dashboard/pages/1_🏠_Home.py"
    if ! file_exists "$home_page"; then
        ensure_dir "$(dirname "$home_page")"
        cat > "$home_page" << 'EOL'
import streamlit as st

st.set_page_config(
    page_title="Error Management System",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("Error Management System")

st.markdown("""
## Real-Time Error Management

This system provides autonomous error detection, monitoring, and automated fixing capabilities.

### Key Features
- 🔍 Real-time error monitoring
- 🤖 Automated error detection and fixing
- 📊 Performance metrics and analytics
- 🧠 Intelligent error analysis
- ⚙️ Customizable error handling rules

### System Status
""")

# Display system metrics
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        label="Active Monitors",
        value="3",
        delta="All Systems Operational"
    )

with col2:
    st.metric(
        label="Error Rate",
        value="0.1%",
        delta="-0.05%"
    )

with col3:
    st.metric(
        label="Response Time",
        value="50ms",
        delta="-10ms"
    )

# Display recent activity
st.subheader("Recent Activity")
st.dataframe({
    "Timestamp": ["2 mins ago", "5 mins ago", "10 mins ago"],
    "Event": [
        "Error detected in log processing",
        "Automated fix applied successfully",
        "System health check completed"
    ],
    "Status": ["Fixed", "Success", "Passed"]
})

# Display system health
st.subheader("System Health")
st.progress(0.98)
st.caption("System operating at 98% efficiency")
EOL
        log "Created Home page"
    fi
}

# Function to fix directory organization
fix_organization() {
    log "Fixing directory organization..."
    
    # Move Python files to appropriate directories
    find . -maxdepth 1 -name "*.py" -not -path "./setup.py" -exec mv {} "$SRC_DIR/" \; 2>/dev/null || true
    find "$SRC_DIR" -maxdepth 1 -name "*_test.py" -exec mv {} "$TESTS_DIR/unit/" \; 2>/dev/null || true
    find "$SRC_DIR" -maxdepth 1 -name "test_*.py" -exec mv {} "$TESTS_DIR/unit/" \; 2>/dev/null || true
    
    # Move Streamlit pages to correct location
    find "$SRC_DIR" -name "*.py" -path "*/pages/*" -exec mv {} "$SRC_DIR/dashboard/pages/" \; 2>/dev/null || true
    
    # Organize documentation
    find . -name "*.md" -not -path "./$DOCS_DIR/*" -not -name "README.md" -exec mv {} "$DOCS_DIR/" \; 2>/dev/null || true
}

# Main execution
main() {
    verify_structure
    verify_streamlit_config
    verify_streamlit_app
    fix_organization
}

# Run main function
main 