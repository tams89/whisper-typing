"""Configuration service implementation for backend settings management."""

import json
from pathlib import Path

import grpc

from backend.api import config_pb2, config_pb2_grpc


class ConfigServiceImpl(config_pb2_grpc.ConfigServiceServicer):
    """Implementation of gRPC ConfigService."""

    def __init__(self, config_path: str = "config.json") -> None:
        """Initialize configuration service.

        Args:
            config_path: Path to configuration file.

        """
        self.config_path = Path(config_path)
        self._load_config()

    def _load_config(self) -> None:
        """Load configuration from file."""
        if self.config_path.exists():
            with self.config_path.open() as f:
                self.config_data = json.load(f)
        else:
            # Default configuration
            self.config_data = {
                "model": "openai/whisper-base.en",
                "language": "en",
                "device": "cpu",
                "compute_type": "auto",
                "use_ollama": False,
                "ollama_host": None,
                "model_cache_dir": "./models/",
                "gemini_model": "models/gemini-2.0-flash",
            }

    def _save_config(self) -> None:
        """Save configuration to file."""
        with self.config_path.open("w") as f:
            json.dump(self.config_data, f, indent=2)

    def _dict_to_proto_config(self, config_dict: dict) -> config_pb2.Config:
        """Convert dictionary to protobuf Config message.

        Args:
            config_dict: Configuration dictionary.

        Returns:
            Protobuf Config message.

        """
        return config_pb2.Config(
            model=config_dict.get("model", ""),
            language=config_dict.get("language", "en"),
            device=config_dict.get("device", "cpu"),
            compute_type=config_dict.get("compute_type", "auto"),
            use_ollama=config_dict.get("use_ollama", False),
            ollama_host=config_dict.get("ollama_host", ""),
            model_cache_dir=config_dict.get("model_cache_dir", "./models/"),
            gemini_model=config_dict.get("gemini_model", "models/gemini-2.0-flash"),
        )

    def _proto_config_to_dict(self, config: config_pb2.Config) -> dict:
        """Convert protobuf Config to dictionary.

        Args:
            config: Protobuf Config message.

        Returns:
            Configuration dictionary.

        """
        return {
            "model": config.model,
            "language": config.language,
            "device": config.device,
            "compute_type": config.compute_type,
            "use_ollama": config.use_ollama,
            "ollama_host": config.ollama_host if config.ollama_host else None,
            "model_cache_dir": config.model_cache_dir,
            "gemini_model": config.gemini_model,
        }

    def GetConfig(  # noqa: N802
        self,
        request: config_pb2.GetConfigRequest,  # noqa: ARG002
        context: grpc.ServicerContext,  # noqa: ARG002
    ) -> config_pb2.ConfigResponse:
        """Get current configuration.

        Args:
            request: Get config request (empty).
            context: gRPC context.

        Returns:
            Current configuration.

        """
        try:
            config = self._dict_to_proto_config(self.config_data)
            return config_pb2.ConfigResponse(config=config)
        except Exception as e:  # noqa: BLE001
            return config_pb2.ConfigResponse(error=str(e))

    def UpdateConfig(  # noqa: N802
        self,
        request: config_pb2.UpdateConfigRequest,
        context: grpc.ServicerContext,  # noqa: ARG002
    ) -> config_pb2.ConfigResponse:
        """Update configuration.

        Args:
            request: Update config request with new configuration.
            context: gRPC context.

        Returns:
            Updated configuration.

        """
        try:
            # Update config data
            new_config = self._proto_config_to_dict(request.config)
            self.config_data.update(new_config)

            # Save to file
            self._save_config()

            # Return updated config
            config = self._dict_to_proto_config(self.config_data)
            return config_pb2.ConfigResponse(config=config)
        except Exception as e:  # noqa: BLE001
            return config_pb2.ConfigResponse(error=str(e))

    def ListModels(  # noqa: N802
        self,
        request: config_pb2.ListModelsRequest,
        context: grpc.ServicerContext,  # noqa: ARG002
    ) -> config_pb2.ListModelsResponse:
        """List available models.

        Args:
            request: List models request.
            context: gRPC context.

        Returns:
            List of available models.

        """
        try:
            models = []

            # faster-whisper models
            whisper_models = [
                ("openai/whisper-tiny.en", "Tiny (English)", "tiny"),
                ("openai/whisper-base.en", "Base (English)", "base"),
                ("openai/whisper-small.en", "Small (English)", "small"),
                ("openai/whisper-medium.en", "Medium (English)", "medium"),
                ("openai/whisper-large-v3", "Large V3", "large-v3"),
            ]

            for model_name, display_name, size in whisper_models:
                models.append(
                    config_pb2.ModelInfo(
                        name=model_name,
                        display_name=display_name,
                        size=size,
                        size_bytes=0,  # Would need to check actual size
                        is_downloaded=False,  # Would need to check cache
                        backend="faster-whisper",
                    )
                )

            # Ollama models (if requested)
            if request.include_ollama:
                ollama_models = [
                    ("whisper:latest", "Whisper (Latest)", "base"),
                    ("whisper:medium", "Whisper (Medium)", "medium"),
                    ("whisper:large", "Whisper (Large)", "large"),
                ]

                for model_name, display_name, size in ollama_models:
                    models.append(
                        config_pb2.ModelInfo(
                            name=model_name,
                            display_name=display_name,
                            size=size,
                            size_bytes=0,
                            is_downloaded=False,
                            backend="ollama",
                        )
                    )

            return config_pb2.ListModelsResponse(models=models)
        except Exception as e:  # noqa: BLE001
            return config_pb2.ListModelsResponse(error=str(e))

    def TestConfig(  # noqa: N802
        self,
        request: config_pb2.TestConfigRequest,
        context: grpc.ServicerContext,  # noqa: ARG002
    ) -> config_pb2.TestConfigResponse:
        """Test configuration by attempting to load model.

        Args:
            request: Test config request with configuration to test.
            context: gRPC context.

        Returns:
            Test result with success status.

        """
        try:
            config_dict = self._proto_config_to_dict(request.config)

            # Try to initialize transcriber with given config
            if config_dict.get("use_ollama"):
                from whisper_typing.ollama_transcriber import (  # noqa: PLC0415
                    OllamaTranscriber,
                )

                _ = OllamaTranscriber(
                    model=config_dict["model"],
                    host=config_dict.get("ollama_host"),
                )
            else:
                from whisper_typing.transcriber import (  # noqa: PLC0415
                    Transcriber,
                )

                _ = Transcriber(
                    model=config_dict["model"],
                    device=config_dict["device"],
                    compute_type=config_dict["compute_type"],
                    download_root=config_dict.get("model_cache_dir"),
                )

            # If we got here, initialization succeeded
            message = f"Successfully loaded {config_dict['model']}"

            # If test audio provided, try transcribing
            transcription = ""
            if request.test_audio:
                # Would need to implement test transcription
                message += " (test transcription not yet implemented)"

            return config_pb2.TestConfigResponse(
                success=True,
                message=message,
                transcription=transcription,
            )
        except Exception as e:  # noqa: BLE001
            return config_pb2.TestConfigResponse(
                success=False,
                message=f"Configuration test failed: {e!s}",
                error=str(e),
            )
