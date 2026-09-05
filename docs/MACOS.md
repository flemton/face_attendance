# macOS app-bundle build

Clerks should receive `Face Attendance.app` (or the zip of that bundle). They do not need Python, a terminal, Homebrew, or Xcode.

Building that file **does** need a Mac with a C++ toolchain. This document is the pack path. It is not optional documentation — `face_recognition` sits on **dlib**, and dlib compiles native code.

The Windows `.exe` is still built on a Windows PC ([docs/WINDOWS.md](WINDOWS.md)). This script will not produce it. It also will not run from Linux.

## What a clerk gets

| Deliverable | How they start |
| --- | --- |
| `Face Attendance.app` | Double-click. First time: **right-click → Open** (unsigned) |
| Zip of that bundle | Unzip, then the same |

Data is **not** stored inside the `.app`. First-run asks for a data folder (default `~/FaceAttendance`). `config.json`, `face_attendance.db`, and `faces/` live there.

Window size is 1280×800. macOS will ask for the camera because the bundle declares `NSCameraUsageDescription`. Nothing is uploaded.

## Build machine prerequisites

Install these **before** `pip install -r requirements.txt`:

1. **Python 3.10 or 3.11** (64-bit) from python.org or Homebrew. 3.12+ is more likely to fight dlib.
2. **Xcode Command Line Tools**
   ```bash
   xcode-select --install
   xcode-select -p
   ```
3. **CMake** via Homebrew
   ```bash
   brew install cmake
   cmake --version
   ```

Typical failure if those are missing:

```
xcrun: error: invalid active developer path
```

or CMake / `clang++` dying while compiling dlib. There is no pip-only workaround we ship. Do not download random unofficial dlib wheels unless you trust the source; we do not vendor them.

We use **PyInstaller** (same spec as Windows and Linux), not py2app. One collection path for OpenCV + dlib is less fragile.

## Apple Silicon (arm64) — read this

- Build **on the Mac you will run**. An arm64 build will not run on Intel, and the reverse is true unless you use Rosetta.
- Use an **arm64 Python** with an **arm64** Homebrew CMake. Mixing a Rosetta (x86_64) Python with arm64 libraries is the usual dlib failure on M1/M2/M3.
  ```bash
  python3 -c "import platform; print(platform.machine())"
  uname -m
  ```
  Both should print `arm64`.
- If `pip install dlib` fails on arm64, retry in a clean venv after `brew install cmake openblas`. You can pass:
  ```bash
  export CMAKE_ARGS="-DCMAKE_OSX_ARCHITECTURES=arm64"
  ```
- We do **not** produce a universal2 (`arm64 + x86_64`) `.app`. That would mean compiling dlib twice and lipo-ing; we do not do that here.
- Intel Macs: build on Intel (`x86_64`). Do not cross-compile from Apple Silicon.

## Build commands

```bash
cd face_attendance
bash packaging/macos/build.sh
```

The script:

1. Refuses to run on non-Darwin
2. Checks for `python3`, `cmake`, and Xcode CLT
3. Creates `.venv` if needed
4. Installs `requirements.txt`, `pyinstaller`, and `tzdata` (compiles **dlib** — first time is slow)
5. Runs PyInstaller with `packaging/FaceAttendance.spec` (onedir + `.app` bundle)
6. Zips the bundle with `ditto` so Finder metadata stays intact

Outputs:

- App: `dist/Face Attendance.app`
- Zip: `packaging/macos/output/FaceAttendance-1.0.0-macos-arm64.zip` (or `x86_64`)

## Signing and Gatekeeper

This pack is **unsigned**. We do not pay for an Apple Developer ID or notarization.

Clerks on a fresh Mac:

1. Unzip if needed
2. Right-click **Face Attendance** → **Open** → Open
3. Allow the camera when macOS asks

`spctl --assess` will fail until someone with a Developer ID signs the bundle. That is expected.

## Runtime notes for IT

- Offline only. No cloud face API.
- One camera (built-in or USB). Settings → Test camera.
- Optional MySQL is local, under Settings → Advanced. SQLite is the default.
- Africa/Accra times need the `tzdata` package (bundled by the spec).

## Other platforms

- Windows installer / portable: [WINDOWS.md](WINDOWS.md) (built on a Windows PC)
- Linux portable tarball / optional AppImage: [LINUX.md](LINUX.md)
