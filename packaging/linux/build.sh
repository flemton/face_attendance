#!/usr/bin/env bash
# Pack Face Attendance for Linux. Requires Python, a C++ compiler, and CMake.
# See docs/LINUX.md.

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

VERSION="1.0.0"
ARCH="$(uname -m)"
OUT_DIR="$ROOT/packaging/linux/output"
DIST_DIR="$ROOT/dist/FaceAttendance"

echo "Build root: $ROOT"

if ! command -v python3 >/dev/null 2>&1; then
  echo "Python 3 is not on PATH. Install Python 3.10+ (python3-venv)." >&2
  exit 1
fi
if ! command -v cmake >/dev/null 2>&1; then
  echo "CMake is not on PATH. Install cmake (build-essential + cmake). See docs/LINUX.md." >&2
  exit 1
fi
if ! command -v c++ >/dev/null 2>&1 && ! command -v g++ >/dev/null 2>&1; then
  echo "No C++ compiler on PATH. Install build-essential. See docs/LINUX.md." >&2
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
  echo "face_recognition did not import. dlib failed to compile." >&2
  echo "Install build-essential, cmake, python3-dev, libopenblas-dev. See docs/LINUX.md." >&2
  exit 1
fi

"$PY" -m PyInstaller "$ROOT/packaging/FaceAttendance.spec" --noconfirm --clean

if [[ ! -x "$DIST_DIR/FaceAttendance" ]]; then
  echo "PyInstaller finished but dist/FaceAttendance/FaceAttendance is missing." >&2
  exit 1
fi

mkdir -p "$OUT_DIR"
cp "$ROOT/packaging/linux/FaceAttendance.desktop" "$DIST_DIR/FaceAttendance.desktop"
# Desktop files launched from a folder need a relative Exec.
sed -i 's|^Exec=FaceAttendance$|Exec=./FaceAttendance|' "$DIST_DIR/FaceAttendance.desktop"

ARCHIVE="$OUT_DIR/FaceAttendance-${VERSION}-linux-${ARCH}.tar.gz"
tar -C "$ROOT/dist" -czf "$ARCHIVE" FaceAttendance

echo "Portable folder: $DIST_DIR"
echo "Tarball: $ARCHIVE"

if command -v appimagetool >/dev/null 2>&1; then
  APPDIR="$OUT_DIR/FaceAttendance.AppDir"
  rm -rf "$APPDIR"
  mkdir -p "$APPDIR/usr/bin"
  cp -a "$DIST_DIR/." "$APPDIR/"
  cat > "$APPDIR/AppRun" <<'EOF'
#!/bin/sh
HERE="$(dirname "$(readlink -f "$0")")"
cd "$HERE" || exit 1
exec "$HERE/FaceAttendance" "$@"
EOF
  chmod +x "$APPDIR/AppRun"
  cp "$ROOT/packaging/linux/FaceAttendance.desktop" "$APPDIR/FaceAttendance.desktop"
  # AppImage desktop Exec must be the binary name only.
  sed -i 's|^Exec=.*|Exec=FaceAttendance|' "$APPDIR/FaceAttendance.desktop"
  # Placeholder icon name; clerks can ignore if no PNG is bundled.
  touch "$APPDIR/face-attendance.png"
  appimagetool "$APPDIR" "$OUT_DIR/FaceAttendance-${VERSION}-linux-${ARCH}.AppImage"
  echo "AppImage: $OUT_DIR/FaceAttendance-${VERSION}-linux-${ARCH}.AppImage"
else
  echo "appimagetool not found — portable tarball is enough. Optional AppImage: see docs/LINUX.md."
fi
