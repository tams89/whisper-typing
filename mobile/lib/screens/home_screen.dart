import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../services/grpc_service.dart';
import '../services/audio_service.dart';
import 'settings_screen.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  String _transcribedText = '';
  bool _isRecording = false;

  @override
  Widget build(BuildContext context) {
    final grpcService = context.watch<GrpcService>();
    final audioService = context.watch<AudioService>();

    return Scaffold(
      appBar: AppBar(
        title: const Text('Whisper Typing'),
        actions: [
          IconButton(
            icon: const Icon(Icons.settings),
            onPressed: () {
              Navigator.push(
                context,
                MaterialPageRoute(builder: (context) => const SettingsScreen()),
              );
            },
          ),
        ],
      ),
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            children: [
              // Connection status card
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(16.0),
                  child: Row(
                    children: [
                      Icon(
                        grpcService.isConnected
                            ? Icons.check_circle
                            : Icons.error_outline,
                        color: grpcService.isConnected
                            ? Colors.green
                            : Colors.red,
                      ),
                      const SizedBox(width: 8),
                      Text(
                        grpcService.isConnected
                            ? 'Connected to backend'
                            : 'Not connected',
                        style: Theme.of(context).textTheme.titleMedium,
                      ),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 24),
              
              // Transcribed text display
              Expanded(
                child: Card(
                  child: Container(
                    width: double.infinity,
                    padding: const EdgeInsets.all(16.0),
                    child: SingleChildScrollView(
                      child: Text(
                        _transcribedText.isEmpty
                            ? 'Press the button below to start recording...'
                            : _transcribedText,
                        style: Theme.of(context).textTheme.bodyLarge,
                      ),
                    ),
                  ),
                ),
              ),
              const SizedBox(height: 24),
              
              // Recording button
              GestureDetector(
                onTapDown: (_) => _startRecording(audioService),
                onTapUp: (_) => _stopRecording(audioService, grpcService),
                onTapCancel: () => _stopRecording(audioService, grpcService),
                child: Container(
                  width: 120,
                  height: 120,
                  decoration: BoxDecoration(
                    shape: BoxShape.circle,
                    color: _isRecording
                        ? Colors.red
                        : Theme.of(context).colorScheme.primary,
                    boxShadow: [
                      BoxShadow(
                        color: (_isRecording ? Colors.red : Theme.of(context).colorScheme.primary)
                            .withOpacity(0.4),
                        blurRadius: 20,
                        spreadRadius: 5,
                      ),
                    ],
                  ),
                  child: Icon(
                    _isRecording ? Icons.stop : Icons.mic,
                    size: 60,
                    color: Colors.white,
                  ),
                ),
              ),
              const SizedBox(height: 16),
              Text(
                _isRecording
                    ? 'Recording... Release to transcribe'
                    : 'Hold to record',
                style: Theme.of(context).textTheme.titleMedium,
              ),
              const SizedBox(height: 24),
              
              // Action buttons
              if (_transcribedText.isNotEmpty) ...[
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                  children: [
                    ElevatedButton.icon(
                      onPressed: _copyToClipboard,
                      icon: const Icon(Icons.copy),
                      label: const Text('Copy'),
                    ),
                    ElevatedButton.icon(
                      onPressed: _clearText,
                      icon: const Icon(Icons.delete),
                      label: const Text('Clear'),
                    ),
                  ],
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }

  Future<void> _startRecording(AudioService audioService) async {
    setState(() {
      _isRecording = true;
    });
    await audioService.startRecording();
  }

  Future<void> _stopRecording(AudioService audioService, GrpcService grpcService) async {
    setState(() {
      _isRecording = false;
    });
    
    final audioData = await audioService.stopRecording();
    if (audioData != null) {
      try {
        final transcription = await grpcService.transcribe(audioData);
        setState(() {
          _transcribedText = transcription;
        });
      } catch (e) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Transcription failed: $e')),
        );
      }
    }
  }

  void _copyToClipboard() {
    // TODO: Implement clipboard copy
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Copied to clipboard')),
    );
  }

  void _clearText() {
    setState(() {
      _transcribedText = '';
    });
  }
}
