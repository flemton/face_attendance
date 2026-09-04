from pathlib import Path

import pytest

from face_attendance.config import default_config
from face_attendance.db import Store, StoreError


def _store(tmp_path: Path) -> Store:
    return Store(tmp_path, default_config())


def _person(store: Store, name: str = "Ama Mensah"):
    return store.add_person(name, "ST-1", "Staff", "Office", None)


def test_add_and_list_people(tmp_path: Path):
    store = _store(tmp_path)
    store.add_person("Kofi Mensah", None, "Teacher", "JHS 2", "faces/1.jpg")
    people = store.list_people()
    assert len(people) == 1
    assert people[0].full_name == "Kofi Mensah"
    assert people[0].role == "Teacher"
    assert people[0].external_id is None


def test_name_required(tmp_path: Path):
    store = _store(tmp_path)
    with pytest.raises(StoreError):
        store.add_person("   ", None, "Staff", None, None)


def test_one_mark_per_person_per_day(tmp_path: Path):
    store = _store(tmp_path)
    person = _person(store)
    kind1, row1 = store.mark_attendance(person, day="2026-09-04")
    kind2, row2 = store.mark_attendance(person, day="2026-09-04")
    assert kind1 == "present"
    assert kind2 == "already"
    assert row1.date == "2026-09-04"
    assert row2.id == row1.id
    kind3, _ = store.mark_attendance(person, day="2026-09-05")
    assert kind3 == "present"
    rows = store.list_attendance()
    assert len(rows) == 2


def test_filters(tmp_path: Path):
    store = _store(tmp_path)
    staff = store.add_person("Ama Serwaa", "A1", "Staff", None, None)
    student = store.add_person("Yaw Boateng", "S1", "Student", "1A", None)
    store.mark_attendance(staff, day="2026-09-01")
    store.mark_attendance(student, day="2026-09-02")
    only_staff = store.list_attendance(role="Staff")
    assert [r.name for r in only_staff] == ["Ama Serwaa"]
    named = store.list_attendance(name_query="yaw")
    assert [r.name for r in named] == ["Yaw Boateng"]
    ranged = store.list_attendance(date_from="2026-09-02", date_to="2026-09-02")
    assert [r.name for r in ranged] == ["Yaw Boateng"]


def test_edit_and_delete_keeps_log(tmp_path: Path):
    store = _store(tmp_path)
    person = _person(store)
    store.mark_attendance(person, day="2026-09-04")
    store.update_person(person.id, "Ama Mensah Updated", "ST-9", "Teacher", "Maths", None)
    updated = store.get_person(person.id)
    assert updated.full_name == "Ama Mensah Updated"
    assert updated.role == "Teacher"
    store.delete_person(person.id)
    assert store.get_person(person.id) is None
    rows = store.list_attendance()
    assert len(rows) == 1
    assert rows[0].name == "Ama Mensah"


def test_sqlite_file_created(tmp_path: Path):
    store = _store(tmp_path)
    _person(store)
    store.close()
    assert (tmp_path / "face_attendance.db").is_file()
