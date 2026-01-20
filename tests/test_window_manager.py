"""Tests for window_manager module."""

from unittest.mock import MagicMock, patch

from whisper_typing.window_manager import WindowManager


def test_get_active_window() -> None:
    """Test retrieving the active window."""
    with patch("pygetwindow.getActiveWindow") as mock_get_active:
        mock_window = MagicMock()
        mock_get_active.return_value = mock_window
        wm = WindowManager()
        assert wm.get_active_window() == mock_window


def test_focus_window_success() -> None:
    """Test successfully focusing a window."""
    wm = WindowManager()
    mock_window = MagicMock()
    mock_window.isActive = False

    # Simulate successful activation
    mock_window.activate.return_value = None

    assert wm.focus_window(mock_window) is True
    mock_window.activate.assert_called_once()


def test_focus_window_failure() -> None:
    """Test failure when focusing a window."""
    wm = WindowManager()
    mock_window = MagicMock()
    mock_window.isActive = False

    # Simulate exception during activation
    mock_window.activate.side_effect = Exception("Focus error")

    assert wm.focus_window(mock_window) is False
