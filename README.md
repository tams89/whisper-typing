# Whisper Typing

![whiisper](https://github.com/user-attachments/assets/8bbd34ac-38d2-481e-9356-06e9f4498f0e)

A powerful, human-like background speech-to-text application for Windows that runs locally. It listens for a global hotkey to record your voice, transcribes it in real-time using `faster-whisper` or `Ollama`, and types the result into your active window with natural rhythm and pace.

## Features

- **Real-Time Transcription**: See your words appear in the preview area instantly as you speak.
- **Human-like Typing**: Simulates natural typing with variable speed, random jitter, and intelligent pauses after punctuation.
- **Global Hotkeys**: Control recording and typing from any application.
  - **Record/Stop**: `F8` (default)
  - **Confirm Type**: `F9` (default)
  - **Improve Text**: `F10` (default) - Uses Gemini AI to fix grammar and refine text.
- **Window Refocus**: Automatically switches back to your target window after recording stops (configurable).
- **Safe Focus**: Automatically stops typing if you switch away from the target window.
- **Secure Storage**: Sensitive API keys (Gemini) are stored safely in a local `.env` file.
- **TUI Management**: A sleek terminal interface for monitoring logs, previewing text, and configuring settings.
- **Microphone Selection**: Choose your preferred input device directly from the configuration screen.
- **Multiple Transcription Backends**: Choose between `faster-whisper` (with CUDA acceleration) or `Ollama` for local model inference.
- **Local Processing**: Audio is processed locally using `faster-whisper` (accelerated with CUDA if available) or via Ollama server.

## Prerequisites

- **Python 3.13+**
- **NVIDIA GPU (Recommended)**: Supports CUDA for lightning-fast transcription with `faster-whisper`. Fallback to CPU is supported but slower.
- **Ollama (Optional)**: For using Ollama as the transcription backend. [Install Ollama](https://ollama.ai)

## Installation

This project uses `uv` for dependency management.

1. **Clone the repository**:
   ```bash
   git clone https://github.com/rpfilomeno/whispher-typing.git
   cd whispher-typing
   ```

2. **Install dependencies**:
   ```bash
   uv sync
   ```

## Usage

Run the application using `uv`:

```bash
uv run whisper-typing
```

## Build EXE

Build a Windows executable application:

```bash
build_dist.ps1
```

### TUI Shortcuts

Inside the application, you can use these keys:

- **`c`**: Open Configuration screen.
- **`p`**: Pause/Resume hotkeys.
- **`r`**: Reload configuration.
- **`q`**: Quit the application.

### Workflow

1. **Start Recording**: Press **F8**. You will see "Recording" in the status bar.
2. **Speak**: You will see transcribed text appear in the **Preview Area** in real-time.
3. **Stop**: Press **F8** again. If enabled, the application will automatically refocus the window you were in before recording.
4. **Confirm Type**: Switch to your target application (e.g., Notepad, Slack) and press **F9**. The text will be typed out with human-like timing.
5. **Improve (Optional)**: Press **F10** before typing to have Gemini AI refine your transcription.

## Configuration

You can customize the application via the UI (press `c`) or by editing local files.

### Secure API Keys

The Gemini API key is stored in a `.env` file. You can enter it through the UI on first run or by editing the file:

```env
GEMINI_API_KEY=your_key_here
```

### JSON Configuration (`config.json`)

Other settings are stored in `config.json`:

```json
{
  "hotkey": "<f8>",
  "type_hotkey": "<f9>",
  "improve_hotkey": "<f10>",
  "model": "openai/whisper-base.en",
  "language": "en",
  "device": "cpu",
  "compute_type": "auto",
  "typing_wpm": 350,
  "refocus_window": false,
  "microphone_name": "Default System Mic",
  "gemini_model": "models/gemini-2.0-flash",
  "model_cache_dir": "./models/",
  "use_ollama": false,
  "ollama_host": null
}
```

## Using Ollama

Ollama provides an alternative transcription backend that can be easier to set up and use with local models.

### Setup Ollama

1. **Install Ollama**: Download and install from [ollama.ai](https://ollama.ai)

2. **Pull a Whisper model**:
   ```bash
   ollama pull whisper
   ```

3. **Configure whisper-typing** to use Ollama by editing `config.json`:
   ```json
   {
     "use_ollama": true,
     "model": "whisper:latest"
   }
   ```

### Ollama Configuration Options

- **`use_ollama`**: Set to `true` to enable Ollama transcription backend
- **`model`**: Ollama model name (e.g., `whisper:latest`, `whisper:medium`, `whisper:large`)
- **`ollama_host`**: Optional custom Ollama server URL (default: `http://localhost:11434`)

### Example: Using Ollama with Custom Host

```json
{
  "use_ollama": true,
  "model": "whisper:medium",
  "ollama_host": "http://192.168.1.100:11434"
}
```

### Benefits of Ollama

- **Easy Installation**: Simple one-command model downloads
- **Model Management**: Easy switching between different Whisper model sizes
- **Remote Inference**: Can connect to Ollama running on another machine
- **Cross-Platform**: Works consistently across Windows, Linux, and macOS

## Model Storage

By default, Whisper models are downloaded and stored in the Hugging Face cache directory:

- **Windows**: `%USERPROFILE%\.cache\huggingface\hub`
- **Linux/macOS**: `~/.cache/huggingface/hub`

### Changing the Storage Location

You can change where models are stored in three ways:

1. **Configuration Screen**: Press `c` in the app and set the **Model Cache Dir**.
2. **JSON Config**: Manually add or edit the `"model_cache_dir"` field in `config.json`.
3. **Environment Variable**: Set the `HF_HOME` environment variable on your system.

## Troubleshooting

- **Slow Transcription**: 
  - For `faster-whisper`: Check the logs to see if "cuda" or "cpu" is being used. You can change this in the Configuration screen.
  - For `Ollama`: Ensure Ollama is running (`ollama serve`) and the model is downloaded.
- **Hotkeys not working**: Ensure no other application is capturing the same keys.
- **Microphone Issues**: Ensure the correct microphone is selected in the Configuration screen (`c`).
- **Ollama Connection Error**: Verify Ollama is running and accessible at the configured `ollama_host` URL.
