#!/bin/bash

# Script to generate self-signed certificates for secure communication

# Exit on any error
set -e

# Certificate settings
CERT_DIR="certs"
DAYS_VALID=365
KEY_SIZE=4096
COUNTRY="US"
STATE="CA"
LOCALITY="San Francisco"
ORGANIZATION="Cursor AI"
ORGANIZATIONAL_UNIT="Error Management System"
COMMON_NAME="error-management.cursor-agent.svc.cluster.local"

# Create certificates directory
mkdir -p "${CERT_DIR}"

# Generate CA private key and certificate
openssl genrsa -out "${CERT_DIR}/ca.key" ${KEY_SIZE}
openssl req -x509 -new -nodes \
    -key "${CERT_DIR}/ca.key" \
    -sha256 -days ${DAYS_VALID} \
    -out "${CERT_DIR}/ca.crt" \
    -subj "/C=${COUNTRY}/ST=${STATE}/L=${LOCALITY}/O=${ORGANIZATION}/OU=${ORGANIZATIONAL_UNIT}/CN=${COMMON_NAME}"

# Generate server private key
openssl genrsa -out "${CERT_DIR}/server.key" ${KEY_SIZE}

# Generate server CSR
openssl req -new \
    -key "${CERT_DIR}/server.key" \
    -out "${CERT_DIR}/server.csr" \
    -subj "/C=${COUNTRY}/ST=${STATE}/L=${LOCALITY}/O=${ORGANIZATION}/OU=${ORGANIZATIONAL_UNIT}/CN=${COMMON_NAME}"

# Generate server certificate
openssl x509 -req \
    -in "${CERT_DIR}/server.csr" \
    -CA "${CERT_DIR}/ca.crt" \
    -CAkey "${CERT_DIR}/ca.key" \
    -CAcreateserial \
    -out "${CERT_DIR}/server.crt" \
    -days ${DAYS_VALID} \
    -sha256

# Generate client private key
openssl genrsa -out "${CERT_DIR}/client.key" ${KEY_SIZE}

# Generate client CSR
openssl req -new \
    -key "${CERT_DIR}/client.key" \
    -out "${CERT_DIR}/client.csr" \
    -subj "/C=${COUNTRY}/ST=${STATE}/L=${LOCALITY}/O=${ORGANIZATION}/OU=${ORGANIZATIONAL_UNIT}/CN=client"

# Generate client certificate
openssl x509 -req \
    -in "${CERT_DIR}/client.csr" \
    -CA "${CERT_DIR}/ca.crt" \
    -CAkey "${CERT_DIR}/ca.key" \
    -CAcreateserial \
    -out "${CERT_DIR}/client.crt" \
    -days ${DAYS_VALID} \
    -sha256

# Create Kubernetes secrets
echo "Creating Kubernetes secrets..."
kubectl create namespace cursor-agent --dry-run=client -o yaml | kubectl apply -f -

kubectl create secret generic agent-certs \
    --namespace cursor-agent \
    --from-file=ca.crt="${CERT_DIR}/ca.crt" \
    --from-file=server.key="${CERT_DIR}/server.key" \
    --from-file=server.crt="${CERT_DIR}/server.crt" \
    --dry-run=client -o yaml | kubectl apply -f -

# Set permissions
chmod 600 "${CERT_DIR}"/*.key
chmod 644 "${CERT_DIR}"/*.crt "${CERT_DIR}"/*.csr

# Clean up CSR files
rm "${CERT_DIR}"/*.csr

echo "Certificate generation complete. Certificates stored in ${CERT_DIR}/"
