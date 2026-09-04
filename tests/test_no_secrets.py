from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKIP_DIRS = {".git", ".venv", "venv", "dist", "build", "__pycache__", ".pytest_cache"}
FORBIDDEN = (
    "qwertyui",
    "password='root'",
    'password="root"',
    "password='qwerty",
    'password="qwerty',
)


def test_source_has_no_shipped_mysql_password():
    hits = []
    for path in ROOT.rglob("*"):
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if path.suffix.lower() not in {".py", ".md", ".txt", ".sql", ".json", ".ps1", ".iss", ".spec", ".yml"}:
            continue
        if path.name == "test_no_secrets.py":
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        for token in FORBIDDEN:
            if token in text:
                hits.append(f"{path.relative_to(ROOT)}: {token}")
    assert hits == []
