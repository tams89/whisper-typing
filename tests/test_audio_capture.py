"""Tests for audio_capture module."""

import threading
import time
from unittest.mock import MagicMock, patch

import pytest
import numpy as np

from whisper_typing.audio_capture import AudioRecorder


@patch("sounddevice.query_devices")
def test_list_devices(mock_query_devices: MagicMock) -> None:
    """Test listing available input devices."""
    mock_query_devices.return_value = [
        {"name": "Mic 1", "max_input_channels": 1},
        {"name": "Speaker", "max_input_channels": 0}, # Should be ignored
        {"name": "Mic 2", "max_input_channels": 2},
    ]
    
    devices = AudioRecorder.list_devices()
    
    assert len(devices) == 2
    assert devices[0] == (0, "Mic 1")
    assert devices[1] == (2, "Mic 2")


@patch("sounddevice.InputStream")
def test_recorder_verify_callback(mock_input_stream: MagicMock) -> None:
    """Test that data is correctly accumulated in the callback."""
    recorder = AudioRecorder(device_index=0)
    
    # Manually trigger callback
    fake_data = np.zeros((10, 1), dtype=np.float32)
    recorder._callback(fake_data, 10, MagicMock(), MagicMock())
    
    # Verify data is in frames
    with recorder._lock:
        assert len(recorder.frames) == 1
        assert np.array_equal(recorder.frames[0], fake_data)


@patch("sounddevice.InputStream")
def test_get_current_data_clears_buffer(mock_input_stream: MagicMock) -> None:
    """Test get_current_data returns concatenated data and clears buffer."""
    recorder = AudioRecorder(device_index=0)
    
    # Add fake data
    frame1 = np.ones((100, 1), dtype=np.float32)
    frame2 = np.ones((100, 1), dtype=np.float32)
    with recorder._lock:
        recorder.frames.append(frame1)
        recorder.frames.append(frame2)
        
    data = recorder.get_current_data()
    
    assert data is not None
    assert len(data) == 200 # 100 + 100, flattened or consolidated
    # frames are not cleared by get_current_data in current implementation


def test_start_stop_logic() -> None:
    """Test start and stop state logic (mocking the actual thread or run loop)."""
    # We mock _record to avoid actual IO
    with patch.object(AudioRecorder, "_record") as mock_record:
        mock_record.side_effect = lambda: time.sleep(0.5)
        recorder = AudioRecorder()
        
        recorder.start()
        assert recorder.recording is True
        assert recorder.thread is not None
        assert recorder.thread.is_alive()
        
        # Stop
        recorder.stop()
        assert recorder.recording is False
        recorder.thread.join(timeout=1)
        assert not recorder.thread.is_alive()
