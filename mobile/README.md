# Flutter Mobile App Setup Guide

This guide explains how to set up and run the Flutter mobile app for whisper-typing.

## Prerequisites

1. **Flutter SDK** (3.16.0 or later)
   - Download from: https://docs.flutter.dev/get-started/install
   - Add Flutter to your PATH

2. **Android Studio** (for Android development)
   - Download from: https://developer.android.com/studio
   - Install Android SDK (API level 21 or higher)

3. **Android Device or Emulator**
   - Physical device with USB debugging enabled, OR
   - Android emulator configured in Android Studio

## Quick Setup

### 1. Install Flutter

Run `flutter doctor` to check installation. If Flutter is not installed:

**Windows:**
```powershell
# Download Flutter SDK from https://docs.flutter.dev/get-started/install/windows
# Extract to C:\src\flutter
# Add to PATH: C:\src\flutter\bin
flutter doctor
```

### 2. Initialize Flutter Project

From this directory (`mobile/`):

```bash
flutter create --org com.whispertyping --project-name whisper_typing_mobile .
```

### 3. Install Dependencies

```bash
flutter pub get
```

### 4. Run the App

```bash
flutter run
```

## Project Structure

After initialization:

```
mobile/
├── android/          # Android config
├── lib/              # Dart code
│   ├── main.dart     # Entry point
│   ├── screens/      # UI screens
│   ├── services/     # gRPC clients
│   └── models/       # Data models
├── proto/            # Protocol buffers
└── pubspec.yaml      # Dependencies
```

## Troubleshooting

```bash
flutter doctor        # Check installation
flutter devices       # List connected devices
flutter clean         # Clean build cache
```

## Resources

- [Flutter Docs](https://docs.flutter.dev/)
- [Dart Language](https://dart.dev/)
- [gRPC Dart](https://grpc.io/docs/languages/dart/)
