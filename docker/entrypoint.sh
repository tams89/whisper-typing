#!/bin/bash
set -e

echo "Starting whisper-typing backend..."

# Check if CUDA is available
if command -v nvidia-smi &> /dev/null; then
    echo "NVIDIA GPU detected:"
    nvidia-smi --query-gpu=name,memory.total --format=csv,noheader
else
    echo "No NVIDIA GPU detected, running on CPU"
fi

# Set default values for environment variables
export MODEL="${MODEL:-openai/whisper-base.en}"
export DEVICE="${DEVICE:-cuda}"
export LANGUAGE="${LANGUAGE:-en}"
export COMPUTE_TYPE="${COMPUTE_TYPE:-auto}"
export USE_OLLAMA="${USE_OLLAMA:-false}"
export MODEL_CACHE_DIR="${MODEL_CACHE_DIR:-/app/models}"
export GRPC_PORT="${GRPC_PORT:-50051}"
export WEB_PORT="${WEB_PORT:-8080}"

echo "Configuration:"
echo "  Model: $MODEL"
echo "  Device: $DEVICE"
echo "  Language: $LANGUAGE"
echo "  Compute Type: $COMPUTE_TYPE"
echo "  Use Ollama: $USE_OLLAMA"
echo "  Model Cache Dir: $MODEL_CACHE_DIR"
echo "  gRPC Port: $GRPC_PORT"
echo "  Web Port: $WEB_PORT"

# Update config.json with environment variables
cat > /app/config.json << EOF
{
  "model": "$MODEL",
  "language": "$LANGUAGE",
  "device": "$DEVICE",
  "compute_type": "$COMPUTE_TYPE",
  "use_ollama": $USE_OLLAMA,
  "ollama_host": "${OLLAMA_HOST}",
  "model_cache_dir": "$MODEL_CACHE_DIR",
  "gemini_model": "${GEMINI_MODEL:-models/gemini-2.0-flash}"
}
EOF

# Start gRPC server
echo "Starting gRPC server on port $GRPC_PORT..."
cd /app
exec uv run python backend/server.py --port "$GRPC_PORT" --config config.json
