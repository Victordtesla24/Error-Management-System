#!/bin/bash

# Exit on any error
set -e

# Configuration
DOCKER_IMAGE="error-management-agent"
DOCKER_TAG="latest"
K8S_NAMESPACE="default"

# Print timestamp
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Starting agent deployment..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "Docker is required but not installed. Please install Docker first."
    exit 1
fi

# Check if kubectl is installed
if ! command -v kubectl &> /dev/null; then
    echo "kubectl is required but not installed. Please install kubectl first."
    exit 1
fi

# Build Docker image
echo "Building Docker image..."
docker build -t ${DOCKER_IMAGE}:${DOCKER_TAG} -f src/agent/Dockerfile .

# Generate API key if not exists
if [ ! -f .api_key ]; then
    echo "Generating new API key..."
    openssl rand -base64 32 > .api_key
fi

# Create Kubernetes secret
echo "Creating Kubernetes secret..."
API_KEY=$(cat .api_key | base64)
kubectl create secret generic agent-secrets \
    --from-literal=api-key=${API_KEY} \
    --namespace=${K8S_NAMESPACE} \
    --dry-run=client -o yaml | kubectl apply -f -

# Deploy to Kubernetes
echo "Deploying to Kubernetes..."
kubectl apply -f k8s/agent-deployment.yaml --namespace=${K8S_NAMESPACE}

# Wait for deployment
echo "Waiting for deployment to complete..."
kubectl rollout status deployment/error-management-agent --namespace=${K8S_NAMESPACE}

echo "Deployment completed successfully!"
echo "You can check the agent status with: kubectl get pods -n ${K8S_NAMESPACE}" 