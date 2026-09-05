from datetime import date, datetime

from face_attendance.clock import ACCRA, format_date, format_time, now, today_iso


def test_now_is_africa_accra():
    assert now().tzinfo == ACCRA


def test_format_date_without_leading_zero():
    assert format_date(date(2026, 9, 4)) == "4 Sep 2026"
    assert format_date("2026-09-04") == "4 Sep 2026"


def test_format_time_hhmm():
    assert format_time("7:42:10") == "07:42"
    assert format_time(datetime(2026, 9, 4, 7, 42, tzinfo=ACCRA)) == "07:42"


def test_today_iso_shape():
    value = today_iso()
    assert len(value) == 10
    assert value[4] == "-" and value[7] == "-"
