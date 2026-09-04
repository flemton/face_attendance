import os

import pytest


@pytest.mark.skipif(not os.environ.get("DISPLAY"), reason="No display")
def test_app_builds_and_switches(tmp_path):
    from face_attendance.app import FaceAttendanceApp

    app = FaceAttendanceApp(data_dir=tmp_path, start_screen="welcome")
    try:
        app.update_idletasks()
        assert app.winfo_width() >= 800
        for key in ("attendance", "staff", "log", "settings"):
            app.show(key)
            app.update_idletasks()
            assert app._current == key
        person = app.store.add_person("Ama Mensah", "A1", "Staff", None, None)
        kind, _ = app.store.mark_attendance(person, day="2026-09-04")
        assert kind == "present"
        app.show("log")
        app.update_idletasks()
    finally:
        app._on_close()
