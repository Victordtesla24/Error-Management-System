#!/bin/bash

# Exit on any error
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}Setting up Error Management System Dashboard...${NC}"

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo -e "${RED}Node.js is not installed. Please install Node.js first.${NC}"
    exit 1
fi

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo -e "${RED}npm is not installed. Please install npm first.${NC}"
    exit 1
fi

# Navigate to dashboard directory
cd "$(dirname "$0")/../src/dashboard/static"

# Install dependencies
echo -e "${YELLOW}Installing dependencies...${NC}"
npm install

# Create production build
echo -e "${YELLOW}Creating production build...${NC}"
npm run build

# Create necessary directories
mkdir -p ../static/build

# Copy build files
echo -e "${YELLOW}Copying build files...${NC}"
cp -r build/* ../static/

# Setup Python environment
echo -e "${YELLOW}Setting up Python environment...${NC}"
cd ../../..
python -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

echo -e "${GREEN}Dashboard setup complete!${NC}"
echo -e "You can now run the system using: ${YELLOW}./scripts/run_system.sh${NC}"

# Create run script if it doesn't exist
if [ ! -f scripts/run_system.sh ]; then
    cat > scripts/run_system.sh << 'EOF'
#!/bin/bash

# Exit on any error
set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Activate virtual environment
source venv/bin/activate

# Start the system
echo -e "${YELLOW}Starting Error Management System...${NC}"

# Start backend service
python -m error_management &
BACKEND_PID=$!

# Start dashboard service
python -m dashboard.service &
DASHBOARD_PID=$!

# Handle shutdown
cleanup() {
    echo -e "${YELLOW}Shutting down services...${NC}"
    kill $BACKEND_PID 2>/dev/null || true
    kill $DASHBOARD_PID 2>/dev/null || true
    exit 0
}

trap cleanup SIGINT SIGTERM

echo -e "${GREEN}System is running!${NC}"
echo "Dashboard: http://localhost:8080"
echo "Backend API: http://localhost:50051"
echo "Press Ctrl+C to stop"

# Wait for processes
wait $BACKEND_PID $DASHBOARD_PID
EOF

    chmod +x scripts/run_system.sh
    echo -e "${GREEN}Created run script: scripts/run_system.sh${NC}"
fi

# Create development script
cat > scripts/dev.sh << 'EOF'
#!/bin/bash

# Exit on any error
set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Activate virtual environment
source venv/bin/activate

# Start backend in development mode
echo -e "${YELLOW}Starting backend in development mode...${NC}"
python -m error_management --debug &
BACKEND_PID=$!

# Start frontend in development mode
cd src/dashboard/static
echo -e "${YELLOW}Starting frontend in development mode...${NC}"
npm start &
FRONTEND_PID=$!

# Handle shutdown
cleanup() {
    echo -e "${YELLOW}Shutting down services...${NC}"
    kill $BACKEND_PID 2>/dev/null || true
    kill $FRONTEND_PID 2>/dev/null || true
    exit 0
}

trap cleanup SIGINT SIGTERM

echo -e "${GREEN}Development server is running!${NC}"
echo "Frontend: http://localhost:3000"
echo "Backend API: http://localhost:50051"
echo "Press Ctrl+C to stop"

# Wait for processes
wait $BACKEND_PID $FRONTEND_PID
EOF

chmod +x scripts/dev.sh
echo -e "${GREEN}Created development script: scripts/dev.sh${NC}"

echo -e "\n${GREEN}Setup complete!${NC}"
echo -e "To start the system in production mode: ${YELLOW}./scripts/run_system.sh${NC}"
echo -e "To start the system in development mode: ${YELLOW}./scripts/dev.sh${NC}"
