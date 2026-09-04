"""SQLite by default; optional MySQL. people + attended unique(person_id, date)."""

from __future__ import annotations

import sqlite3
import threading
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

from face_attendance.clock import format_time_long, now, today_iso
from face_attendance.config import AppConfig, ROLES
from face_attendance.paths import db_path, ensure_data_layout

SQLITE_SCHEMA = """
CREATE TABLE IF NOT EXISTS people (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT NOT NULL,
    external_id TEXT,
    role TEXT NOT NULL DEFAULT 'Staff',
    class_dept TEXT,
    photo_path TEXT,
    created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS attended (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    person_id INTEGER,
    name TEXT NOT NULL,
    time TEXT NOT NULL,
    date TEXT NOT NULL,
    UNIQUE (person_id, date),
    FOREIGN KEY (person_id) REFERENCES people(id) ON DELETE SET NULL
);
"""

MYSQL_SCHEMA = [
    """
    CREATE TABLE IF NOT EXISTS people (
        id INT AUTO_INCREMENT PRIMARY KEY,
        full_name VARCHAR(255) NOT NULL,
        external_id VARCHAR(64) NULL,
        role VARCHAR(32) NOT NULL DEFAULT 'Staff',
        class_dept VARCHAR(128) NULL,
        photo_path VARCHAR(512) NULL,
        created_at VARCHAR(32) NOT NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """,
    """
    CREATE TABLE IF NOT EXISTS attended (
        id INT AUTO_INCREMENT PRIMARY KEY,
        person_id INT NULL,
        name VARCHAR(255) NOT NULL,
        time VARCHAR(16) NOT NULL,
        date VARCHAR(10) NOT NULL,
        UNIQUE KEY attended_person_date (person_id, date),
        CONSTRAINT fk_attended_person
            FOREIGN KEY (person_id) REFERENCES people(id) ON DELETE SET NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """,
]


@dataclass
class Person:
    id: int
    full_name: str
    external_id: str | None
    role: str
    class_dept: str | None
    photo_path: str | None
    created_at: str


@dataclass
class AttendanceRow:
    id: int
    person_id: int | None
    name: str
    time: str
    date: str
    role: str | None = None
    external_id: str | None = None


class StoreError(Exception):
    pass


