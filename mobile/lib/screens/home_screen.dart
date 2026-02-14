import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
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
  bool _isTranscribing = false;
  final List<String> _transcriptionHistory = [];

  @override
  Widget build(BuildContext context) {
    final grpcService = context.watch<GrpcService>();
    final audioService = context.watch<AudioService>();

    return Scaffold(
      appBar: AppBar(
        title: const Text('Whisper Typing'),
        actions: [
          IconButton(
            icon: const Icon(Icons.history),
            onPressed: _showHistory,
          ),
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
                      child: _isTranscribing
                          ? const Center(
                              child: Column(
                                mainAxisAlignment: MainAxisAlignment.center,
                                children: [
                                  CircularProgressIndicator(),
                                  SizedBox(height: 16),
                                  Text('Transcribing...'),
                                ],
                              ),
                            )
                          : Text(
                              _transcribedText.isEmpty
                                  ? 'Press and hold the button below to start recording...'
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
                      onPressed: _improveText(grpcService),
                      icon: const Icon(Icons.auto_fix_high),
                      label: const Text('Improve'),
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
      _isTranscribing = true;
    });
    
    final audioData = await audioService.stopRecording();
    
    if (audioData != null && audioData.isNotEmpty) {
      try {
        final transcription = await grpcService.transcribe(audioData);
        setState(() {
          _transcribedText = transcription;
          _transcriptionHistory.insert(0, transcription);
          _isTranscribing = false;
        });
      } catch (e) {
        setState(() {
          _isTranscribing = false;
        });
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text('Transcription failed: $e')),
          );
        }
      }
    } else {
      setState(() {
        _isTranscribing = false;
      });
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('No audio recorded')),
        );
      }
    }
  }

  Future<void> _copyToClipboard() async {
    await Clipboard.setData(ClipboardData(text: _transcribedText));
    if (mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Copied to clipboard')),
      );
    }
  }

  VoidCallback _improveText(GrpcService grpcService) {
    return () async {
      try {
        setState(() {
          _isTranscribing = true;
        });
        
        final improved = await grpcService.improveText(_transcribedText);
        
        setState(() {
          _transcribedText = improved;
          _isTranscribing = false;
        });
        
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('Text improved!')),
          );
        }
      } catch (e) {
        setState(() {
          _isTranscribing = false;
        });
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text('Text improvement failed: $e')),
          );
        }
      }
    };
  }

  void _clearText() {
    setState(() {
      _transcribedText = '';
    });
  }

  void _showHistory() {
    showModalBottomSheet(
      context: context,
      builder: (context) => Container(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Transcription History',
              style: Theme.of(context).textTheme.titleLarge,
            ),
            const SizedBox(height: 16),
            Expanded(
              child: _transcriptionHistory.isEmpty
                  ? const Center(child: Text('No history yet'))
                  : ListView.builder(
                      itemCount: _transcriptionHistory.length,
                      itemBuilder: (context, index) {
                        return Card(
                          child: ListTile(
                            title: Text(
                              _transcriptionHistory[index],
                              maxLines: 2,
                              overflow: TextOverflow.ellipsis,
                            ),
                            onTap: () {
                              setState(() {
                                _transcribedText = _transcriptionHistory[index];
                              });
                              Navigator.pop(context);
                            },
                          ),
                        );
                      },
                    ),
            ),
          ],
        ),
      ),
    );
  }
}
