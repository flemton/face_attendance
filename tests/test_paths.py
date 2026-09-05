from pathlib import Path

from face_attendance.paths import (
    CONFIG_NAME,
    DB_NAME,
    FACES_DIRNAME,
    default_data_dir,
    ensure_data_layout,
    resolve_data_dir,
)


def test_layout_creates_faces(tmp_path: Path):
    folder = ensure_data_layout(tmp_path / "data")
    assert (folder / FACES_DIRNAME).is_dir()
    assert folder.name == "data"


def test_resolve_override(tmp_path: Path):
    assert resolve_data_dir(tmp_path / "custom") == (tmp_path / "custom").resolve()


def test_default_dir_name():
    assert default_data_dir().name == "FaceAttendance"


def test_artifact_names():
    assert CONFIG_NAME == "config.json"
    assert DB_NAME == "face_attendance.db"
