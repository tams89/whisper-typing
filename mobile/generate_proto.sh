#!/bin/bash
# Generate Dart code from Protocol Buffer definitions

# Ensure protoc is installed
if ! command -v protoc &> /dev/null; then
    echo "Error: protoc (Protocol Buffer Compiler) is not installed"
    echo "Install with: brew install protobuf (macOS) or apt install protobuf-compiler (Linux)"
    exit 1
fi

# Ensure protoc Dart plugin is installed
if ! command -v protoc-gen-dart &> /dev/null; then
    echo "Error: protoc-gen-dart plugin is not installed"
    echo "Install with: dart pub global activate protoc_plugin"
    echo "Make sure ~/.pub-cache/bin is in your PATH"
    exit 1
fi

# Generate Dart code
echo "Generating Dart code from proto files..."

protoc \
    --dart_out=grpc:lib/generated \
    --proto_path=proto \
    proto/transcription.proto \
    proto/config.proto \
    proto/health.proto

echo "Code generation complete!"
echo "Generated files are in lib/generated/"
