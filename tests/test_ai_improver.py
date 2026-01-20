"""Tests for ai_improver module."""

from unittest.mock import MagicMock, patch

from whisper_typing.ai_improver import AIImprover


@patch("google.genai.Client")
def test_initialization(mock_client_cls: MagicMock) -> None:
    """Test AIImprover initialization."""
    improver = AIImprover(api_key="fake-key")
    mock_client_cls.assert_called_with(api_key="fake-key")
    assert improver.client is not None


def test_initialization_no_key() -> None:
    """Test initialization without API key disables client."""
    improver = AIImprover(api_key="")
    assert improver.client is None


@patch("google.genai.Client")
def test_list_models(mock_client_cls: MagicMock) -> None:
    """Test listing models."""
    mock_client = mock_client_cls.return_value

    Model1 = MagicMock()
    Model1.name = "models/gemini-pro"
    Model1.supported_actions = ["generateContent"]

    Model2 = MagicMock()
    Model2.name = "models/embedding-001"
    Model2.supported_actions = ["embedContent"]  # Should filter out

    mock_client.models.list.return_value = [Model1, Model2]

    models = AIImprover.list_models(api_key="fake")
    assert "models/gemini-pro" in models
    assert "models/embedding-001" not in models


@patch("google.genai.Client")
def test_improve_text_success(mock_client_cls: MagicMock) -> None:
    """Test successful text improvement."""
    mock_client = mock_client_cls.return_value
    mock_response = MagicMock()
    mock_response.text = "Improved text"
    mock_client.models.generate_content.return_value = mock_response

    improver = AIImprover(api_key="fake")
    result = improver.improve_text("Bad text")

    assert result == "Improved text"
    mock_client.models.generate_content.assert_called()


def test_improve_text_no_client() -> None:
    """Test improve_text returns original text if no client."""
    improver = AIImprover(api_key="")
    assert improver.improve_text("Original") == "Original"
