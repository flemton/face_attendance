"""Desktop shell — 1280×800, binding nav only."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import tkinter as tk

from face_attendance import WINDOW_TITLE
from face_attendance.config import AppConfig, load_config, save_config
from face_attendance.db import Store, StoreError
from face_attendance.paths import ensure_data_layout, resolve_data_dir, write_pointer
from face_attendance.recognizer import RecognitionUnavailable, load_known
from face_attendance.screens.attendance import AttendanceScreen
from face_attendance.screens.log import LogScreen
from face_attendance.screens.settings import SettingsScreen
from face_attendance.screens.staff import StaffScreen
from face_attendance.screens.welcome import WelcomeScreen
from face_attendance.theme import BONE_ALT, NAVY, WINDOW_H, WINDOW_W, apply_root
from face_attendance.widgets import Sidebar


class FaceAttendanceApp(tk.Tk):
    def __init__(
        self,
        data_dir: str | Path | None = None,
        start_screen: str | None = None,
        force_welcome: bool = False,
    ) -> None:
        super().__init__()
        self.title(WINDOW_TITLE)
        self.geometry(f"{WINDOW_W}x{WINDOW_H}")
        self.minsize(1100, 700)
        self.configure(bg=BONE_ALT)
        _windows_dpi()
        apply_root(self)
        self._center()

        self.data_dir = ensure_data_layout(resolve_data_dir(data_dir))
        write_pointer(self.data_dir)
        self.cfg: AppConfig = load_config(self.data_dir)
        try:
            self.store = Store(self.data_dir, self.cfg)
        except StoreError:
            self.cfg.engine = "sqlite"
            self.store = Store(self.data_dir, self.cfg)
        self.known = []
        self._current = ""
        self._force_welcome = force_welcome

        shell = tk.Frame(self, bg=BONE_ALT)
        shell.pack(fill=tk.BOTH, expand=True)
        self.sidebar = Sidebar(shell, on_nav=self.show)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)
        self.main = tk.Frame(shell, bg=BONE_ALT)
        self.main.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.screens = {
            "welcome": WelcomeScreen(self.main, self),
            "attendance": AttendanceScreen(self.main, self),
            "staff": StaffScreen(self.main, self),
            "log": LogScreen(self.main, self),
            "settings": SettingsScreen(self.main, self),
        }
        for frame in self.screens.values():
            frame.place(relx=0, rely=0, relwidth=1, relheight=1)

        self.protocol("WM_DELETE_WINDOW", self._on_close)
        initial = start_screen
        if initial is None:
            initial = "welcome" if (force_welcome or self.cfg.needs_welcome()) else "attendance"
        self.show(initial)

    def _center(self) -> None:
        self.update_idletasks()
        w = WINDOW_W
        h = WINDOW_H
        x = max(0, (self.winfo_screenwidth() - w) // 2)
        y = max(0, (self.winfo_screenheight() - h) // 2)
        self.geometry(f"{w}x{h}+{x}+{y}")

    def save_cfg(self) -> None:
        save_config(self.data_dir, self.cfg)

    def use_data_dir(self, folder: str | Path, chosen_by_user: bool = False) -> None:
        self.store.close()
        self.data_dir = ensure_data_layout(Path(folder))
        write_pointer(self.data_dir)
        self.cfg = load_config(self.data_dir)
        if chosen_by_user:
            self.cfg.setup.data_folder_chosen = True
            save_config(self.data_dir, self.cfg)
        try:
            self.store = Store(self.data_dir, self.cfg)
        except StoreError:
            self.cfg.engine = "sqlite"
            self.store = Store(self.data_dir, self.cfg)
        self.reload_encodings()
        for screen in self.screens.values():
            if hasattr(screen, "refresh"):
                screen.refresh()

    def reload_encodings(self) -> None:
        try:
            self.known = load_known(self.store.list_people(), self.data_dir)
        except RecognitionUnavailable:
            self.known = []

    def show(self, key: str) -> None:
        if key not in self.screens:
            key = "attendance"
        previous = self.screens.get(self._current)
        if previous is not None and hasattr(previous, "on_hide"):
            previous.on_hide()
        self._current = key
        frame = self.screens[key]
        frame.lift()
        if hasattr(frame, "on_show"):
            frame.on_show()
        if hasattr(frame, "refresh"):
            frame.refresh()
        if key != "welcome":
            self.sidebar.set_active(key)
        else:
            self.sidebar.set_active("")

    def _on_close(self) -> None:
        current = self.screens.get(self._current)
        if current is not None and hasattr(current, "on_hide"):
            current.on_hide()
        self.store.close()
        self.destroy()


def _windows_dpi() -> None:
    if sys.platform != "win32":
        return
    try:
        import ctypes

        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        try:
            import ctypes

            ctypes.windll.user32.SetProcessDPIAware()
        except Exception:
            pass


def main(argv: list[str] | None = None, start_screen: str | None = None) -> int:
    parser = argparse.ArgumentParser(description="Face Attendance by Flemton Tech")
    parser.add_argument("--data-dir", help="Use this data folder (and persist the pointer)")
    parser.add_argument(
        "--screen",
        choices=("welcome", "attendance", "staff", "log", "settings"),
        help="Open this screen",
    )
    parser.add_argument("--welcome", action="store_true", help="Show first-run even if skipped")
    args = parser.parse_args(argv)
    screen = start_screen or args.screen
    app = FaceAttendanceApp(
        data_dir=args.data_dir,
        start_screen=screen,
        force_welcome=args.welcome,
    )
    app.mainloop()
    return 0


# Sidebar uses navy; keep import used for future chrome tweaks
_ = NAVY
