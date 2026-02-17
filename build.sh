#!/usr/bin/env bash
set -euo pipefail

# Build PyMacroRecorder standalone binary using pyinstaller (Linux/macOS)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"
DIST_DIR="$PROJECT_ROOT/dist"
BUILD_DIR="$PROJECT_ROOT/build"
SPEC_FILE="$PROJECT_ROOT/PyMacroRecorder.spec"
ENTRYPOINT="$PROJECT_ROOT/main.py"
ICON_FILE="$PROJECT_ROOT/assets/logo.ico"
APP_NAME="PyMacroRecorder"

# Clean previous outputs
rm -rf "$DIST_DIR" "$BUILD_DIR" "$SPEC_FILE"

# Run pyinstaller with icon and assets
pyinstaller --onefile --noconsole --name "$APP_NAME" --icon "$ICON_FILE" --add-data "assets:assets" --distpath "$DIST_DIR" --workpath "$BUILD_DIR" "$ENTRYPOINT"

# Print result path
echo "Build complete. Binary located at: $DIST_DIR/$APP_NAME"

