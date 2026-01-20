"""Tests for transcriber module."""

from unittest.mock import MagicMock, patch

import pytest
import numpy as np

from whisper_typing.transcriber import Transcriber


@patch("whisper_typing.transcriber.WhisperModel")
@patch("torch.cuda.is_available")
def test_transcriber_initialization_cpu(
    mock_cuda_avail: MagicMock, mock_whisper_model: MagicMock
) -> None:
    """Test Transcriber initialization on CPU."""
    mock_cuda_avail.return_value = False

    transcriber = Transcriber(device="cpu", compute_type="int8")

    assert transcriber.device == "cpu"
    assert transcriber.compute_type == "int8"
    mock_whisper_model.assert_called_once()


@patch("whisper_typing.transcriber.WhisperModel")
@patch("torch.cuda.is_available")
def test_transcriber_initialization_cuda_auto(
    mock_cuda_avail: MagicMock, mock_whisper_model: MagicMock
) -> None:
    """Test Transcriber initialization on CUDA with auto compute type."""
    mock_cuda_avail.return_value = True

    transcriber = Transcriber(device="cuda", compute_type="auto")

    assert transcriber.device == "cuda"
    assert transcriber.compute_type == "float16"  # Auto selects float16 for cuda


@patch("whisper_typing.transcriber.WhisperModel")
def test_transcribe_success(mock_whisper_model: MagicMock) -> None:
    """Test successful transcription."""
    mock_instance = mock_whisper_model.return_value

    # Mock segments result
    Segment = MagicMock()
    Segment.text = "Hello world"
    mock_instance.transcribe.return_value = ([Segment], None)

    transcriber = Transcriber()
    result = transcriber.transcribe(np.zeros(10))

    assert result == "Hello world"


@patch("whisper_typing.transcriber.WhisperModel")
def test_transcribe_multiple_segments(mock_whisper_model: MagicMock) -> None:
    """Test transcription with multiple segments."""
    mock_instance = mock_whisper_model.return_value

    Seg1 = MagicMock()
    Seg1.text = "Hello"
    Seg2 = MagicMock()
    Seg2.text = "world"
    mock_instance.transcribe.return_value = ([Seg1, Seg2], None)

    transcriber = Transcriber()
    result = transcriber.transcribe(np.zeros(10))

    assert result == "Hello world"
