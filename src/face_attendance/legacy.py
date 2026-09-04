"""One-time import from the old attendancedb staff/attended MySQL tables."""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any

from face_attendance.clock import now
from face_attendance.config import AppConfig
from face_attendance.db import Store, StoreError, _open_mysql
from face_attendance.paths import faces_dir


def table_names(cur: Any) -> set[str]:
    names: set[str] = set()
    try:
        cur.execute("SHOW TABLES")
        for row in cur.fetchall():
            names.add(str(row[0]).lower())
    except Exception:
        try:
            cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
            for row in cur.fetchall():
                names.add(str(row[0]).lower())
        except Exception:
            return set()
    return names


def is_legacy_schema(names: set[str]) -> bool:
    return "staff" in names and "attended" in names


def detect_legacy_mysql(cfg: AppConfig) -> bool:
    conn = _open_mysql(cfg)
    try:
        cur = conn.cursor()
        return is_legacy_schema(table_names(cur))
    finally:
        conn.close()


def import_legacy_mysql(store: Store, cfg: AppConfig, data_dir: Path) -> dict[str, int]:
    """Copy old staff + attended into people/attended. Safe to re-run; skips dup days."""
    conn = _open_mysql(cfg)
    try:
        cur = conn.cursor()
        if not is_legacy_schema(table_names(cur)):
            raise StoreError("No old attendancedb staff/attended tables were found.")
        cur.execute("SELECT id, name, img_name FROM staff")
        staff_rows = list(cur.fetchall())
        cur.execute("SELECT staff_id, name, time, date FROM attended")
        attended_rows = list(cur.fetchall())
    finally:
        conn.close()
    return import_legacy_rows(store, data_dir, staff_rows, attended_rows)


def import_legacy_rows(
    store: Store,
    data_dir: Path,
    staff_rows: list[tuple[Any, ...]],
    attended_rows: list[tuple[Any, ...]],
) -> dict[str, int]:
    dest = faces_dir(data_dir)
    dest.mkdir(parents=True, exist_ok=True)
    existing = {p.full_name.lower(): p for p in store.list_people()}
    id_map: dict[int, int] = {}
    people_added = 0
    for raw_id, name, img_name in staff_rows:
        full_name = str(name or "").strip()
        if not full_name:
            continue
        photo_rel = None
        source = Path(str(img_name or ""))
        if str(img_name) and source.is_file():
            suffix = source.suffix or ".jpg"
            target = dest / f"import_{int(raw_id)}{suffix}"
            if not target.is_file():
                shutil.copy2(source, target)
            photo_rel = f"faces/{target.name}"
        prior = existing.get(full_name.lower())
        if prior is not None:
            id_map[int(raw_id)] = prior.id
            continue
        person = store.add_person(
            full_name=full_name,
            external_id=None,
            role="Staff",
            class_dept=None,
            photo_path=photo_rel,
        )
        id_map[int(raw_id)] = person.id
        existing[full_name.lower()] = person
        people_added += 1

    marks = 0
    skipped = 0
    for staff_id, name, time_value, date_value in attended_rows:
        try:
            old_id = int(staff_id)
        except (TypeError, ValueError):
            skipped += 1
            continue
        person_id = id_map.get(old_id)
        if person_id is None:
            skipped += 1
            continue
        person = store.get_person(person_id)
        if person is None:
            skipped += 1
            continue
        day = _as_iso_date(date_value)
        existing = store.already_marked(person.id, day)
        if existing:
            skipped += 1
            continue
        # Insert historical time/date without using "now".
        with store._lock:
            store._execute(
                store._q(
                    "INSERT INTO attended (person_id, name, time, date) VALUES (?, ?, ?, ?)"
                ),
                (person.id, str(name or person.full_name), _as_time(time_value), day),
            )
            store._conn.commit()
        marks += 1
    return {
        "people": people_added,
        "attended": marks,
        "skipped": skipped,
        "imported_at": now().isoformat(timespec="seconds"),
    }


def _as_iso_date(value: Any) -> str:
    text = str(value)
    if hasattr(value, "isoformat"):
        try:
            return value.isoformat()[:10]
        except Exception:
            pass
    return text[:10]


def _as_time(value: Any) -> str:
    text = str(value)
    if hasattr(value, "strftime"):
        try:
            return value.strftime("%H:%M:%S")
        except Exception:
            pass
    return text[:8] if text else "00:00:00"
