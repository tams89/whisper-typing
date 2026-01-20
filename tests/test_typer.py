"""Tests for typer module."""

import threading
from unittest.mock import MagicMock, call, patch

from whisper_typing.typer import Typer


def test_typer_initialization() -> None:
    """Test Typer initialization with default and custom WPM."""
    typer = Typer()
    assert typer.wpm == 40
    
    typer_fast = Typer(wpm=100)
    assert typer_fast.wpm == 100


@patch("whisper_typing.typer.Controller")
@patch("time.sleep")
def test_type_text_basic(mock_sleep: MagicMock, mock_controller_cls: MagicMock) -> None:
    """Test typing text calls the keyboard controller correctly."""
    mock_keyboard = MagicMock()
    mock_controller_cls.return_value = mock_keyboard
    
    typer = Typer(wpm=60)
    text = "Hello"
    typer.type_text(text)
    
    assert mock_keyboard.type.call_count == len(text)
    mock_keyboard.type.assert_has_calls([call(char) for char in text])
    assert mock_sleep.called


@patch("whisper_typing.typer.Controller")
@patch("time.sleep")
def test_type_text_stop_event(mock_sleep: MagicMock, mock_controller_cls: MagicMock) -> None:
    """Test typing stops when stop_event is set."""
    mock_keyboard = MagicMock()
    mock_controller_cls.return_value = mock_keyboard
    
    typer = Typer(wpm=60)
    stop_event = threading.Event()
    
    # Set stop event immediately
    stop_event.set()
    typer.type_text("Hello", stop_event=stop_event)
    
    mock_keyboard.type.assert_not_called()


@patch("whisper_typing.typer.Controller")
@patch("time.sleep")
def test_type_text_check_focus_failure(mock_sleep: MagicMock, mock_controller_cls: MagicMock) -> None:
    """Test typing stops when check_focus returns False."""
    mock_keyboard = MagicMock()
    mock_controller_cls.return_value = mock_keyboard
    
    typer = Typer(wpm=60)
    
    # check_focus simply returns False
    typer.type_text("Hello", check_focus=lambda: False)
    
    mock_keyboard.type.assert_not_called()
