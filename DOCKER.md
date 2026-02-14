# Docker Deployment Guide for Whisper-Typing Backend

This guide explains how to deploy the whisper-typing backend as a Docker container with GPU support.

## Prerequisites

- Docker Engine 20.10 or later
- Docker Compose v2.0 or later
- NVIDIA Container Toolkit (for GPU acceleration)
- NVIDIA GPU with CUDA support (optional, can run on CPU)

### Installing NVIDIA Container Toolkit

For Ubuntu/Debian:

```bash
# Add NVIDIA package repository
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | \
  sudo tee /etc/apt/sources.list.d/nvidia-docker.list

# Install nvidia-container-toolkit
sudo apt-get update
sudo apt-get install -y nvidia-container-toolkit

# Restart Docker
sudo systemctl restart docker
```

For Windows with Docker Desktop:
- Ensure you have WSL2 with NVIDIA GPU support enabled
- Install NVIDIA drivers for WSL2
- Docker Desktop will automatically use GPU passthrough

## Quick Start

1. **Clone the repository**:
   ```bash
   git clone https://github.com/rpfilomeno/whispher-typing.git
   cd whispher-typing
   ```

2. **Configure environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your preferred settings
   ```

3. **Build and start the container**:
   ```bash
   docker-compose up -d
   ```

4. **Check logs**:
   ```bash
   docker-compose logs -f
   ```

5. **Test the connection**:
   ```bash
   # The gRPC server should be running on port 50051
   # The web admin panel should be accessible at http://localhost:8080
   ```

## Configuration

### Environment Variables

Edit `.env` or modify `docker-compose.yml` to configure the backend:

| Variable | Default | Description |
|----------|---------|-------------|
| `MODEL` | `openai/whisper-base.en` | Whisper model to use |
| `DEVICE` | `cuda` | Device (`cuda` or `cpu`) |
| `LANGUAGE` | `en` | Default language for transcription |
| `COMPUTE_TYPE` | `auto` | Compute type for faster-whisper |
| `USE_OLLAMA` | `false` | Use Ollama backend instead of faster-whisper |
| `OLLAMA_HOST` | `http://localhost:11434` | Ollama server URL |
| `MODEL_CACHE_DIR` | `/app/models` | Model cache directory (inside container) |
| `GEMINI_API_KEY` | - | Gemini API key for text improvement |
| `GRPC_PORT` | `50051` | gRPC server port |
| `WEB_PORT` | `8080` | Web admin panel port |

### Volume Mounts

The following directories are mounted for persistence:

- `./models:/app/models` - Model cache (models are downloaded here)
- `./config.json:/app/config.json` - Configuration file
- `./logs:/app/logs` - Application logs

## Using with Tailscale

To make the backend accessible over Tailscale:

1. **Install Tailscale on the host machine**:
   ```bash
   curl -fsSL https://tailscale.com/install.sh | sh
   sudo tailscale up
   ```

2. **Note your Tailscale IP**:
   ```bash
   tailscale ip -4
   ```

3. **Configure your mobile app** to connect to `<tailscale-ip>:50051`

### Exposing Ports

The container exposes:
- Port **50051**: gRPC API for transcription
- Port **8080**: Web admin panel (upcoming in Phase 3)

## Running on CPU Only

If you don't have an NVIDIA GPU or want to run on CPU:

1. Edit `docker-compose.yml` and remove the `runtime: nvidia` section
2. Set `DEVICE=cpu` in your `.env` file
3. Remove the GPU-related deployment configuration

Example CPU-only `docker-compose.yml`:

```yaml
services:
  whisper-typing-backend:
    build:
      context: .
      dockerfile: Dockerfile
    environment:
      - DEVICE=cpu
      - MODEL=openai/whisper-tiny.en  # Use smaller model for CPU
    ports:
      - "50051:50051"
    volumes:
      - ./models:/app/models
    restart: unless-stopped
```

## Using Ollama Backend

To use Ollama instead of faster-whisper:

1. **Install and start Ollama** (can be on the same or different machine):
   ```bash
   # Install Ollama
   curl -fsSL https://ollama.ai/install.sh | sh
   
   # Pull Whisper model
   ollama pull whisper
   ```

2. **Configure the backend**:
   ```env
   USE_OLLAMA=true
   MODEL=whisper:latest
   OLLAMA_HOST=http://localhost:11434  # Or remote Ollama server
   ```

3. **Restart the container**:
   ```bash
   docker-compose restart
   ```

## Updating the Backend

To update to the latest version:

```bash
# Pull latest changes
git pull origin feature/mobile-backend-api

# Rebuild the container
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

## Troubleshooting

### Container won't start

Check logs:
```bash
docker-compose logs whisper-typing-backend
```

### GPU not detected

Verify NVIDIA Container Toolkit:
```bash
docker run --rm --gpus all nvidia/cuda:12.4.1-base-ubuntu22.04 nvidia-smi
```

### Model download is slow

Models are downloaded on first run. Whisper models range from:
- Tiny: ~75 MB
- Base: ~150 MB
- Small: ~500 MB
- Medium: ~1.5 GB
- Large-v3: ~3 GB

### Permission errors

Ensure Docker has permission to create directories:
```bash
mkdir -p models logs
chmod 777 models logs
```

## Performance Notes

- **GPU (CUDA)**: Real-time transcription possible with base/small models
- **CPU**: Slower than real-time for medium/large models
- **Ollama**: Performance depends on Ollama server configuration

## Security Notes

- The container runs gRPC without TLS by default
- When using over Tailscale, the connection is already encrypted
- For additional security, API key authentication will be added in Phase 1 completion
- Never expose the gRPC port directly to the internet without authentication

## Next Steps

- Configure the mobile Flutter app to connect to your backend
- Set up the web admin panel (Phase 3)
- Configure Gemini API key for text improvement feature
