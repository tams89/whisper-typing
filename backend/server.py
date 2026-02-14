"""Main gRPC server for whisper-typing backend API."""

import argparse
import json
import logging
import signal
import sys
from concurrent import futures
from pathlib import Path

import grpc

from backend.api import config_pb2_grpc, health_pb2_grpc, transcription_pb2_grpc
from backend.api.config_service import ConfigServiceImpl
from backend.api.health_service import HealthServiceImpl
from backend.api.transcription_service import TranscriptionServiceImpl

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class GRPCServer:
    """gRPC server for whisper-typing backend."""

    def __init__(
        self,
        port: int = 50051,
        config_path: str = "config.json",
        max_workers: int = 10,
    ) -> None:
        """Initialize gRPC server.

        Args:
            port: Port to listen on.
            config_path: Path to configuration file.
            max_workers: Maximum number of worker threads.

        """
        self.port = port
        self.config_path = Path(config_path)
        self.max_workers = max_workers
        self.server: grpc.Server | None = None

        # Load configuration
        self.config = self._load_config()

        # Initialize services
        self.config_service = ConfigServiceImpl(str(self.config_path))
        self.health_service = HealthServiceImpl(version="1.0.0")
        self.health_service.set_config(self.config)

        self.transcription_service = TranscriptionServiceImpl(
            use_ollama=self.config.get("use_ollama", False),
            model=self.config.get("model", "openai/whisper-base.en"),
            ollama_host=self.config.get("ollama_host"),
            device=self.config.get("device", "cpu"),
            compute_type=self.config.get("compute_type", "auto"),
            language=self.config.get("language", "en"),
            model_cache_dir=self.config.get("model_cache_dir"),
        )

    def _load_config(self) -> dict:
        """Load configuration from file.

        Returns:
            Configuration dictionary.

        """
        if self.config_path.exists():
            with self.config_path.open() as f:
                return json.load(f)

        # Return default config
        return {
            "model": "openai/whisper-base.en",
            "language": "en",
            "device": "cpu",
            "compute_type": "auto",
            "use_ollama": False,
            "ollama_host": None,
            "model_cache_dir": "./models/",
        }

    def start(self) -> None:
        """Start the gRPC server."""
        # Create server
        self.server = grpc.server(
            futures.ThreadPoolExecutor(max_workers=self.max_workers),
        )

        # Register services
        transcription_pb2_grpc.add_TranscriptionServiceServicer_to_server(
            self.transcription_service,
            self.server,
        )
        config_pb2_grpc.add_ConfigServiceServicer_to_server(
            self.config_service,
            self.server,
        )
        health_pb2_grpc.add_HealthServiceServicer_to_server(
            self.health_service,
            self.server,
        )

        # Bind to port
        self.server.add_insecure_port(f"[::]:{self.port}")

        # Start server
        self.server.start()
        logger.info("gRPC server started on port %s", self.port)
        logger.info("Using model: %s", self.config.get("model"))
        logger.info("Device: %s", self.config.get("device"))
        backend_type = "Ollama" if self.config.get("use_ollama") else "faster-whisper"
        logger.info("Backend: %s", backend_type)

    def stop(self, grace_period: int = 5) -> None:
        """Stop the gRPC server.

        Args:
            grace_period: Grace period in seconds for graceful shutdown.

        """
        if self.server:
            logger.info("Stopping gRPC server...")
            self.server.stop(grace_period)
            logger.info("gRPC server stopped")

    def wait_for_termination(self) -> None:
        """Wait for server termination."""
        if self.server:
            self.server.wait_for_termination()


def main() -> None:
    """Run the gRPC backend server."""
    parser = argparse.ArgumentParser(description="Whisper-Typing gRPC Backend Server")
    parser.add_argument(
        "--port",
        type=int,
        default=50051,
        help="Port to listen on (default: 50051)",
    )
    parser.add_argument(
        "--config",
        type=str,
        default="config.json",
        help="Path to configuration file (default: config.json)",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=10,
        help="Maximum number of worker threads (default: 10)",
    )

    args = parser.parse_args()

    # Create and start server
    server = GRPCServer(
        port=args.port,
        config_path=args.config,
        max_workers=args.workers,
    )

    # Handle graceful shutdown
    def signal_handler(
        sig: int,  # noqa: ARG001
        frame,  # noqa: ARG001, ANN001
    ) -> None:
        """Handle shutdown signals.

        Args:
            sig: Signal number.
            frame: Current stack frame.

        """
        logger.info("Received shutdown signal")
        server.stop()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Start server and wait for termination
    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    main()
