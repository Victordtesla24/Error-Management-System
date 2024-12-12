FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    AUTO_FIX=1 \
    MONITOR_ENABLED=1 \
    ERROR_DETECTION_ENABLED=1 \
    DEBIAN_FRONTEND=noninteractive \
    PYTHONPATH=/app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    build-essential \
    inotify-tools \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements*.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir -r requirements-grpc.txt \
    && pip install --no-cache-dir -r requirements-streamlit.txt

# Copy project files
COPY . .

# Create necessary directories
RUN mkdir -p logs backups reports

# Make scripts executable
RUN chmod +x scripts/*.sh entrypoint.sh

# Expose ports
EXPOSE 8502 8080

# Set entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]
