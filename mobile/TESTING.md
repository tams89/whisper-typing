# Testing Guide - Whisper-Typing Mobile App

This guide provides comprehensive testing procedures for the complete whisper-typing system.

## Test Environment Setup

### Backend Setup

1. **Start the Docker backend:**
   ```bash
   cd whispher-typing
   docker-compose up -d
   ```

2. **Verify backend is running:**
   ```bash
   docker-compose ps
   curl http://localhost:8080/api/health
   ```

3. **Get Tailscale IP:**
   ```bash
   tailscale ip -4
   # Example output: 100.64.1.5
   ```

### Mobile App Setup

1. **Install dependencies:**
   ```bash
   cd mobile
   flutter pub get
   ```

2. **Generate proto code:**
   ```powershell
   # Windows
   .\generate_proto.ps1
   
   # Linux/macOS
   ./generate_proto.sh
   ```

3. **Connect Android device or start emulator:**
   ```bash
   flutter devices
   ```

4. **Run the app:**
   ```bash
   flutter run
   ```

## Test Cases

### Phase 1: Backend API Tests

#### Test 1.1: gRPC Server Health
```bash
# Using grpcurl (install from: https://github.com/fullstorydev/grpcurl)
grpcurl -plaintext localhost:50051 whisper_typing.HealthService/Check
```

**Expected:** Status HEALTHY response

#### Test 1.2: Configuration API
```bash
curl http://localhost:8080/api/config
```

**Expected:** JSON with current configuration

#### Test 1.3: Models List
```bash
curl http://localhost:8080/api/models
```

**Expected:** List of available Whisper models

### Phase 2: Docker Tests

#### Test 2.1: Container Build
```bash
docker-compose build
```

**Expected:** Successful build without errors

#### Test 2.2: GPU Passthrough
```bash
docker-compose exec whisper-typing-backend nvidia-smi
```

**Expected:** GPU information displayed (if GPU available)

#### Test 2.3: Volume Persistence
```bash
# Stop and start container
docker-compose down
docker-compose up -d

# Check if config persists
curl http://localhost:8080/api/config
```

**Expected:** Configuration unchanged after restart

### Phase 3: Web Admin Panel Tests

#### Test 3.1: Web UI Access
```
Navigate to: http://localhost:8080
```

**Expected:** Admin panel loads successfully

#### Test 3.2: Configuration Save
1. Change model to "openai/whisper-small.en"
2. Click "Save Configuration"
3. Refresh page

**Expected:** Changes persist after refresh

#### Test 3.3: Connection Test
1. Click "Test Configuration"

**Expected:** "Configuration test passed!" message

### Phase 4-6: Mobile App Tests

#### Test 4.1: First Launch (Onboarding)
1. Install app on fresh device/emulator
2. Launch app

**Expected:**
- Splash screen appears (2 seconds)
- Welcome screen with features list
- Can navigate through all 4 pages
- Page indicators work correctly

#### Test 4.2: Permission Handling
1. On permissions page, click "Grant Permission"

**Expected:**
- Android permission dialog appears
- After granting, success snackbar appears

#### Test 4.3: Backend Connection
1. On connection page, enter Tailscale IP
2. Click "Test Connection"

**Expected:**
- Loading indicator appears
- Success message after connection
- Auto-advances to completion page

#### Test 4.4: Onboarding Completion
1. On completion page, click "Get Started"

**Expected:**
- Navigate to home screen
- On app restart, home screen shows directly (no onboarding)

#### Test 4.5: Connection Status Indicator
1. On home screen, observe connection status

**Expected:**
- Green checkmark if connected
- Red error icon if disconnected
- Status text matches indicator

#### Test 4.6: Audio Recording
1. Hold microphone button
2. Speak a test phrase
3. Release button

**Expected:**
- Button turns red while holding
- "Recording..." text appears
- "Transcribing..." appears after release
- Transcription appears in text area

#### Test 4.7: Transcription Accuracy
Test phrases (expected results):
- "Hello world" → Should transcribe accurately
- "The quick brown fox" → Should transcribe accurately
- "Testing one two three" → Should transcribe accurately

**Expected:** >90% word accuracy for clear speech

#### Test 4.8: Copy to Clipboard
1. After transcription, click "Copy"

**Expected:**
- Success snackbar appears
- Can paste text into another app

#### Test 4.9: Text Improvement
1. After transcription, click "Improve"

**Expected:**
- Loading indicator appears
- Improved text replaces original
- Success message appears

#### Test 4.10: Transcription History
1. Perform multiple transcriptions
2. Click history icon
3. Tap a history item

**Expected:**
- History modal shows all transcriptions
- Tapping item loads it into main area
- Modal closes

#### Test 4.11: Clear Function
1. After transcription, click "Clear"

**Expected:**
- Text area clears immediately
- Action buttons disappear

#### Test 4.12: Settings Configuration
1. Navigate to Settings
2. Change host/port
3. Click "Save & Connect"

**Expected:**
- Success message appears
- Connection status updates
- Settings persist after app restart

#### Test 4.13: Settings Test Connection
1. In settings, click "Test Connection"

**Expected:**
- Loading indicator appears
- Green success message if backend reachable
- Red error message if unreachable

