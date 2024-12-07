# Use Python 3.9 slim image optimized for M3
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ src/
COPY setup.py .

# Install the package
RUN pip install -e .

# Create non-root user
RUN useradd -m -r agent && \
    chown -R agent:agent /app
USER agent

# Set secure environment variables
ENV PYTHONPATH=/app
ENV SECURE_MODE=1
ENV PROJECT_PATH=/workspace

# Create workspace directory with correct permissions
USER root
RUN mkdir /workspace && chown agent:agent /workspace
USER agent

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD python -c "import http.client; conn = http.client.HTTPConnection('localhost:8080'); conn.request('GET', '/health'); response = conn.getresponse(); exit(0 if response.status == 200 else 1)"

# Expose ports for gRPC and monitoring
EXPOSE 50051 8080

# Run the error management system
ENTRYPOINT ["python", "-m", "error_management"]
CMD ["/workspace"]
