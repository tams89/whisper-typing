"""Tests for app_controller module."""

import threading
import time
from unittest.mock import MagicMock, patch, ANY

import pytest

from whisper_typing.app_controller import WhisperAppController, DEFAULT_CONFIG


@pytest.fixture
def mock_dependencies():
    """Mock all external dependencies for the controller."""
    with (
        patch("whisper_typing.app_controller.AudioRecorder") as MockRecorder,
        patch("whisper_typing.app_controller.Transcriber") as MockTranscriber,
        patch("whisper_typing.app_controller.Typer") as MockTyper,
        patch("whisper_typing.app_controller.AIImprover") as MockImprover,
        patch("whisper_typing.app_controller.WindowManager") as MockWindowManager,
        patch("pynput.keyboard.GlobalHotKeys") as MockHotKeys,
        patch("whisper_typing.app_controller.sd") as MockSD,
    ):
        yield {
            "recorder": MockRecorder,
            "transcriber": MockTranscriber,
            "typer": MockTyper,
            "improver": MockImprover,
            "window_manager": MockWindowManager,
            "hotkeys": MockHotKeys,
            "sd": MockSD,
        }

    MockSD.query_devices.return_value = []


def test_initialization(mock_dependencies):
    """Test controller initialization."""
    controller = WhisperAppController()
    assert controller.config == {}

    # Components should be None until initialized
    assert controller.recorder is None
    assert controller.transcriber is None


def test_initialize_components(mock_dependencies):
    """Test initializing components."""
    controller = WhisperAppController()
    controller.config = DEFAULT_CONFIG.copy()
    controller.config["gemini_api_key"] = "fake"
    success = controller.initialize_components()

    assert success is True
    assert controller.recorder is not None
    assert controller.transcriber is not None
    assert controller.typer is not None
    assert controller.improver is not None
    assert controller.window_manager is not None


def test_start_listener(mock_dependencies):
    """Test starting the global hotkey listener."""
    controller = WhisperAppController()
    controller.config = DEFAULT_CONFIG.copy()
    controller.config["gemini_api_key"] = "fake"
    controller.initialize_components()

    controller.start_listener()

    ExpectedHotKeys = mock_dependencies["hotkeys"]
    ExpectedHotKeys.assert_called_once()

    # Check hotkey map creation (simplified check)
    args, _ = ExpectedHotKeys.call_args
    hotkey_map = args[0]
    assert controller.config["hotkey"] in hotkey_map
    assert controller.config["type_hotkey"] in hotkey_map


def test_on_record_toggle_start(mock_dependencies):
    """Test starting recording."""
    controller = WhisperAppController()
    controller.config = DEFAULT_CONFIG.copy()
    controller.config["gemini_api_key"] = "fake"
    controller.initialize_components()
    mock_wm = controller.window_manager
    mock_recorder = controller.recorder
    mock_recorder.recording = False

    # Simulate window handle
    mock_wm.get_active_window.return_value = "WindowHandle"

    # Trigger toggle (Start)
    controller.on_record_toggle()

    assert controller.window_manager is not None
    mock_wm.get_active_window.assert_called()

    assert controller.target_window_handle == "WindowHandle"
    mock_recorder.start.assert_called_once()


def test_on_record_toggle_stop(mock_dependencies):
    """Test stopping recording."""
    controller = WhisperAppController()
    controller.config = DEFAULT_CONFIG.copy()
    controller.config["gemini_api_key"] = "fake"
    controller.initialize_components()
    mock_recorder = controller.recorder
    # Set to recording state
    mock_recorder.recording = True
    controller.stop_live_transcribe = threading.Event()

    # Trigger toggle (Stop)
    controller.on_record_toggle()

    mock_recorder.stop.assert_called_once()
    assert controller.stop_live_transcribe.is_set()


def test_on_type_confirm(mock_dependencies):
    """Test typing confirmation."""
    controller = WhisperAppController()
    controller.config = DEFAULT_CONFIG.copy()
    controller.config["gemini_api_key"] = "fake"
    controller.initialize_components()
    mock_typer = controller.typer

    controller.pending_text = "Hello World"

    # Mock threading to run synchronously for test or just assert it was started
    # Here we simulate the logic inside the thread or check if thread started
    with patch("threading.Thread") as MockThread:
        controller.on_type_confirm()
        MockThread.assert_called_once()
        # You could introspect the target of the thread if needed,
        # but verifying the thread creation is usually sufficient for this level.


def test_on_improve_text(mock_dependencies):
    """Test AI improvement trigger."""
    controller = WhisperAppController()
    controller.config = DEFAULT_CONFIG.copy()
    controller.config["gemini_api_key"] = "fake"
    controller.initialize_components()
    mock_improver = controller.improver

    controller.pending_text = "Bad text"

    with patch("threading.Thread") as MockThread:
        controller.on_improve_text()
        MockThread.assert_called_once()
