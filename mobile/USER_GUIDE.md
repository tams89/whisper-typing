# Whisper-Typing Mobile App - User Guide

Complete guide for using the Whisper-Typing mobile app on Android.

## Table of Contents

1. [Introduction](#introduction)
2. [Requirements](#requirements)
3. [Installation](#installation)
4. [First-Time Setup](#first-time-setup)
5. [Using the App](#using-the-app)
6. [Settings](#settings)
7. [Tips & Best Practices](#tips--best-practices)
8. [Troubleshooting](#troubleshooting)
9. [FAQ](#faq)

## Introduction

Whisper-Typing Mobile is a privacy-focused speech-to-text app that connects to your self-hosted backend server. Unlike cloud-based services, your audio never leaves your private network - it's transcribed on your own hardware using state-of-the-art AI models.

### Key Features

✨ **Private & Secure** - All processing happens on your server  
🎯 **High Accuracy** - Powered by OpenAI's Whisper model  
⚡ **Real-Time** - Fast transcription with GPU acceleration  
📝 **AI Improvement** - Enhance text with Gemini AI  
📱 **Simple Interface** - Push-to-talk recording  
📜 **History** - Access previous transcriptions

## Requirements

### Backend Server
- Desktop PC with:
  - Docker installed
  - NVIDIA GPU (recommended) or CPU
  - Tailscale for secure networking
- Running the whisper-typing backend

### Mobile Device
- Android 5.0 (API 21) or higher
- Microphone access
- Internet connection (WiFi or mobile data)
- Tailscale app installed (for secure connection)

## Installation

### Step 1: Install Tailscale

1. Install Tailscale on your Android device from Google Play Store
2. Install Tailscale on your desktop PC
3. Sign in to the same Tailscale account on both devices
4. Note your desktop PC's Tailscale IP address

### Step 2: Set Up Backend Server

Follow the backend setup guide in `DOCKER.md`:

```bash
# On your desktop PC
git clone https://github.com/rpfilomeno/whispher-typing.git
cd whispher-typing
docker-compose up -d
```

### Step 3: Install Mobile App

**Option A: Build from source**
```bash
cd mobile
flutter build apk --release
# Install dist/app-release.apk on your device
```

**Option B: Install pre-built APK** (if available)
Download the APK from GitHub releases and install it.

## First-Time Setup

### Welcome Screen

When you first open the app, you'll see a welcome screen with an overview of features. Tap "Next" to continue.

### Grant Microphone Permission

The app needs microphone access to record your voice:

1. Tap "Grant Permission"
2. When Android asks, tap "Allow"
3. If you accidentally deny, you can grant it later in Android Settings

### Connect to Backend

Enter your backend server details:

1. **Host**: Enter your desktop PC's Tailscale IP
   - Example: `100.64.1.5`
   - Or hostname: `my-desktop.tailnet-abc.ts.net`

2. **Port**: Keep default `50051` (unless you changed it)

3. Tap "Test Connection" to verify it works

4. If successful, tap "Next"

### Complete Setup

Review the setup summary and tap "Get Started" to begin using the app!

## Using the App

### Home Screen

The home screen is your main interface:

- **Connection Status** - Shows if backend is reachable
- **Transcription Area** - Displays your text
- **Microphone Button** - Press and hold to record
- **Action Buttons** - Copy, improve, or clear text
- **History Icon** - View previous transcriptions
- **Settings Icon** - Configure the app

### Recording Audio

**Push-to-Talk Method:**

1. Press and hold the large circular microphone button
2. Speak clearly into your phone's microphone
3. Release the button when finished
4. Wait for transcription (usually 1-3 seconds)

**Tips for Best Results:**
- Speak at a normal pace
- Minimize background noise
- Hold phone 6-12 inches from mouth
- Speak in complete sentences

### Viewing Transcription

After recording:
- Text appears in the transcription area
- Transcription is automatically saved to history
- You can immediately start another recording

### Copying Text

To use your transcribed text:

1. Tap the "Copy" button
2. Success message confirms copy
3. Paste into any app (Messages, Notes, Email, etc.)

### Improving Text

Use AI to enhance your transcription:

1. Tap the "Improve" button (magic wand icon)
2. Wait for AI processing (2-5 seconds)
3. Improved text replaces original
4. Grammar, punctuation, and clarity enhanced

*Note: Requires Gemini API key configured in backend*

### Viewing History

Access previous transcriptions:

1. Tap the history icon (clock) in the app bar
2. Scroll through recent transcriptions
3. Tap any item to load it into the main area
4. History is available until you close the app

*Note: History is currently session-only (not persisted)*

### Clearing Text

To start fresh:
1. Tap the "Clear" button
2. Transcription area empties immediately

## Settings

Access settings by tapping the gear icon:

### Backend Server

- **Host / IP Address**: Your backend server location
- **Port**: gRPC port (default 50051)
- **Save & Connect**: Apply changes and reconnect
- **Test Connection**: Verify backend is reachable

### Connection Status

Shows current connection state:
- **Connected** (green) - Ready to transcribe
- **Disconnected** (red) - Check settings or backend

### About

View app version and information

## Tips & Best Practices

### For Better Accuracy

1. **Speak Naturally** - Don't over-enunciate or slow down
2. **Quiet Environment** - Reduce background noise
3. **Good Model** - Use `base.en` or `small.en` for English
4. **Stable Connection** - Ensure good WiFi/data signal

### For Faster Transcription

1. **GPU Backend** - Use CUDA acceleration on backend
2. **Smaller Model** - `tiny.en` is fastest
3. **Shorter Clips** - 5-15 seconds ideal
4. **Tailscale** - Lower latency than VPN

### For Privacy

1. **Use Tailscale** - End-to-end encrypted
2. **Self-Host Backend** - Your data never leaves your network
3. **No Cloud** - Unlike Siri/Google Assistant
4. **Open Source** - Inspect the code yourself

### For Battery Life

1. **WiFi Preferred** - Uses less power than mobile data
2. **Close When Done** - Don't leave app running
3. **Airplane Mode** - Use with Tailscale on WiFi only

## Troubleshooting

### Connection Issues

**Problem:** "Not connected" status

**Solutions:**
1. Verify backend is running: `docker-compose ps`
2. Check Tailscale is active on both devices
3. Ping backend: `ping <tailscale-ip>`
4. Ensure firewall allows port 50051
5. Try restarting Tailscale on both devices

### Recording Issues

**Problem:** "Permission denied" error

**Solutions:**
1. Go to Android Settings > Apps > Whisper Typing
2. Tap Permissions > Microphone
3. Select "Allow"
4. Restart the app

**Problem:** No audio captured

**Solutions:**
1. Test mic in another app (Voice Recorder)
2. Check for mic hardware issues
3. Close other apps using microphone
4. Restart device

### Transcription Issues

**Problem:** Empty or incorrect transcription

**Solutions:**
1. Speak louder and clearer
2. Reduce background noise
3. Try different microphone position
4. Check audio quality in recording app first
5. Use larger model (small.en or medium.en)

**Problem:** Slow transcription

**Solutions:**
1. Check backend is using GPU (not CPU)
2. Use smaller model (tiny.en or base.en)
3. Record shorter clips
4. Check network latency
5. Restart backend container

### App Crashes

**Problem:** App crashes during use

**Solutions:**
1. Update to latest version
2. Clear app cache: Settings > Apps > Whisper Typing > Storage > Clear Cache
3. Reinstall app
4. Check Android logs: `adb logcat`

## FAQ

### Q: Is my voice data sent to the cloud?
**A:** No! All audio is processed on your private backend server over Tailscale. Nothing goes to external servers.

### Q: What languages are supported?
**A:** Whisper supports 90+ languages. Configure the model in your backend (e.g., `whisper-large-v3` for multilingual).

### Q: Can I use this without Tailscale?
**A:** Yes, but it's not recommended. You could use direct IP, but Tailscale provides encryption and easy NAT traversal.

### Q: Does it work offline?
**A:** No, it requires network connection to your backend server. The backend itself works offline.

### Q: How accurate is the transcription?
**A:** With the `base.en` model and clear speech, expect >90% accuracy. Larger models (small, medium, large) are even better.

### Q: Can I use this while driving?
**A:** Use caution. While hands-free, it may be distracting. Follow local laws regarding phone use while driving.

### Q: Why is it slower than Siri/Google?
**A:** Cloud services have massive server farms. Your transcription runs on your PC. With a good GPU, it's still very fast (<3s).

### Q: Can I improve transcription quality?
**A:** Yes! Use a larger model (configure in backend), speak clearly, reduce background noise, and use the "Improve" feature.

### Q: Is there an iOS version?
**A:** Not yet, but it's planned! Flutter supports iOS, so it's technically feasible.

### Q: Can multiple people use the same backend?
**A:** Yes, but currently there's no user authentication. Everyone on your Tailscale network can access it.

### Q: How do I update the app?
**A:** Download the new APK and install over the existing app. Your settings will be preserved.

## Support

- **GitHub Issues**: https://github.com/rpfilomeno/whispher-typing/issues
- **Documentation**: See README.md and BACKEND_IMPLEMENTATION.md
- **Backend Guide**: See DOCKER.md

## Version History

### v1.0.0 (Current)
- Initial release
- Push-to-talk recording
- Real-time transcription
- Text improvement with Gemini
- Transcription history
- Onboarding wizard
- Tailscale support
- Android 5.0+ support

## License

MIT License - See LICENSE file

---

**Thank you for using Whisper-Typing! 🎤✨**

For backend setup, see `DOCKER.md`  
For development, see `SETUP.md`  
For testing, see `TESTING.md`