class Store:
    """Thin adapter over SQLite or MySQL with the same clerk-facing API."""

    def __init__(self, data_dir: Path, cfg: AppConfig):
        self.data_dir = Path(data_dir)
        self.cfg = cfg
        self.engine = cfg.engine if cfg.engine in ("sqlite", "mysql") else "sqlite"
        self._lock = threading.Lock()
        self._conn: Any = None
        self._param = "?" if self.engine == "sqlite" else "%s"
        self._connect()

    @property
    def location(self) -> str:
        if self.engine == "mysql":
            m = self.cfg.mysql
            return f"MySQL {m.user}@{m.host}:{m.port}/{m.database}"
        return str(db_path(self.data_dir))

    def close(self) -> None:
        with self._lock:
            if self._conn is not None:
                try:
                    self._conn.close()
                except Exception:
                    pass
                self._conn = None

    def reconnect(self, cfg: AppConfig) -> None:
        self.close()
        self.cfg = cfg
        self.engine = cfg.engine if cfg.engine in ("sqlite", "mysql") else "sqlite"
        self._param = "?" if self.engine == "sqlite" else "%s"
        self._connect()

    def _connect(self) -> None:
        if self.engine == "mysql":
            self._conn = _open_mysql(self.cfg)
        else:
            ensure_data_layout(self.data_dir)
            path = db_path(self.data_dir)
            self._conn = sqlite3.connect(str(path), check_same_thread=False)
            self._conn.row_factory = sqlite3.Row
            self._conn.execute("PRAGMA foreign_keys = ON")
        self._init_schema()

    def _init_schema(self) -> None:
        with self._lock:
            cur = self._conn.cursor()
            if self.engine == "sqlite":
                cur.executescript(SQLITE_SCHEMA)
            else:
                for stmt in MYSQL_SCHEMA:
                    cur.execute(stmt)
            self._conn.commit()

    def _execute(self, sql: str, params: Iterable[Any] = ()) -> Any:
        cur = self._conn.cursor()
        cur.execute(sql, tuple(params))
        return cur

    def _q(self, sql: str) -> str:
        return sql.replace("?", self._param)

    def add_person(
        self,
        full_name: str,
        external_id: str | None,
        role: str,
        class_dept: str | None,
        photo_path: str | None,
    ) -> Person:
        name = (full_name or "").strip()
        if not name:
            raise StoreError("Full name is required.")
        role = role if role in ROLES else "Staff"
        created = now().isoformat(timespec="seconds")
        with self._lock:
            cur = self._execute(
                self._q(
                    "INSERT INTO people (full_name, external_id, role, class_dept, photo_path, created_at) "
                    "VALUES (?, ?, ?, ?, ?, ?)"
                ),
                (
                    name,
                    _clean(external_id),
                    role,
                    _clean(class_dept),
                    _clean(photo_path),
                    created,
                ),
            )
            self._conn.commit()
            person_id = int(cur.lastrowid)
        return self.get_person(person_id)

    def update_person(
        self,
        person_id: int,
        full_name: str,
        external_id: str | None,
        role: str,
        class_dept: str | None,
        photo_path: str | None,
    ) -> Person:
        name = (full_name or "").strip()
        if not name:
            raise StoreError("Full name is required.")
        role = role if role in ROLES else "Staff"
        with self._lock:
            self._execute(
                self._q(
                    "UPDATE people SET full_name=?, external_id=?, role=?, class_dept=?, photo_path=? "
                    "WHERE id=?"
                ),
                (
                    name,
                    _clean(external_id),
                    role,
                    _clean(class_dept),
                    _clean(photo_path),
                    person_id,
                ),
            )
            self._conn.commit()
        person = self.get_person(person_id)
        if person is None:
            raise StoreError("Person not found.")
        return person

    def delete_person(self, person_id: int) -> None:
        with self._lock:
            self._execute(self._q("DELETE FROM people WHERE id=?"), (person_id,))
            self._conn.commit()

    def get_person(self, person_id: int) -> Person | None:
        with self._lock:
            cur = self._execute(self._q("SELECT * FROM people WHERE id=?"), (person_id,))
            row = cur.fetchone()
        return _person_from_row(row) if row is not None else None

    def list_people(self) -> list[Person]:
        with self._lock:
            cur = self._execute(
                "SELECT * FROM people ORDER BY full_name COLLATE NOCASE"
                if self.engine == "sqlite"
                else "SELECT * FROM people ORDER BY full_name"
            )
            rows = cur.fetchall()
        return [_person_from_row(row) for row in rows]

    def already_marked(self, person_id: int, day: str | None = None) -> AttendanceRow | None:
        day = day or today_iso()
        with self._lock:
            cur = self._execute(
                self._q("SELECT * FROM attended WHERE person_id=? AND date=?"),
                (person_id, day),
            )
            row = cur.fetchone()
        return _attended_from_row(row) if row is not None else None

    def mark_attendance(self, person: Person, day: str | None = None) -> tuple[str, AttendanceRow]:
        """One mark per person per day. Returns ('present'|'already', row)."""
        day = day or today_iso()
        existing = self.already_marked(person.id, day)
        if existing:
            return "already", existing
        marked_at = format_time_long()
        try:
            with self._lock:
                cur = self._execute(
                    self._q(
                        "INSERT INTO attended (person_id, name, time, date) VALUES (?, ?, ?, ?)"
                    ),
                    (person.id, person.full_name, marked_at, day),
                )
                self._conn.commit()
                row_id = int(cur.lastrowid)
        except Exception as exc:
            # Unique race: treat as already marked.
            existing = self.already_marked(person.id, day)
            if existing:
                return "already", existing
            raise StoreError(f"Could not save attendance: {exc}") from exc
        row = AttendanceRow(
            id=row_id,
            person_id=person.id,
            name=person.full_name,
            time=marked_at,
            date=day,
            role=person.role,
            external_id=person.external_id,
        )
        return "present", row

    def list_attendance(
        self,
        date_from: str | None = None,
        date_to: str | None = None,
        role: str | None = None,
        name_query: str | None = None,
    ) -> list[AttendanceRow]:
        sql = (
            "SELECT a.id, a.person_id, a.name, a.time, a.date, p.role, p.external_id "
            "FROM attended a LEFT JOIN people p ON p.id = a.person_id WHERE 1=1"
        )
        params: list[Any] = []
        if date_from:
            sql += " AND a.date >= ?"
            params.append(date_from)
        if date_to:
            sql += " AND a.date <= ?"
            params.append(date_to)
        if role and role in ROLES:
            sql += " AND p.role = ?"
            params.append(role)
        if name_query and name_query.strip():
            sql += " AND a.name LIKE ?"
            params.append(f"%{name_query.strip()}%")
        sql += " ORDER BY a.date DESC, a.time DESC"
        with self._lock:
            cur = self._execute(self._q(sql), params)
            rows = cur.fetchall()
        return [_attended_from_row(row) for row in rows]

    def count_people(self) -> int:
        with self._lock:
            cur = self._execute("SELECT COUNT(*) FROM people")
            row = cur.fetchone()
        return int(row[0])


