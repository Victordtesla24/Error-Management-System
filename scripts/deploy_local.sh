#!/bin/bash

# Script to deploy the Error Management System locally
# Requires: Docker Desktop with Kubernetes enabled, kubectl, openssl

# Exit on any error
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}Starting Error Management System deployment...${NC}"

# Check prerequisites
echo -e "${YELLOW}Checking prerequisites...${NC}"

if ! command -v docker &> /dev/null; then
    echo -e "${RED}Docker is not installed. Please install Docker Desktop.${NC}"
    exit 1
fi

if ! command -v kubectl &> /dev/null; then
    echo -e "${RED}kubectl is not installed. Please install kubectl.${NC}"
    exit 1
fi

if ! kubectl config current-context &> /dev/null; then
    echo -e "${RED}No Kubernetes context found. Please enable Kubernetes in Docker Desktop.${NC}"
    exit 1
fi

# Generate certificates
echo -e "${YELLOW}Generating certificates...${NC}"
./scripts/generate_certs.sh

# Create namespace if it doesn't exist
echo -e "${YELLOW}Creating Kubernetes namespace...${NC}"
kubectl create namespace cursor-agent --dry-run=client -o yaml | kubectl apply -f -

# Apply ConfigMap
echo -e "${YELLOW}Applying ConfigMap...${NC}"
kubectl apply -f kubernetes/configmap.yaml

# Build Docker image
echo -e "${YELLOW}Building Docker image...${NC}"
docker-compose build

# Apply Kubernetes manifests
echo -e "${YELLOW}Applying Kubernetes manifests...${NC}"
kubectl apply -f kubernetes/deployment.yaml

# Wait for pods to be ready
echo -e "${YELLOW}Waiting for pods to be ready...${NC}"
kubectl wait --for=condition=ready pod -l app=error-management -n cursor-agent --timeout=300s

# Setup port forwarding in background
echo -e "${YELLOW}Setting up port forwarding...${NC}"
kubectl port-forward svc/error-management -n cursor-agent 50051:50051 &
PORT_FORWARD_PID=$!

# Trap cleanup
cleanup() {
    echo -e "${YELLOW}Cleaning up...${NC}"
    kill $PORT_FORWARD_PID 2>/dev/null || true
}
trap cleanup EXIT

# Display system information
echo -e "${GREEN}Error Management System deployed successfully!${NC}"
echo -e "${GREEN}System Information:${NC}"
echo -e "gRPC endpoint: localhost:50051"
echo -e "Monitoring endpoint: localhost:8080"
echo -e "\nTo view logs:"
echo -e "kubectl logs -f deployment/error-management -n cursor-agent"
echo -e "\nTo stop the system:"
echo -e "kubectl delete -f kubernetes/deployment.yaml"

# Keep script running
echo -e "${YELLOW}Press Ctrl+C to stop the system${NC}"
wait $PORT_FORWARD_PID
