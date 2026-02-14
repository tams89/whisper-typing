import 'dart:typed_data';
import 'package:flutter/foundation.dart';
import 'package:grpc/grpc.dart';
import 'package:shared_preferences/shared_preferences.dart';

// TODO: Import generated protobuf files when proto files are compiled
// import '../proto/transcription.pbgrpc.dart';
// import '../proto/health.pbgrpc.dart';

class GrpcService extends ChangeNotifier {
  ClientChannel? _channel;
  String _host = 'localhost';
  int _port = 50051;
  bool _isConnected = false;

  String get host => _host;
  int get port => _port;
  bool get isConnected => _isConnected;

  GrpcService() {
    _loadSettings();
  }

  Future<void> _loadSettings() async {
    final prefs = await SharedPreferences.getInstance();
    _host = prefs.getString('grpc_host') ?? 'localhost';
    _port = prefs.getInt('grpc_port') ?? 50051;
    notifyListeners();
  }

  Future<void> _saveSettings() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('grpc_host', _host);
    await prefs.setInt('grpc_port', _port);
  }

  Future<void> connect(String host, int port) async {
    try {
      // Close existing channel if any
      await _channel?.shutdown();

      _host = host;
      _port = port;
      await _saveSettings();

      // Create new channel
      _channel = ClientChannel(
        _host,
        port: _port,
        options: const ChannelOptions(
          credentials: ChannelCredentials.insecure(),
        ),
      );

      // Test connection with health check
      final isHealthy = await checkHealth();
      _isConnected = isHealthy;
      notifyListeners();

      if (!isHealthy) {
        throw Exception('Backend health check failed');
      }
    } catch (e) {
      _isConnected = false;
      notifyListeners();
      rethrow;
    }
  }

  Future<bool> checkHealth() async {
    if (_channel == null) return false;

    try {
      // TODO: Implement health check using generated proto
      // final stub = HealthServiceClient(_channel!);
      // final response = await stub.check(HealthCheckRequest());
      // return response.status == HealthCheckResponse_Status.HEALTHY;

      // Mock implementation until proto is compiled
      await Future.delayed(const Duration(milliseconds: 100));
      return true;
    } catch (e) {
      debugPrint('Health check failed: $e');
      return false;
    }
  }

  Future<String> transcribe(Uint8List audioData) async {
    if (_channel == null || !_isConnected) {
      throw Exception('Not connected to backend');
    }

    try {
      // TODO: Implement transcription using generated proto
      // final stub = TranscriptionServiceClient(_channel!);
      // final request = AudioRequest()
      //   ..audioData = audioData
      //   ..sampleRate = 16000
      //   ..channels = 1
      //   ..encoding = 'wav';
      // final response = await stub.transcribe(request);
      // return response.text;

      // Mock implementation until proto is compiled
      await Future.delayed(const Duration(seconds: 1));
      return 'Mock transcription: This is a test transcription of your audio.';
    } catch (e) {
      debugPrint('Transcription failed: $e');
      rethrow;
    }
  }

  Future<String> improveText(String text) async {
    if (_channel == null || !_isConnected) {
      throw Exception('Not connected to backend');
    }

    try {
      // TODO: Implement text improvement using generated proto
      // final stub = TranscriptionServiceClient(_channel!);
      // final request = ImproveTextRequest()..text = text;
      // final response = await stub.improveText(request);
      // return response.improvedText;

      // Mock implementation
      await Future.delayed(const Duration(seconds: 1));
      return 'Improved: $text';
    } catch (e) {
      debugPrint('Text improvement failed: $e');
      rethrow;
    }
  }

  @override
  void dispose() {
    _channel?.shutdown();
    super.dispose();
  }
}
