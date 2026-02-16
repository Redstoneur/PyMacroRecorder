#!/usr/bin/env pwsh
# Build PyMacroRecorder standalone binary using pyinstaller (Windows)
$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Definition
$DistDir = Join-Path $ProjectRoot "dist"
$BuildDir = Join-Path $ProjectRoot "build"
$SpecFile = Join-Path $ProjectRoot "PyMacroRecorder.spec"
$EntryPoint = Join-Path $ProjectRoot "main.py"
$AppName = "PyMacroRecorder"

# Clean previous outputs
Remove-Item -Recurse -Force -ErrorAction SilentlyContinue $DistDir, $BuildDir, $SpecFile

# Run pyinstaller
pyinstaller \
  --onefile \
  --name "$AppName" \
  --distpath "$DistDir" \
  --workpath "$BuildDir" \
  "$EntryPoint"

Write-Host "Build complete. Binary located at: $DistDir\$AppName.exe"

