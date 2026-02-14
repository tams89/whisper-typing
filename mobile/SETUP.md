# Mobile App Setup Instructions

This guide walks you through setting up the Flutter mobile app from scratch.

## Prerequisites

Before you begin, ensure you have:

1. **Flutter SDK** (3.16.0+): https://docs.flutter.dev/get-started/install
2. **Android Studio**: https://developer.android.com/studio
3. **Android SDK** (API 21+)
4. **Protocol Buffer Compiler** (`protoc`): https://github.com/protocolbuffers/protobuf/releases
5. **Dart protoc plugin**: Install with `dart pub global activate protoc_plugin`

## Step-by-Step Setup

### 1. Initialize Flutter Project

The basic project structure is already created. Run Flutter's init to complete setup:

```bash
cd mobile

# If starting fresh, you can create the project with:
# flutter create --org com.whispertyping --project-name whisper_typing_mobile .

# Or just install dependencies from pubspec.yaml:
flutter pub get
```

### 2. Generate Protocol Buffer Code

Generate Dart classes from the `.proto` files:

**On Windows:**
```powershell
.\generate_proto.ps1
```

**On Linux/macOS:**
```bash
chmod +x generate_proto.sh
./generate_proto.sh
```

This will create Dart gRPC client code in `lib/generated/`.

### 3. Update gRPC Service

After generating proto code, update `lib/services/grpc_service.dart`:

1. Uncomment the import statements at the top
2. Uncomment the actual gRPC implementation code
3. Remove the mock implementations

### 4. Configure Android

The Android configuration is already set up with:
- Required permissions (RECORD_AUDIO, INTERNET, WAKE_LOCK)
- Minimum SDK 21
- Target SDK 34

No additional Android configuration needed!

### 5. Run the App

**On connected Android device:**
```bash
flutter devices  # List available devices
flutter run
```

**Build APK for distribution:**
```bash
flutter build apk --release
```

## Project Structure

```
mobile/
├── android/                    # Android-specific config
│   └── app/
│       └── src/main/
│           └── AndroidManifest.xml  # Permissions & app config
├── lib/
│   ├── main.dart              # App entry point
│   ├── screens/               # UI screens
│   │   ├── home_screen.dart       # Main recording screen
│   │   └── settings_screen.dart   # Backend configuration
│   ├── services/              # Business logic
│   │   ├── grpc_service.dart      # gRPC client
│   │   └── audio_service.dart     # Audio recording
│   └── generated/             # Generated proto code (after running script)
├── proto/                     # Protocol buffer definitions
│   ├── transcription.proto
│   ├── config.proto
│   └── health.proto
├── pubspec.yaml               # Dependencies
├── generate_proto.sh          # Proto code generation (Linux/macOS)
└── generate_proto.ps1         # Proto code generation (Windows)
```

## Dependencies

Key packages used:

| Package | Purpose |
|---------|---------|
| `grpc` | gRPC client for Dart |
| `protobuf` | Protocol Buffer support |
| `record` | Audio recording |
| `permission_handler` | Runtime permissions |
| `provider` | State management |
| `shared_preferences` | Settings storage |

## Connecting to Backend

1. Start the backend Docker container on your desktop PC
2. Get your Tailscale IP: `tailscale ip -4`
3. Open the mobile app
4. Go to Settings (gear icon)
5. Enter your Tailscale IP and port 50051
6. Tap "Save & Connect"
7. Test the connection

## Usage

1. **Start Recording**: Press and hold the microphone button
2. **Stop Recording**: Release the button
3. **View Transcription**: Text appears in the display area
4. **Copy Text**: Tap the "Copy" button
5. **Clear Text**: Tap the "Clear" button

## Troubleshooting

### Flutter not found
```bash
# Add Flutter to PATH
export PATH="$PATH:/path/to/flutter/bin"  # Linux/macOS
# OR
setx PATH "%PATH%;C:\src\flutter\bin"     # Windows
```

### protoc not found
Download from: https://github.com/protocolbuffers/protobuf/releases
Extract and add `protoc.exe` to your PATH.

### protoc-gen-dart not found
```bash
# Install the plugin
dart pub global activate protoc_plugin

# Add Dart pub cache to PATH
export PATH="$PATH:$HOME/.pub-cache/bin"  # Linux/macOS
# OR
setx PATH "%PATH%;%APPDATA%\Pub\Cache\bin"  # Windows
```

### Permission denied on Android
The app will request microphone permission on first use. If denied, enable it manually:
- Settings > Apps > Whisper Typing > Permissions > Microphone

### Cannot connect to backend
- Verify backend is running: `docker-compose ps`
- Check Tailscale IP: `tailscale ip -4`
- Ensure both devices are on same Tailscale network
- Test backend health: `curl http://<tailscale-ip>:50051`

### Audio recording fails
- Ensure microphone permission is granted
- Check device has a working microphone
- Try restarting the app

## Development

### Hot Reload
Flutter supports hot reload for rapid development:
```bash
# While app is running, press 'r' for hot reload
# Or press 'R' for hot restart
```

### Debugging
```bash
# Run with verbose logging
flutter run -v

# View logs
flutter logs
```

### Testing
```bash
# Run unit tests
flutter test

# Run with coverage
flutter test --coverage
```

## Next Steps

- Implement text improvement feature (Gemini integration)
- Add transcription history persistence
- Add share functionality
- Implement iOS support
- Add dark mode toggle

## Resources

- [Flutter Documentation](https://docs.flutter.dev/)
- [gRPC Dart Guide](https://grpc.io/docs/languages/dart/)
- [Protocol Buffers Dart](https://pub.dev/packages/protobuf)
- [Whisper-Typing Backend Docs](../BACKEND_IMPLEMENTATION.md)
