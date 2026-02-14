# Generate Dart code from Protocol Buffer definitions
# Windows PowerShell version

# Check if protoc is installed
$protocPath = Get-Command protoc -ErrorAction SilentlyContinue
if (-not $protocPath) {
    Write-Host "Error: protoc (Protocol Buffer Compiler) is not installed" -ForegroundColor Red
    Write-Host "Download from: https://github.com/protocolbuffers/protobuf/releases"
    Write-Host "Add protoc.exe to your PATH"
    exit 1
}

# Check if protoc-gen-dart is installed
$dartPluginPath = Get-Command protoc-gen-dart -ErrorAction SilentlyContinue
if (-not $dartPluginPath) {
    Write-Host "Error: protoc-gen-dart plugin is not installed" -ForegroundColor Red
    Write-Host "Install with: dart pub global activate protoc_plugin"
    Write-Host "Make sure %APPDATA%\Pub\Cache\bin is in your PATH"
    exit 1
}

# Create output directory
New-Item -ItemType Directory -Path "lib\generated" -Force | Out-Null

# Generate Dart code
Write-Host "Generating Dart code from proto files..." -ForegroundColor Green

protoc `
    --dart_out=grpc:lib/generated `
    --proto_path=proto `
    proto/transcription.proto `
    proto/config.proto `
    proto/health.proto

if ($LASTEXITCODE -eq 0) {
    Write-Host "Code generation complete!" -ForegroundColor Green
    Write-Host "Generated files are in lib/generated/"
} else {
    Write-Host "Code generation failed!" -ForegroundColor Red
    exit 1
}
