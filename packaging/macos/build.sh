#!/usr/bin/env bash
# Pack Face Attendance for macOS. Requires Python, Xcode CLT, and CMake.
# See docs/MACOS.md.

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

VERSION="1.0.0"
ARCH="$(uname -m)"
OUT_DIR="$ROOT/packaging/macos/output"
APP_NAME="Face Attendance.app"
APP_PATH="$ROOT/dist/$APP_NAME"

echo "Build root: $ROOT (arch=$ARCH)"

if [[ "$(uname -s)" != "Darwin" ]]; then
  echo "This script must run on a Mac. It cannot produce a .app from Linux." >&2
  exit 1
fi

if ! command -v python3 >/dev/null 2>&1; then
  echo "Python 3 is not on PATH. Install Python 3.10 or 3.11 (python.org or Homebrew)." >&2
  exit 1
fi
if ! command -v cmake >/dev/null 2>&1; then
  echo "CMake is not on PATH. Install with: brew install cmake" >&2
  echo "See docs/MACOS.md." >&2
  exit 1
fi
if ! xcode-select -p >/dev/null 2>&1; then
  echo "Xcode Command Line Tools are not installed. Run: xcode-select --install" >&2
  echo "See docs/MACOS.md." >&2
  exit 1
fi

VENV="$ROOT/.venv"
PY="$VENV/bin/python"
if [[ ! -x "$PY" ]]; then
  python3 -m venv "$VENV"
fi

"$PY" -m pip install --upgrade pip
"$PY" -m pip install -r "$ROOT/requirements.txt"
"$PY" -m pip install "mysql-connector-python>=8.0.33" pyinstaller tzdata

if ! "$PY" -c "import face_recognition" >/dev/null 2>&1; then
  echo "face_recognition did not import. dlib failed to compile on this Mac." >&2
  echo "On Apple Silicon, build arm64 against arm64 Python — do not mix Rosetta wheels." >&2
  echo "See docs/MACOS.md." >&2
  exit 1
fi

"$PY" -m PyInstaller "$ROOT/packaging/FaceAttendance.spec" --noconfirm --clean

if [[ ! -d "$APP_PATH" ]]; then
  echo "PyInstaller finished but dist/$APP_NAME is missing." >&2
  echo "The spec must run on Darwin so BUNDLE creates the .app." >&2
  exit 1
fi

mkdir -p "$OUT_DIR"
ZIP="$OUT_DIR/FaceAttendance-${VERSION}-macos-${ARCH}.zip"
rm -f "$ZIP"
# ditto preserves the .app bundle layout (do not use zip -r).
ditto -c -k --keepParent "$APP_PATH" "$ZIP"

echo "App bundle: $APP_PATH"
echo "Zip: $ZIP"
echo "Unsigned. First launch: right-click the app → Open (Gatekeeper)."
