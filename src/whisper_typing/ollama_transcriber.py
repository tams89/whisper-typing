"""Audio transcription using Ollama models."""

from __future__ import annotations

import io
from typing import TYPE_CHECKING

import ollama
import soundfile as sf

if TYPE_CHECKING:
    import numpy as np


class OllamaTranscriber:
    """Handles speech-to-text conversion using Ollama models."""

    def __init__(
        self,
        model_id: str = "whisper:latest",
        language: str | None = None,
        ollama_host: str | None = None,
    ) -> None:
        """Initialize the OllamaTranscriber.

        Args:
            model_id: Ollama model name (e.g., 'whisper:latest', 'whisper:medium').
            language: Optional language code for transcription.
            ollama_host: Optional Ollama server host URL.

        """
        self.model_id = model_id
        self.language = language
        self.ollama_host = ollama_host

        # Configure client
        if ollama_host:
            self.client = ollama.Client(host=ollama_host)
        else:
            self.client = ollama.Client()

    def transcribe(self, audio_input: str | np.ndarray) -> str:
        """Transcribe audio input (file path or numpy array) to text.

        Args:
            audio_input: File path to audio or numpy array of audio samples.

        Returns:
            The transcribed text.

        """
        # Handle numpy array input
        if not isinstance(audio_input, str):
            # Convert numpy array to WAV bytes
            sample_rate = 16000  # Ollama expects 16kHz
            buffer = io.BytesIO()
            sf.write(buffer, audio_input, sample_rate, format="WAV")
            audio_bytes = buffer.getvalue()
        else:
            # Read file as bytes
            with open(audio_input, "rb") as f:
                audio_bytes = f.read()

        # Use Ollama's transcribe API
        response = self.client.generate(
            model=self.model_id,
            prompt="Transcribe the following audio:",
            images=[audio_bytes],
        )

        return response["response"].strip()
