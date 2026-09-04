"""First-run welcome. Spec copy is binding."""

from __future__ import annotations

import tkinter as tk
from tkinter import filedialog, messagebox

from face_attendance.camera import open_camera
from face_attendance.paths import default_data_dir, write_pointer
from face_attendance.theme import BONE_ALT, BORDER, F, INK, MUTE, NAVY, WHITE, draw_scan_face
from face_attendance.widgets import Card, FAButton, StepList


class WelcomeScreen(tk.Frame):
    def __init__(self, master, app) -> None:
        super().__init__(master, bg=BONE_ALT)
        self.app = app

        card = Card(self)
        card.place(relx=0.5, rely=0.5, anchor="center", width=460)
        body = card.body
        body.configure(padx=40, pady=32)

        icon = tk.Canvas(body, width=56, height=56, bg=WHITE, highlightthickness=0)
        icon.pack(pady=(8, 8))
        draw_scan_face(icon, 8, 8, 40, NAVY)

        tk.Label(body, text="Welcome", bg=WHITE, fg=INK, font=F(24, "bold")).pack()
        tk.Label(
            body,
            text="Local face attendance for schools and offices in Ghana.\nData stays on this computer.",
            bg=WHITE,
            fg=MUTE,
            font=F(11),
            justify=tk.CENTER,
        ).pack(pady=(8, 18))

        self.steps = StepList(
            body,
            ["Choose data folder", "Connect camera", "Register first person"],
        )
        self.steps.pack(fill=tk.X, pady=(0, 20))

        FAButton(body, "Continue", command=self._continue, variant="primary").pack(
            fill=tk.X, pady=(4, 8)
        )
        FAButton(body, "Skip for now", command=self._skip, variant="secondary").pack(fill=tk.X)

        foot = tk.Frame(body, bg=WHITE)
        foot.pack(fill=tk.X, pady=(20, 0))
        tk.Label(foot, text="i", bg=BORDER, fg=NAVY, font=F(9, "bold"), width=2).pack(
            side=tk.LEFT
        )
        tk.Label(
            foot,
            text="  No internet required. No cloud account.",
            bg=WHITE,
            fg=MUTE,
            font=F(9),
            anchor="w",
        ).pack(side=tk.LEFT)

        self.refresh()

    def refresh(self) -> None:
        self.steps.set_current(self._current_step())

    def _current_step(self) -> int:
        setup = self.app.cfg.setup
        if not setup.data_folder_chosen:
            return 1
        if not setup.camera_connected:
            return 2
        return 3

    def _continue(self) -> None:
        setup = self.app.cfg.setup
        if not setup.data_folder_chosen:
            self._choose_folder()
            return
        if not setup.camera_connected:
            self._connect_camera()
            return
        self.app.show("staff")

    def _choose_folder(self) -> None:
        chosen = filedialog.askdirectory(
            title="Choose data folder",
            initialdir=str(self.app.data_dir or default_data_dir()),
        )
        if not chosen:
            return
        self.app.use_data_dir(chosen, chosen_by_user=True)
        self.refresh()

    def _connect_camera(self) -> None:
        try:
            cap = open_camera(self.app.cfg.camera_index)
        except Exception as exc:
            messagebox.showerror("Connect camera", str(exc), parent=self)
            return
        cap.release()
        self.app.cfg.setup.camera_connected = True
        self.app.save_cfg()
        self.refresh()
        messagebox.showinfo(
            "Connect camera",
            "Camera is ready. Next, register the first person.",
            parent=self,
        )

    def _skip(self) -> None:
        self.app.cfg.setup.skipped = True
        self.app.save_cfg()
        write_pointer(self.app.data_dir)
        self.app.show("attendance")
