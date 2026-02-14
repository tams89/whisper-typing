import 'dart:typed_data';
import 'package:flutter/foundation.dart';
import 'package:record/record.dart';
import 'package:permission_handler/permission_handler.dart';

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

      // Start recording
      await _recorder.start(
        const RecordConfig(
          encoder: AudioEncoder.wav,
          sampleRate: 16000,
          numChannels: 1,
          bitRate: 128000,
        ),
      );

      _isRecording = true;
      notifyListeners();
      debugPrint('Recording started');
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

      // TODO: Read audio file and return bytes
      // For now, return mock data
      return Uint8List(0);
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