### End-to-End Tests

#### E2E Test 1: Complete Flow
1. Fresh install
2. Complete onboarding
3. Record audio
4. View transcription
5. Copy text
6. Paste in notes app

**Expected:** All steps work seamlessly

#### E2E Test 2: Network Interruption
1. Start recording
2. Disable WiFi/data mid-transcription

**Expected:**
- Error message appears
- Connection status updates to disconnected
- Can reconnect and try again

#### E2E Test 3: Permission Denial Recovery
1. Deny microphone permission
2. Try to record

**Expected:**
- Error message explains need for permission
- Can grant permission from settings
- Recording works after granting

#### E2E Test 4: Long Audio Recording
1. Record 30+ seconds of speech
2. Release and transcribe

**Expected:**
- Recording completes successfully
- Transcription handles long audio
- Result displays correctly

#### E2E Test 5: Multiple Quick Recordings
1. Record 10 short phrases quickly
2. Check history

**Expected:**
- All transcriptions complete
- History shows all items
- No crashes or hangs

### Performance Tests

#### Perf Test 1: Transcription Latency
1. Record 5-second audio clip
2. Measure time from release to transcription display

**Expected:** <3 seconds over Tailscale

#### Perf Test 2: App Memory Usage
1. Monitor RAM usage in Android Studio Profiler
2. Perform 20 transcriptions

**Expected:** Memory stays <200MB, no leaks

#### Perf Test 3: Battery Impact
1. Perform 50 transcriptions over 10 minutes
2. Check battery drain

**Expected:** <5% battery usage

### Security Tests

#### Sec Test 1: Network Traffic
1. Use Wireshark to monitor traffic
2. Perform transcription

**Expected:** All traffic encrypted via Tailscale

#### Sec Test 2: Stored Credentials
1. Check app data directory
2. Look for saved host/port

**Expected:** No sensitive data in plain text

#### Sec Test 3: Permission Scoping
1. Check Android permissions in Settings

**Expected:** Only RECORD_AUDIO, INTERNET, WAKE_LOCK granted

## Test Matrix

| Platform | API 21 | API 28 | API 31 | API 34 |
|----------|--------|--------|--------|--------|
| Physical | ⚠️     | ✅     | ✅     | ✅     |
| Emulator | ✅     | ✅     | ✅     | ✅     |

| Backend | CPU | GPU (CUDA) |
|---------|-----|------------|
| faster-whisper | ✅ | ✅ |
| Ollama | ✅ | ✅ |

## Known Issues & Limitations

1. **iOS Support:** Not yet implemented (Flutter is ready, needs iOS config)
2. **Offline Mode:** No offline transcription (requires backend)
3. **Model Download:** No progress indication in mobile app
4. **History Persistence:** History lost on app restart (no database yet)
5. **Text Improvement:** Requires Gemini API key configuration

## Troubleshooting

### Backend Not Reachable
- Verify Docker container running: `docker-compose ps`
- Check Tailscale connectivity: `ping <tailscale-ip>`
- Verify firewall allows port 50051

### Permission Errors
- Go to Android Settings > Apps > Whisper Typing > Permissions
- Manually grant microphone permission

### Proto Generation Fails
- Ensure `protoc` is installed and in PATH
- Ensure `protoc-gen-dart` is installed: `dart pub global activate protoc_plugin`
- Check PATH includes Dart pub cache: `%APPDATA%\Pub\Cache\bin`

### Audio Recording Fails
- Test with device microphone in other apps
- Check for audio conflicts (other apps using mic)
- Try restarting the app

### Transcription Always Returns Mock Data
- Verify proto code was generated: check `lib/generated/` exists
- Uncomment imports in `grpc_service.dart`
- Rebuild app after proto generation

## Automated Testing

### Unit Tests
```bash
cd mobile
flutter test
```

### Widget Tests
```bash
flutter test test/widgets/
```

### Integration Tests
```bash
flutter test integration_test/
```

## Test Report Template

```
Test Date: ____________________
Tester: ____________________
Device: ____________________
Android Version: ____________________
Backend Version: ____________________

Phase 1: Backend API     [ ] Pass  [ ] Fail
Phase 2: Docker          [ ] Pass  [ ] Fail
Phase 3: Web Admin       [ ] Pass  [ ] Fail
Phase 4: Mobile UI       [ ] Pass  [ ] Fail
Phase 5: Onboarding      [ ] Pass  [ ] Fail
Phase 6: Transcription   [ ] Pass  [ ] Fail
E2E Tests                [ ] Pass  [ ] Fail

Issues Found:
_____________________________________________
_____________________________________________
_____________________________________________

Overall Status: [ ] Ready for Release  [ ] Needs Work
```

## Continuous Integration

For automated testing in CI/CD:

```yaml
# Example GitHub Actions workflow
name: Test
on: [push]
jobs:
  backend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Test backend
        run: uv run pytest
  
  flutter-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: subosito/flutter-action@v2
      - run: cd mobile && flutter test
```

## Next Steps

After all tests pass:
1. Fix any identified issues
2. Document test results
3. Prepare for release (Phase 8)
4. Create release notes
5. Build production APK
