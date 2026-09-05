# Face Attendance

**Flemton Tech · local app**

Face attendance on this computer for schools and offices.

A clerk can install, register people, run a morning session, and export CSV without using a terminal. Faces and records stay in the data folder you choose. There is no cloud account and no internet is required for attendance.

## What you get

- **Take attendance** — morning session, Start / Pause / Stop, one mark per person per day
- **Staff** — capture a photo to `{data}/faces/`, name, optional ID, role, class/department
- **Log** — filters, CSV export, print, path shown in the footer
- **Settings** — organisation, camera + test, data folder, Strict / Simple / Loose, English, optional MySQL

Times on screen are **Africa/Accra**.

This is not Tamale Dispatch. It does not include payroll, GES, liveness, multi-camera, or a mobile app.

## Clerk install

Use a packed build from the matching OS. Clerks do not need Python or a compiler.

1. Windows: run `FaceAttendance-1.0.0-Setup.exe`, **or** unzip the portable folder and start `FaceAttendance.exe`.
2. macOS: open `Face Attendance.app` (first time: right-click → Open).
3. Linux: unzip the tarball and start `FaceAttendance` (or the optional AppImage).
4. On first launch choose a **data folder** (or Skip for now). Config is saved as `config.json` in that folder.
5. Connect the camera, register the first person, then take attendance.

Default database: **SQLite** at `{data folder}/face_attendance.db`. Photos: `{data folder}/faces/`.

## Build for Windows / macOS / Linux

Packed builds are produced **on that OS**. The Windows `.exe` is still built on a Windows PC.

| Platform | Clerk deliverable | Build script | Doc |
| --- | --- | --- | --- |
| Windows | Setup.exe or portable folder | `packaging/windows/build.ps1` | [docs/WINDOWS.md](docs/WINDOWS.md) |
| macOS | `Face Attendance.app` | `packaging/macos/build.sh` | [docs/MACOS.md](docs/MACOS.md) |
| Linux | Portable tarball (optional AppImage) | `packaging/linux/build.sh` | [docs/LINUX.md](docs/LINUX.md) |

All three compile **dlib** (`face_recognition`). Build-machine prerequisites are documented honestly in those files (VC++ / CMake on Windows; Xcode CLT + Homebrew CMake on Mac; build-essential + CMake on Linux). Apple Silicon notes (arm64 vs Intel, no universal2 binary) are in the macOS doc.

## Run from source (developers)

Needs Python 3.10+. On Windows, `face_recognition` / dlib also need **Visual C++ Build Tools** and **CMake** — that is documented honestly in [docs/WINDOWS.md](docs/WINDOWS.md). Do not expect `pip install` alone to work on a clean Windows PC.

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python -m face_attendance
```

On Linux / macOS, after installing CMake and a C++ compiler:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt   # app UI + tests, no dlib
pip install -r requirements.txt       # full recognition stack
python -m face_attendance
```

Optional flags: `--data-dir PATH`, `--screen staff|log|settings|attendance|welcome`.

`register_staff.py` opens the Staff screen. `face_attendance.py` starts the app.

## Settings → Advanced (MySQL)

MySQL is optional. Default is SQLite on this PC.

If you already have the old `attendancedb` (`staff` + `attended` tables), connect under Advanced and use **Import old attendancedb** once. Schema for a new MySQL database is in `sql/mysql_schema.sql`. Credentials are stored only in `{data folder}/config.json` on that computer — they are never shipped in this repository.

## Tests

```bash
pip install -r requirements-dev.txt
pytest
```

Recognition tests that need `face_recognition` are skipped when dlib is not installed.

## Credits

Built from the CS50-era Face Attendance work. Thanks Nick, Prof. David J. Malan, Brian Yu, Doug Lloyd, and the CS50 team.
