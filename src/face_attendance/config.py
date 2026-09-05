"""config.json in the chosen data folder. No credentials are shipped in source."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path

from face_attendance.paths import config_path, ensure_data_layout

ROLES = ("Staff", "Teacher", "Student", "Other")
STRICTNESS = ("strict", "simple", "loose")
ENGINES = ("sqlite", "mysql")


@dataclass
class MysqlSettings:
    host: str = "127.0.0.1"
    port: int = 3306
    user: str = ""
    password: str = ""
    database: str = "attendancedb"


@dataclass
class SetupState:
    data_folder_chosen: bool = False
    camera_connected: bool = False
    first_person_registered: bool = False
    skipped: bool = False


@dataclass
class AppConfig:
    org_name: str = ""
    camera_index: int = 0
    strictness: str = "simple"
    language: str = "en"
    engine: str = "sqlite"
    mysql: MysqlSettings = field(default_factory=MysqlSettings)
    setup: SetupState = field(default_factory=SetupState)
    mysql_import_done: bool = False

    def needs_welcome(self) -> bool:
        if self.setup.skipped:
            return False
        setup = self.setup
        return not (
            setup.data_folder_chosen
            and setup.camera_connected
            and setup.first_person_registered
        )


def default_config() -> AppConfig:
    return AppConfig()


def _mysql_from_dict(raw: dict | None) -> MysqlSettings:
    raw = raw or {}
    port = raw.get("port", 3306)
    try:
        port = int(port)
    except (TypeError, ValueError):
        port = 3306
    return MysqlSettings(
        host=str(raw.get("host") or "127.0.0.1"),
        port=port,
        user=str(raw.get("user") or ""),
        password=str(raw.get("password") or ""),
        database=str(raw.get("database") or "attendancedb"),
    )


def _setup_from_dict(raw: dict | None) -> SetupState:
    raw = raw or {}
    return SetupState(
        data_folder_chosen=bool(raw.get("data_folder_chosen")),
        camera_connected=bool(raw.get("camera_connected")),
        first_person_registered=bool(raw.get("first_person_registered")),
        skipped=bool(raw.get("skipped")),
    )


def load_config(data_dir: Path) -> AppConfig:
    path = config_path(data_dir)
    if not path.is_file():
        cfg = default_config()
        save_config(data_dir, cfg)
        return cfg
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return default_config()
    if not isinstance(raw, dict):
        return default_config()
    strictness = str(raw.get("strictness") or "simple").lower()
    if strictness not in STRICTNESS:
        strictness = "simple"
    engine = str(raw.get("engine") or "sqlite").lower()
    if engine not in ENGINES:
        engine = "sqlite"
    language = str(raw.get("language") or "en")
    if language.lower() not in ("en", "english"):
        language = "en"
    else:
        language = "en"
    try:
        camera_index = int(raw.get("camera_index") or 0)
    except (TypeError, ValueError):
        camera_index = 0
    return AppConfig(
        org_name=str(raw.get("org_name") or ""),
        camera_index=max(0, camera_index),
        strictness=strictness,
        language=language,
        engine=engine,
        mysql=_mysql_from_dict(raw.get("mysql") if isinstance(raw.get("mysql"), dict) else {}),
        setup=_setup_from_dict(raw.get("setup") if isinstance(raw.get("setup"), dict) else {}),
        mysql_import_done=bool(raw.get("mysql_import_done")),
    )


def save_config(data_dir: Path, cfg: AppConfig) -> Path:
    ensure_data_layout(data_dir)
    path = config_path(data_dir)
    payload = {
        "org_name": cfg.org_name,
        "camera_index": cfg.camera_index,
        "strictness": cfg.strictness,
        "language": cfg.language,
        "engine": cfg.engine,
        "mysql": asdict(cfg.mysql),
        "setup": asdict(cfg.setup),
        "mysql_import_done": cfg.mysql_import_done,
    }
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return path
