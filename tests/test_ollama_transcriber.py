"""Tests for Ollama transcriber module."""

from unittest.mock import MagicMock, mock_open, patch

import numpy as np

from whisper_typing.ollama_transcriber import OllamaTranscriber

DUMMY_AUDIO_SIZE = 10


@patch("whisper_typing.ollama_transcriber.ollama.Client")
def test_ollama_transcriber_initialization_default(mock_client: MagicMock) -> None:
    """Test OllamaTranscriber initialization with default settings."""
    transcriber = OllamaTranscriber()

    assert transcriber.model_id == "whisper:latest"
    assert transcriber.language is None
    assert transcriber.ollama_host is None
    mock_client.assert_called_once_with()


@patch("whisper_typing.ollama_transcriber.ollama.Client")
def test_ollama_transcriber_initialization_custom_host(mock_client: MagicMock) -> None:
    """Test OllamaTranscriber initialization with custom host."""
    custom_host = "http://localhost:11434"
    transcriber = OllamaTranscriber(ollama_host=custom_host)

    assert transcriber.ollama_host == custom_host
    mock_client.assert_called_once_with(host=custom_host)


@patch("whisper_typing.ollama_transcriber.ollama.Client")
def test_ollama_transcribe_numpy_array(mock_client: MagicMock) -> None:
    """Test transcription with numpy array input."""
    mock_instance = mock_client.return_value
    mock_instance.generate.return_value = {"response": "Hello world"}

    transcriber = OllamaTranscriber()
    result = transcriber.transcribe(np.zeros(DUMMY_AUDIO_SIZE))

    assert result == "Hello world"
    mock_instance.generate.assert_called_once()


@patch("whisper_typing.ollama_transcriber.ollama.Client")
def test_ollama_transcribe_file_path(mock_client: MagicMock) -> None:
    """Test transcription with file path input."""
    mock_instance = mock_client.return_value
    mock_instance.generate.return_value = {"response": "Test transcription"}

    transcriber = OllamaTranscriber()

    mock_file = mock_open(read_data=b"audio_data")
    with patch("builtins.open", mock_file):
        result = transcriber.transcribe("test_audio.wav")

    assert result == "Test transcription"
    mock_instance.generate.assert_called_once()


@patch("whisper_typing.ollama_transcriber.ollama.Client")
def test_ollama_transcribe_with_language(mock_client: MagicMock) -> None:
    """Test OllamaTranscriber with language parameter."""
    transcriber = OllamaTranscriber(language="en")

    assert transcriber.language == "en"
    mock_client.assert_called_once_with()


@patch("whisper_typing.ollama_transcriber.ollama.Client")
def test_ollama_transcribe_strips_whitespace(mock_client: MagicMock) -> None:
    """Test that transcription result is stripped of whitespace."""
    mock_instance = mock_client.return_value
    mock_instance.generate.return_value = {"response": "  Test text  "}

    transcriber = OllamaTranscriber()
    result = transcriber.transcribe(np.zeros(DUMMY_AUDIO_SIZE))

    assert result == "Test text"
