"""Data-folder pointer and on-disk layout. Config lives in the data folder."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

POINTER_NAME = "pointer.json"
CONFIG_NAME = "config.json"
DB_NAME = "face_attendance.db"
FACES_DIRNAME = "faces"


def is_windows() -> bool:
    return sys.platform == "win32"


def app_support_dir() -> Path:
    if is_windows():
        root = os.environ.get("APPDATA") or str(Path.home() / "AppData" / "Roaming")
        return Path(root) / "FlemtonTech" / "FaceAttendance"
    xdg = os.environ.get("XDG_CONFIG_HOME")
    if xdg:
        return Path(xdg) / "flemton-tech" / "face-attendance"
    return Path.home() / ".config" / "flemton-tech" / "face-attendance"


def pointer_path() -> Path:
    return app_support_dir() / POINTER_NAME


def default_data_dir() -> Path:
    if is_windows():
        docs = os.environ.get("USERPROFILE")
        base = Path(docs) / "Documents" if docs else Path.home() / "Documents"
        return base / "FaceAttendance"
    return Path.home() / "FaceAttendance"


def read_pointer() -> Path | None:
    path = pointer_path()
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    folder = data.get("data_folder")
    if not folder:
        return None
    return Path(folder)


def write_pointer(data_dir: Path) -> None:
    support = app_support_dir()
    support.mkdir(parents=True, exist_ok=True)
    payload = {"data_folder": str(data_dir)}
    pointer_path().write_text(json.dumps(payload, indent=2), encoding="utf-8")


def resolve_data_dir(override: str | Path | None = None) -> Path:
    if override:
        return Path(override).expanduser().resolve()
    pointed = read_pointer()
    if pointed:
        return pointed.expanduser()
    return default_data_dir()


def ensure_data_layout(data_dir: Path) -> Path:
    data_dir = Path(data_dir).expanduser()
    data_dir.mkdir(parents=True, exist_ok=True)
    (data_dir / FACES_DIRNAME).mkdir(parents=True, exist_ok=True)
    return data_dir


def faces_dir(data_dir: Path) -> Path:
    return Path(data_dir) / FACES_DIRNAME


def db_path(data_dir: Path) -> Path:
    return Path(data_dir) / DB_NAME


def config_path(data_dir: Path) -> Path:
    return Path(data_dir) / CONFIG_NAME


def resolve_photo(data_dir: Path, photo_path: str | None) -> Path | None:
    if not photo_path:
        return None
    path = Path(photo_path)
    if not path.is_absolute():
        path = Path(data_dir) / path
    return path if path.is_file() else path
