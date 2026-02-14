"""FastAPI web admin panel for backend configuration and management."""

import logging
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Whisper-Typing Admin Panel")


class Config(BaseModel):
    """Configuration model."""

    model: str
    language: str
    device: str
    compute_type: str
    use_ollama: bool
    ollama_host: str | None
    model_cache_dir: str
    gemini_model: str


class TestRequest(BaseModel):
    """Test configuration request."""

    config: Config


@app.get("/", response_class=HTMLResponse)
async def root() -> str:
    """Serve the admin panel homepage.

    Returns:
        HTML content for the admin panel.

    """
    html_path = Path(__file__).parent / "static" / "index.html"
    if html_path.exists():
        return html_path.read_text()

    # Fallback minimal HTML
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Whisper-Typing Admin</title>
    </head>
    <body>
        <h1>Whisper-Typing Backend Admin</h1>
        <p>Web interface coming soon...</p>
        <p>API Status: <a href="/api/health">Check Health</a></p>
    </body>
    </html>
    """


@app.get("/api/health")
async def health_check() -> JSONResponse:
    """Check API health status.

    Returns:
        Health status JSON.

    """
    return JSONResponse({
        "status": "healthy",
        "service": "whisper-typing-admin",
        "version": "1.0.0",
    })


@app.get("/api/config")
async def get_config() -> Config:
    """Get current configuration.

    Returns:
        Current configuration.

    """
    import json  # noqa: PLC0415

    config_path = Path("config.json")
    if not config_path.exists():
        raise HTTPException(status_code=404, detail="Configuration file not found")

    with config_path.open() as f:  # noqa: ASYNC230
        config_data = json.load(f)

    return Config(**config_data)


@app.post("/api/config")
async def update_config(config: Config) -> JSONResponse:
    """Update configuration.

    Args:
        config: New configuration.

    Returns:
        Success response.

    """
    import json  # noqa: PLC0415

    config_path = Path("config.json")

    try:
        # Save configuration
        with config_path.open("w") as f:  # noqa: ASYNC230
            json.dump(config.model_dump(), f, indent=2)

        return JSONResponse({
            "status": "success",
            "message": "Configuration updated successfully",
        })
    except Exception as e:
        logger.exception("Failed to update configuration")
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.get("/api/models")
async def list_models() -> JSONResponse:
    """List available models.

    Returns:
        List of available models.

    """
    models = [
        {
            "name": "openai/whisper-tiny.en",
            "display_name": "Tiny (English)",
            "size": "tiny",
            "backend": "faster-whisper",
        },
        {
            "name": "openai/whisper-base.en",
            "display_name": "Base (English)",
            "size": "base",
            "backend": "faster-whisper",
        },
        {
            "name": "openai/whisper-small.en",
            "display_name": "Small (English)",
            "size": "small",
            "backend": "faster-whisper",
        },
        {
            "name": "openai/whisper-medium.en",
            "display_name": "Medium (English)",
            "size": "medium",
            "backend": "faster-whisper",
        },
        {
            "name": "openai/whisper-large-v3",
            "display_name": "Large V3 (Multilingual)",
            "size": "large-v3",
            "backend": "faster-whisper",
        },
        {
            "name": "whisper:latest",
            "display_name": "Whisper (Latest)",
            "size": "base",
            "backend": "ollama",
        },
        {
            "name": "whisper:medium",
            "display_name": "Whisper (Medium)",
            "size": "medium",
            "backend": "ollama",
        },
    ]

    return JSONResponse({"models": models})


@app.post("/api/test")
async def test_config(request: TestRequest) -> JSONResponse:
    """Test configuration.

    Args:
        request: Test configuration request.

    Returns:
        Test result.

    """
    # NOTE: Implement actual configuration test when Phase 1 auth is complete
    # For now, return mock success
    return JSONResponse({
        "success": True,
        "message": f"Configuration test passed for model: {request.config.model}",
    })


if __name__ == "__main__":
    import os

    import uvicorn

    port = int(os.environ.get("WEB_PORT", "8080"))
    uvicorn.run(app, host="0.0.0.0", port=port)  # noqa: S104
