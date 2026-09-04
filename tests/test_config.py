from pathlib import Path

from face_attendance.config import default_config, load_config, save_config


def test_save_and_load_roundtrip(tmp_path: Path):
    cfg = default_config()
    cfg.org_name = "Tamale Senior High"
    cfg.strictness = "strict"
    cfg.setup.data_folder_chosen = True
    save_config(tmp_path, cfg)
    loaded = load_config(tmp_path)
    assert loaded.org_name == "Tamale Senior High"
    assert loaded.strictness == "strict"
    assert loaded.setup.data_folder_chosen is True
    assert loaded.engine == "sqlite"
    assert loaded.mysql.password == ""


def test_unknown_strictness_falls_back(tmp_path: Path):
    (tmp_path / "config.json").write_text('{"strictness": "psychic"}', encoding="utf-8")
    cfg = load_config(tmp_path)
    assert cfg.strictness == "simple"


def test_needs_welcome_until_complete_or_skipped(tmp_path: Path):
    cfg = default_config()
    assert cfg.needs_welcome() is True
    cfg.setup.skipped = True
    assert cfg.needs_welcome() is False
