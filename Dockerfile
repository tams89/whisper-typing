# Multi-stage Dockerfile for whisper-typing backend with CUDA support
FROM nvidia/cuda:12.4.1-runtime-ubuntu22.04 AS base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3.13 \
    python3-pip \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install uv for dependency management
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"

# Set working directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync --no-dev

# Copy source code
COPY src/ ./src/
COPY backend/ ./backend/
COPY config.json ./

# Generate gRPC code
RUN uv run python -m grpc_tools.protoc \
    -I=backend/api \
    --python_out=backend/api \
    --grpc_python_out=backend/api \
    backend/api/transcription.proto \
    backend/api/config.proto \
    backend/api/health.proto

# Create directories for models and logs
RUN mkdir -p /app/models /app/logs

# Expose gRPC port
EXPOSE 50051

# Expose web admin port
EXPOSE 8080

# Set entrypoint
COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
