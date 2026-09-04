from pathlib import Path

from face_attendance.db import AttendanceRow
from face_attendance.export import write_csv, write_print_html


def _row() -> AttendanceRow:
    return AttendanceRow(
        id=1,
        person_id=1,
        name="Kwame Mensah",
        time="07:45:00",
        date="2026-09-04",
        role="Staff",
        external_id="EMP001",
    )


def test_csv_has_required_columns(tmp_path: Path):
    path = write_csv(tmp_path / "out.csv", [_row()])
    text = path.read_text(encoding="utf-8-sig")
    lines = text.strip().splitlines()
    assert lines[0] == "Name,ID,Role,Time,Date"
    assert "Kwame Mensah" in lines[1]
    assert "EMP001" in lines[1]
    assert "07:45" in lines[1]


def test_print_html_contains_rows(tmp_path: Path):
    path = write_print_html([_row()], org_name="Test School", data_path=str(tmp_path))
    html = path.read_text(encoding="utf-8")
    assert "Kwame Mensah" in html
    assert "Test School" in html
    assert "Africa/Accra" in html
    path.unlink()
