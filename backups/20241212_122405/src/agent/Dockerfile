FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    POETRY_VERSION=1.4.2

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy project files
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir -r requirements-grpc.txt \
    && pip install --no-cache-dir -r requirements-streamlit.txt

# Install development dependencies
RUN pip install --no-cache-dir pytest pytest-asyncio pytest-cov pylint flake8 mypy black isort

# Make scripts executable
RUN chmod +x scripts/*.sh

# Create necessary directories
RUN mkdir -p logs reports backups

# Set Python path
ENV PYTHONPATH=/app

# Create entrypoint script for autonomous operation
RUN echo '#!/bin/bash\n\
# Start error management service\n\
python -m src.error_management &\n\
\n\
# Start agent monitoring\n\
python -m src.agent.main &\n\
\n\
# Start dashboard\n\
streamlit run src/dashboard/Home.py --server.port=8502 --server.address=0.0.0.0 &\n\
\n\
# Execute verify and fix script periodically\n\
while true; do\n\
    ./scripts/verify_and_fix.sh\n\
    sleep 60\n\
done' > /app/entrypoint.sh \
    && chmod +x /app/entrypoint.sh

# Set entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]
