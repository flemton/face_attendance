from pathlib import Path

from face_attendance.config import default_config
from face_attendance.db import Store
from face_attendance.legacy import import_legacy_rows, is_legacy_schema


def test_legacy_schema_detection():
    assert is_legacy_schema({"staff", "attended"})
    assert not is_legacy_schema({"people", "attended"})


def test_import_legacy_rows(tmp_path: Path):
    store = Store(tmp_path, default_config())
    photo = tmp_path / "old.jpg"
    photo.write_bytes(b"not-a-real-image")
    stats = import_legacy_rows(
        store,
        tmp_path,
        staff_rows=[(1, "Alhassan Osman", str(photo))],
        attended_rows=[(1, "Alhassan Osman", "05:44:10", "2021-11-06")],
    )
    assert stats["people"] == 1
    assert stats["attended"] == 1
    people = store.list_people()
    assert people[0].full_name == "Alhassan Osman"
    assert people[0].photo_path and people[0].photo_path.startswith("faces/")
    rows = store.list_attendance()
    assert rows[0].date == "2021-11-06"
    assert rows[0].time == "05:44:10"
    again = import_legacy_rows(
        store,
        tmp_path,
        staff_rows=[(1, "Alhassan Osman", str(photo))],
        attended_rows=[(1, "Alhassan Osman", "05:44:10", "2021-11-06")],
    )
    assert again["people"] == 0
    assert again["attended"] == 0
    assert again["skipped"] >= 1
    assert store.count_people() == 1
