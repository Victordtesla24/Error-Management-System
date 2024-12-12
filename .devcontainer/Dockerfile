FROM docker/dev-environments-go:stable-1

# Remove problematic Yarn repository and clean up
RUN rm -f /etc/apt/sources.list.d/yarn.list && \
    apt-get clean

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    git \
    curl \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Install Go 1.23
RUN rm -rf /usr/local/go && \
    curl -L https://golang.org/dl/go1.23.4.linux-arm64.tar.gz | tar -C /usr/local -xz

# Set up Go environment
ENV GOPATH=/go
ENV GOROOT=/usr/local/go
ENV PATH=$PATH:/usr/local/go/bin:/go/bin

# Set up Python environment
ENV PYTHONPATH=/app/src
ENV PATH=$PATH:/usr/local/bin

# Create necessary directories
RUN mkdir -p /go/{bin,pkg,src} && \
    mkdir -p /app

WORKDIR /app

# Install base Python packages
RUN pip3 install --no-cache-dir \
    setuptools \
    wheel \
    pip --upgrade

# We'll install requirements in the container after mounting
CMD ["bash"]