def _clean(value: str | None) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _row_val(row: Any, key: str, index: int | None = None) -> Any:
    if isinstance(row, dict):
        return row.get(key)
    try:
        return row[key]
    except (KeyError, IndexError, TypeError):
        if index is not None:
            try:
                return row[index]
            except (KeyError, IndexError, TypeError):
                return None
        return None


def _person_from_row(row: Any) -> Person:
    return Person(
        id=int(_row_val(row, "id", 0)),
        full_name=str(_row_val(row, "full_name", 1) or ""),
        external_id=_clean(_row_val(row, "external_id", 2)),
        role=str(_row_val(row, "role", 3) or "Staff"),
        class_dept=_clean(_row_val(row, "class_dept", 4)),
        photo_path=_clean(_row_val(row, "photo_path", 5)),
        created_at=str(_row_val(row, "created_at", 6) or ""),
    )


def _attended_from_row(row: Any) -> AttendanceRow:
    person_id = _row_val(row, "person_id", 1)
    return AttendanceRow(
        id=int(_row_val(row, "id", 0)),
        person_id=int(person_id) if person_id is not None else None,
        name=str(_row_val(row, "name", 2) or ""),
        time=str(_row_val(row, "time", 3) or ""),
        date=str(_row_val(row, "date", 4) or ""),
        role=_clean(_row_val(row, "role", 5)),
        external_id=_clean(_row_val(row, "external_id", 6)),
    )


def _open_mysql(cfg: AppConfig) -> Any:
    try:
        import mysql.connector
    except ImportError as exc:
        raise StoreError(
            "MySQL support is optional. Install mysql-connector-python to use it."
        ) from exc
    m = cfg.mysql
    if not m.user or not m.database:
        raise StoreError("MySQL user and database are required.")
    try:
        conn = mysql.connector.connect(
            host=m.host or "127.0.0.1",
            port=int(m.port or 3306),
            user=m.user,
            password=m.password or "",
            database=m.database,
        )
    except Exception as exc:
        raise StoreError(f"Could not connect to MySQL: {exc}") from exc
    return conn


def mysql_available() -> bool:
    try:
        import mysql.connector  # noqa: F401
        return True
    except ImportError:
        return False


def test_mysql(cfg: AppConfig) -> str:
    conn = _open_mysql(cfg)
    try:
        cur = conn.cursor()
        cur.execute("SELECT 1")
        cur.fetchone()
    finally:
        conn.close()
    return "Connected."
