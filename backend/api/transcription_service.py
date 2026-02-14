"""Transcription service implementation using existing whisper-typing modules."""

import io
import time
from collections.abc import Iterator

import grpc
import numpy as np
import soundfile as sf

from backend.api import transcription_pb2, transcription_pb2_grpc
from whisper_typing.ai_improver import AIImprover
from whisper_typing.ollama_transcriber import OllamaTranscriber
from whisper_typing.transcriber import Transcriber


class TranscriptionServiceImpl(transcription_pb2_grpc.TranscriptionServiceServicer):
    """Implementation of gRPC TranscriptionService."""

    def __init__(  # noqa: PLR0913
        self,
        *,
        use_ollama: bool = False,
        model: str = "openai/whisper-base.en",
        ollama_host: str | None = None,
        device: str = "cpu",
        compute_type: str = "auto",
        language: str = "en",
        model_cache_dir: str | None = None,
    ) -> None:
        """Initialize transcription service with configuration.

        Args:
            use_ollama: Whether to use Ollama backend.
            model: Model name to use for transcription.
            ollama_host: Ollama server URL (if using Ollama).
            device: Device to use ("cpu" or "cuda").
            compute_type: Compute type for faster-whisper.
            language: Default language code.
            model_cache_dir: Directory for model cache.

        """
        self.use_ollama = use_ollama
        self.model = model
        self.language = language

        if use_ollama:
            self.transcriber: Transcriber | OllamaTranscriber = OllamaTranscriber(
                model=model,
                host=ollama_host,
            )
        else:
            self.transcriber = Transcriber(
                model=model,
                device=device,
                compute_type=compute_type,
                download_root=model_cache_dir,
            )

    def Transcribe(  # noqa: N802
        self,
        request: transcription_pb2.AudioRequest,
        context: grpc.ServicerContext,  # noqa: ARG002
    ) -> transcription_pb2.TranscriptionResponse:
        """Transcribe a complete audio file.

        Args:
            request: Audio request with audio data and metadata.
            context: gRPC context.

        Returns:
            Transcription response with text result.

        """
        try:
            # Convert audio bytes to numpy array
            audio_data = self._audio_bytes_to_array(
                request.audio_data,
                request.sample_rate,
                request.channels,
                request.encoding,
            )

            # Perform transcription
            language = request.language if request.language else self.language
            text = self.transcriber.transcribe(audio_data, language=language)

            return transcription_pb2.TranscriptionResponse(
                text=text,
                is_partial=False,
                confidence=1.0,
                timestamp_ms=int(time.time() * 1000),
            )
        except Exception as e:  # noqa: BLE001
            return transcription_pb2.TranscriptionResponse(
                text="",
                error=str(e),
                timestamp_ms=int(time.time() * 1000),
            )

    def StreamTranscribe(  # noqa: N802
        self,
        request_iterator: Iterator[transcription_pb2.AudioChunk],
        context: grpc.ServicerContext,  # noqa: ARG002
    ) -> Iterator[transcription_pb2.TranscriptionResponse]:
        """Stream audio chunks and receive real-time transcription.

        Args:
            request_iterator: Iterator of audio chunks.
            context: gRPC context.

        Yields:
            Transcription responses (partial and final).

        """
        audio_buffer = []
        sample_rate = 16000
        channels = 1
        encoding = "pcm"

        try:
            for chunk in request_iterator:
                # Update metadata from first chunk
                if not audio_buffer:
                    sample_rate = chunk.sample_rate
                    channels = chunk.channels
                    encoding = chunk.encoding

                audio_buffer.append(chunk.audio_data)

                # If final chunk, process complete audio
                if chunk.is_final:
                    # Combine all audio data
                    complete_audio = b"".join(audio_buffer)
                    audio_array = self._audio_bytes_to_array(
                        complete_audio,
                        sample_rate,
                        channels,
                        encoding,
                    )

                    # Transcribe
                    text = self.transcriber.transcribe(
                        audio_array,
                        language=self.language,
                    )

                    yield transcription_pb2.TranscriptionResponse(
                        text=text,
                        is_partial=False,
                        confidence=1.0,
                        timestamp_ms=int(time.time() * 1000),
                    )
                    break

                # Send partial response (optional - for real-time feedback)
                # For now, we'll wait until final chunk
                # In the future, could implement streaming transcription
        except Exception as e:  # noqa: BLE001
            yield transcription_pb2.TranscriptionResponse(
                text="",
                error=str(e),
                timestamp_ms=int(time.time() * 1000),
            )

    def ImproveText(  # noqa: N802
        self,
        request: transcription_pb2.ImproveTextRequest,
        context: grpc.ServicerContext,  # noqa: ARG002
    ) -> transcription_pb2.ImproveTextResponse:
        """Improve text using AI (Gemini).

        Args:
            request: Text improvement request.
            context: gRPC context.

        Returns:
            Improved text response.

        """
        try:
            improver = AIImprover(api_key=request.api_key)
            improved_text = improver.improve_text(request.text)

            return transcription_pb2.ImproveTextResponse(
                improved_text=improved_text,
            )
        except Exception as e:  # noqa: BLE001
            return transcription_pb2.ImproveTextResponse(
                improved_text="",
                error=str(e),
            )

    def _audio_bytes_to_array(
        self,
        audio_bytes: bytes,
        sample_rate: int,  # noqa: ARG002
        channels: int,
        encoding: str,
    ) -> np.ndarray:
        """Convert audio bytes to numpy array.

        Args:
            audio_bytes: Raw audio data.
            sample_rate: Sample rate in Hz.
            channels: Number of channels.
            encoding: Audio encoding format.

        Returns:
            Audio as numpy array.

        """
        if encoding.lower() in ("wav", "wave"):
            # WAV format - use soundfile
            audio_array, _ = sf.read(io.BytesIO(audio_bytes))
        elif encoding.lower() == "pcm":
            # Raw PCM data
            audio_array = (
                np.frombuffer(audio_bytes, dtype=np.int16).astype(np.float32) / 32768.0
            )
        else:
            # Try soundfile as fallback
            audio_array, _ = sf.read(io.BytesIO(audio_bytes))

        # Convert stereo to mono if needed
        if len(audio_array.shape) > 1 and channels == 1:
            audio_array = audio_array.mean(axis=1)

        return audio_array
