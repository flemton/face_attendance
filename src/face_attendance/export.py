"""CSV export (required) and a print-ready HTML sheet."""

from __future__ import annotations

import csv
import html
import os
import sys
import tempfile
import webbrowser
from pathlib import Path

from face_attendance import PRODUCT_NAME, VENDOR
from face_attendance.clock import format_date, format_time, now
from face_attendance.db import AttendanceRow


CSV_COLUMNS = ("Name", "ID", "Role", "Time", "Date")


def write_csv(path: Path, rows: list[AttendanceRow]) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(CSV_COLUMNS)
        for row in rows:
            writer.writerow(
                [
                    row.name,
                    row.external_id or "",
                    row.role or "",
                    format_time(row.time),
                    row.date,
                ]
            )
    return path


def write_print_html(
    rows: list[AttendanceRow],
    org_name: str = "",
    data_path: str = "",
) -> Path:
    title = org_name.strip() or PRODUCT_NAME
    generated = f"{format_date()} · {format_time(now())} Africa/Accra"
    body_rows = []
    for row in rows:
        body_rows.append(
            "<tr>"
            f"<td>{html.escape(row.name)}</td>"
            f"<td>{html.escape(row.external_id or '')}</td>"
            f"<td>{html.escape(row.role or '')}</td>"
            f"<td>{html.escape(format_time(row.time))}</td>"
            f"<td>{html.escape(row.date)}</td>"
            "</tr>"
        )
    if not body_rows:
        body_rows.append('<tr><td colspan="5">No records in this filter.</td></tr>')
    markup = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>{html.escape(title)} — attendance</title>
  <style>
    body {{ font-family: Segoe UI, Arial, sans-serif; color: #1A1A1A; margin: 32px; }}
    h1 {{ font-size: 20px; margin: 0 0 4px; }}
    p.meta {{ color: #6B7280; margin: 0 0 20px; font-size: 13px; }}
    table {{ border-collapse: collapse; width: 100%; }}
    th, td {{ border: 1px solid #E7E0D6; padding: 8px 10px; text-align: left; font-size: 13px; }}
    th {{ background: #F6F1EA; }}
    footer {{ margin-top: 24px; color: #6B7280; font-size: 12px; }}
    @media print {{ button {{ display: none; }} }}
  </style>
</head>
<body>
  <button onclick="window.print()">Print</button>
  <h1>{html.escape(title)}</h1>
  <p class="meta">{html.escape(PRODUCT_NAME)} by {html.escape(VENDOR)} · {html.escape(generated)}</p>
  <table>
    <thead><tr><th>Name</th><th>ID</th><th>Role</th><th>Time</th><th>Date</th></tr></thead>
    <tbody>
      {''.join(body_rows)}
    </tbody>
  </table>
  <footer>Stored on this computer{(': ' + html.escape(data_path)) if data_path else ''}.</footer>
</body>
</html>
"""
    handle = tempfile.NamedTemporaryFile(
        prefix="face-attendance-print-",
        suffix=".html",
        delete=False,
    )
    handle.write(markup.encode("utf-8"))
    handle.close()
    return Path(handle.name)


def open_print(rows: list[AttendanceRow], org_name: str = "", data_path: str = "") -> Path:
    path = write_print_html(rows, org_name=org_name, data_path=data_path)
    if sys.platform == "win32":
        try:
            os.startfile(str(path), "print")  # type: ignore[attr-defined]
            return path
        except OSError:
            pass
    webbrowser.open(path.as_uri())
    return path
