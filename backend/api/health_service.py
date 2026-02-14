"""Health check service implementation for monitoring backend status."""

import time

import grpc
import torch

from backend.api import health_pb2, health_pb2_grpc


class HealthServiceImpl(health_pb2_grpc.HealthServiceServicer):
    """Implementation of gRPC HealthService."""

    def __init__(self, version: str = "1.0.0") -> None:
        """Initialize health service.

        Args:
            version: Backend version string.

        """
        self.version = version
        self.start_time = time.time()
        self.current_config = {}

    def set_config(self, config: dict) -> None:
        """Set current configuration for info responses.

        Args:
            config: Current configuration dictionary.

        """
        self.current_config = config

    def Check(  # noqa: N802
        self,
        request: health_pb2.HealthCheckRequest,  # noqa: ARG002
        context: grpc.ServicerContext,  # noqa: ARG002
    ) -> health_pb2.HealthCheckResponse:
        """Check service health status.

        Args:
            request: Health check request (empty).
            context: gRPC context.

        Returns:
            Health status response.

        """
        try:
            # Service is healthy if we can respond
            return health_pb2.HealthCheckResponse(
                status=health_pb2.HealthCheckResponse.Status.HEALTHY,
                message="Service is running",
                timestamp_ms=int(time.time() * 1000),
            )
        except Exception as e:  # noqa: BLE001
            return health_pb2.HealthCheckResponse(
                status=health_pb2.HealthCheckResponse.Status.UNHEALTHY,
                message=f"Health check failed: {e!s}",
                timestamp_ms=int(time.time() * 1000),
            )

    def GetInfo(  # noqa: N802
        self,
        request: health_pb2.InfoRequest,  # noqa: ARG002
        context: grpc.ServicerContext,  # noqa: ARG002
    ) -> health_pb2.InfoResponse:
        """Get service information.

        Args:
            request: Info request (empty).
            context: gRPC context.

        Returns:
            Service information response.

        """
        try:
            # Check CUDA availability
            cuda_available = torch.cuda.is_available()

            # Get current device
            device = self.current_config.get("device", "cpu")

            # Get backend type
            whisper_backend = (
                "ollama" if self.current_config.get("use_ollama") else "faster-whisper"
            )

            # Get current model
            current_model = self.current_config.get("model", "unknown")

            # Calculate uptime
            uptime_seconds = int(time.time() - self.start_time)

            return health_pb2.InfoResponse(
                version=self.version,
                whisper_backend=whisper_backend,
                device=device,
                cuda_available=cuda_available,
                current_model=current_model,
                uptime_seconds=uptime_seconds,
            )
        except Exception:  # noqa: BLE001
            # Return minimal info on error
            return health_pb2.InfoResponse(
                version=self.version,
                whisper_backend="unknown",
                device="unknown",
                cuda_available=False,
                current_model="unknown",
                uptime_seconds=0,
            )
