# Windows installer and portable build

Clerks should receive `FaceAttendance-1.0.0-Setup.exe` or a portable zip. They do not need Python, a terminal, CMake, or Visual Studio.

Building those files **does** need a Windows PC with a C++ toolchain. This document is the pack path. It is not optional documentation — `face_recognition` sits on **dlib**, and dlib compiles native code.

## What a clerk gets

| Deliverable | How they start |
| --- | --- |
| Inno Setup installer | Start menu → Face Attendance |
| Portable folder | Double-click `FaceAttendance.exe` inside the unzipped folder |

Data is **not** stored next to the exe. First-run asks for a data folder (default `Documents\FaceAttendance`). `config.json`, `face_attendance.db`, and `faces\` live there.

Window size is 1280×800.

## Build machine prerequisites

Install these **before** `pip install -r requirements.txt`:

1. **Python 3.10 or 3.11** (64-bit) from python.org, with “Add python.exe to PATH”.
2. **Visual Studio Build Tools 2022**
   - Workload: **Desktop development with C++**
   - Include the Windows 10/11 SDK and the latest MSVC toolset
3. **CMake** from [cmake.org](https://cmake.org/download/), added to PATH  
   Confirm in a new Command Prompt: `cmake --version`

Typical failure if those are missing:

```
error: Microsoft Visual C++ 14.0 or greater is required
```

or dlib’s CMake step exits while compiling. There is no pip-only workaround we ship. Do not download random unofficial dlib wheels unless you trust the source; we do not vendor them.

Optional: Inno Setup 6 if you want the installer (portable onedir works without it).

## Build commands

From a Developer Command Prompt or a normal prompt after the tools are on PATH:

```powershell
cd face_attendance
powershell -ExecutionPolicy Bypass -File packaging\windows\build.ps1
```

The script:

1. Creates `.venv` if needed
2. Installs `requirements.txt`, `pyinstaller`, and `tzdata`
3. Compiles **dlib** (this can take a long time the first time)
4. Runs PyInstaller with `packaging/FaceAttendance.spec` (onedir, windowed)
5. If `ISCC.exe` is on PATH, compiles `packaging/windows/FaceAttendance.iss`

Outputs:

- Portable app: `dist/FaceAttendance/FaceAttendance.exe`
- Installer (if Inno is installed): `packaging/windows/output/FaceAttendance-1.0.0-Setup.exe`

Zip `dist/FaceAttendance` for a portable drop.

## What we do not do from Linux CI

This repository’s Linux agents cannot emit a signed Windows exe. Do not merge a release tag for a build that was not produced on Windows with the steps above.

## Runtime notes for IT

- Offline only. No cloud face API.
- One USB camera. Settings → Test camera.
- Optional MySQL is local, under Settings → Advanced. SQLite is the default.
- Africa/Accra times need the `tzdata` package (bundled by the spec).
