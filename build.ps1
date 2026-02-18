#!/usr/bin/env pwsh
# Build PyMacroRecorder standalone binary using pyinstaller (Windows)
$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Definition
$DistDir = Join-Path $ProjectRoot "dist"
$BuildDir = Join-Path $ProjectRoot "build"
$SpecFile = Join-Path $ProjectRoot "PyMacroRecorder.spec"
$EntryPoint = Join-Path $ProjectRoot "main.py"
$IconFile = Join-Path $ProjectRoot "assets\logo.ico"
$AppName = "PyMacroRecorder"

# Clean previous outputs
Remove-Item -Recurse -Force -ErrorAction SilentlyContinue $DistDir, $BuildDir, $SpecFile

# Run pyinstaller with icon and assets
# Add hidden imports for pynput backends (especially for Linux cross-compat)
pyinstaller --onefile --noconsole `
  --name "$AppName" `
  --icon "$IconFile" `
  --add-data "assets;assets" `
  --hidden-import pynput.keyboard._win32 `
  --hidden-import pynput.mouse._win32 `
  --distpath "$DistDir" `
  --workpath "$BuildDir" `
  "$EntryPoint"

Write-Output "Build complete. Binary located at: $DistDir\$AppName.exe"

