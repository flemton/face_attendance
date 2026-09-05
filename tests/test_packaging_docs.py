from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def test_pack_docs_and_scripts_exist():
    expected = [
        ROOT / "docs" / "WINDOWS.md",
        ROOT / "docs" / "LINUX.md",
        ROOT / "docs" / "MACOS.md",
        ROOT / "packaging" / "FaceAttendance.spec",
        ROOT / "packaging" / "windows" / "build.ps1",
        ROOT / "packaging" / "linux" / "build.sh",
        ROOT / "packaging" / "linux" / "FaceAttendance.desktop",
        ROOT / "packaging" / "macos" / "build.sh",
    ]
    missing = [str(path.relative_to(ROOT)) for path in expected if not path.is_file()]
    assert missing == []


def test_readme_points_at_three_pack_docs():
    text = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "docs/WINDOWS.md" in text
    assert "docs/LINUX.md" in text
    assert "docs/MACOS.md" in text
    assert "Build for Windows / macOS / Linux" in text


def test_linux_and_macos_scripts_are_valid_bash():
    for rel in ("packaging/linux/build.sh", "packaging/macos/build.sh"):
        result = subprocess.run(
            ["bash", "-n", str(ROOT / rel)],
            check=False,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, result.stderr


def test_macos_script_refuses_linux():
    if sys.platform == "darwin":
        return
    result = subprocess.run(
        ["bash", str(ROOT / "packaging" / "macos" / "build.sh")],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0
    assert "must run on a Mac" in (result.stderr + result.stdout)
