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

## Clerk install (Windows)

Use the packed build from a Windows machine (see [docs/WINDOWS.md](docs/WINDOWS.md)):

1. Run `FaceAttendance-1.0.0-Setup.exe`, **or** unzip the portable `FaceAttendance` folder and start `FaceAttendance.exe`.
2. On first launch choose a **data folder** (or Skip for now). Config is saved as `config.json` in that folder.
3. Connect the camera, register the first person, then take attendance.

Default database: **SQLite** at `{data folder}/face_attendance.db`. Photos: `{data folder}/faces/`.

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
