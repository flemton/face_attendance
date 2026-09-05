#!/usr/bin/env python3
"""Launch Face Attendance (Flemton Tech)."""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from face_attendance.app import main

if __name__ == "__main__":
    raise SystemExit(main())
