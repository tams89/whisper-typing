import 'dart:io';
import 'dart:typed_data';
import 'package:flutter/foundation.dart';
import 'package:record/record.dart';
import 'package:permission_handler/permission_handler.dart';
import 'package:path_provider/path_provider.dart';

class AudioService extends ChangeNotifier {
  final AudioRecorder _recorder = AudioRecorder();
  bool _isRecording = false;
  String? _recordingPath;

  bool get isRecording => _isRecording;

  Future<bool> requestPermission() async {
    final status = await Permission.microphone.request();
    return status.isGranted;
  }

  Future<bool> checkPermission() async {
    final status = await Permission.microphone.status;
    return status.isGranted;
  }

  Future<void> startRecording() async {
    try {
      // Check permission first
      final hasPermission = await checkPermission();
      if (!hasPermission) {
        final granted = await requestPermission();
        if (!granted) {
          throw Exception('Microphone permission denied');
        }
      }

      // Check if device supports recording
      if (!await _recorder.hasPermission()) {
        throw Exception('Recording permission not granted');
      }

      // Get temporary directory for recording
      final tempDir = await getTemporaryDirectory();
      final timestamp = DateTime.now().millisecondsSinceEpoch;
      _recordingPath = '${tempDir.path}/recording_$timestamp.wav';

      // Start recording to file
      await _recorder.start(
        const RecordConfig(
          encoder: AudioEncoder.wav,
          sampleRate: 16000,
          numChannels: 1,
          bitRate: 128000,
        ),
        path: _recordingPath!,
      );

      _isRecording = true;
      notifyListeners();
      debugPrint('Recording started: $_recordingPath');
    } catch (e) {
      debugPrint('Failed to start recording: $e');
      _isRecording = false;
      notifyListeners();
      rethrow;
    }
  }

  Future<Uint8List?> stopRecording() async {
    try {
      if (!_isRecording) {
        return null;
      }

      final path = await _recorder.stop();
      _isRecording = false;
      notifyListeners();

      if (path == null) {
        debugPrint('No recording path returned');
        return null;
      }

      _recordingPath = path;
      debugPrint('Recording stopped: $path');

      // Read the audio file and return bytes
      final file = File(path);
      if (await file.exists()) {
        final bytes = await file.readAsBytes();
        debugPrint('Audio file read: ${bytes.length} bytes');
        
        // Clean up the file after reading
        await file.delete();
        
        return bytes;
      } else {
        debugPrint('Recording file does not exist: $path');
        return null;
      }
    } catch (e) {
      debugPrint('Failed to stop recording: $e');
      _isRecording = false;
      notifyListeners();
      return null;
    }
  }

  Future<void> cancelRecording() async {
    try {
      await _recorder.cancel();
      _isRecording = false;
      _recordingPath = null;
      notifyListeners();
      debugPrint('Recording cancelled');
      
      // Clean up file if it exists
      if (_recordingPath != null) {
        final file = File(_recordingPath!);
        if (await file.exists()) {
          await file.delete();
        }
      }
    } catch (e) {
      debugPrint('Failed to cancel recording: $e');
    }
  }

  @override
  void dispose() {
    _recorder.dispose();
    super.dispose();
  }
}
