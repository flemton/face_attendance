# Linux portable build

Clerks should receive a `FaceAttendance-1.0.0-linux-*.tar.gz` (or an AppImage if you wrap one). They do not need Python, a terminal, or CMake.

Building those files **does** need a Linux machine with a C++ toolchain. This document is the pack path. It is not optional documentation — `face_recognition` sits on **dlib**, and dlib compiles native code.

The Windows `.exe` is still built on a Windows PC ([docs/WINDOWS.md](WINDOWS.md)). This script will not produce it.

## What a clerk gets

| Deliverable | How they start |
| --- | --- |
| Portable folder (inside the tarball) | Double-click `FaceAttendance`, or the `.desktop` file |
| Optional AppImage | Double-click `FaceAttendance-1.0.0-linux-*.AppImage` (chmod +x first) |

Data is **not** stored next to the binary. First-run asks for a data folder (default `~/FaceAttendance`). `config.json`, `face_attendance.db`, and `faces/` live there.

Window size is 1280×800. Typical Ubuntu / Debian desktops (X11 or XWayland) are the target. A headless server will not show the GUI.

## Build machine prerequisites

Install these **before** `pip install -r requirements.txt`:

1. **Python 3.10 or 3.11** with `venv` (`python3-venv`).
2. **build-essential** (gcc/g++, make).
3. **CMake** (`cmake` on PATH). Confirm: `cmake --version`.
4. **Python headers** (`python3-dev`) and **OpenBLAS** (`libopenblas-dev`) so dlib can compile.
5. **Tk** (`python3-tk`) if you also run from source. The packed binary bundles Tcl/Tk.

On Debian / Ubuntu:

```bash
sudo apt-get update
sudo apt-get install -y build-essential cmake python3-dev python3-venv python3-tk \
  libopenblas-dev liblapack-dev libx11-dev
```

Typical failure if those are missing:

```
error: command 'g++' failed
```

or CMake cannot find Python / OpenBLAS while compiling dlib. There is no pip-only workaround we ship. Do not download random unofficial dlib wheels unless you trust the source; we do not vendor them.

Optional: [appimagetool](https://github.com/AppImage/appimagetool) on PATH if you want an AppImage. The tarball is enough.

## Build commands

```bash
cd face_attendance
bash packaging/linux/build.sh
```

The script:

1. Checks for `python3`, `cmake`, and a C++ compiler
2. Creates `.venv` if needed
3. Installs `requirements.txt`, `pyinstaller`, and `tzdata` (compiles **dlib** — first time is slow)
4. Runs PyInstaller with `packaging/FaceAttendance.spec` (onedir, windowed)
5. Writes `packaging/linux/output/FaceAttendance-1.0.0-linux-<arch>.tar.gz`
6. If `appimagetool` is on PATH, also writes an AppImage

Outputs:

- Portable app: `dist/FaceAttendance/FaceAttendance`
- Tarball: `packaging/linux/output/FaceAttendance-1.0.0-linux-x86_64.tar.gz` (or `aarch64`)

Build on the CPU you will run: x86_64 vs ARM. We do not ship a multi-arch binary.

## Runtime notes for IT

- Offline only. No cloud face API.
- One USB camera. Settings → Test camera. The clerk needs permission to `/dev/video*`.
- If the packed app exits with a `libGL` / `libxcb` error, install the desktop OpenGL stack (`libgl1`, `libxcb-xinerama0` on Ubuntu).
- Optional MySQL is local, under Settings → Advanced. SQLite is the default.
- Africa/Accra times need the `tzdata` package (bundled by the spec).

## Other platforms

- Windows installer / portable: [WINDOWS.md](WINDOWS.md) (built on a Windows PC)
- macOS `.app`: [MACOS.md](MACOS.md) (built on a Mac)
