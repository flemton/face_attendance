"""Take attendance — morning session, one mark per person per day."""

from __future__ import annotations

import tkinter as tk
from dataclasses import dataclass

import cv2
from PIL import Image, ImageTk

from face_attendance.camera import grab_frame, open_camera
from face_attendance.clock import format_date, format_time, today_iso
from face_attendance.db import Person
from face_attendance.paths import resolve_photo
from face_attendance.recognizer import (
    RecognitionUnavailable,
    encode_bgr_frame,
    match,
)
from face_attendance.theme import (
    BONE,
    BONE_ALT,
    BORDER,
    DANGER,
    F,
    INK,
    MUTE,
    NAVY,
    SUCCESS,
    WHITE,
)
from face_attendance.widgets import Card, FAButton, StatusBanner


@dataclass
class RailItem:
    name: str
    status: str
    time: str
    kind: str
    photo_path: str | None = None


class AttendanceScreen(tk.Frame):
    def __init__(self, master, app) -> None:
        super().__init__(master, bg=BONE_ALT)
        self.app = app
        self._cap = None
        self._job = None
        self._imgtk = None
        self._running = False
        self._paused = False
        self._frame_i = 0
        self._rail: list[RailItem] = []
        self._thumbs: list[ImageTk.PhotoImage] = []
        self._unknown_cool = 0

        header = tk.Frame(self, bg=BONE_ALT)
        header.pack(fill=tk.X, padx=28, pady=(22, 8))
        left = tk.Frame(header, bg=BONE_ALT)
        left.pack(side=tk.LEFT, fill=tk.X, expand=True)
        tk.Label(left, text="Take attendance", bg=BONE_ALT, fg=INK, font=F(22, "bold")).pack(
            anchor="w"
        )
        self.session_label = tk.Label(left, text="", bg=BONE_ALT, fg=MUTE, font=F(11))
        self.session_label.pack(anchor="w", pady=(4, 0))
        self.cam_pill = tk.Label(
            header,
            text="Camera: Local",
            bg=WHITE,
            fg=INK,
            font=F(9),
            padx=10,
            pady=5,
            highlightbackground=BORDER,
            highlightthickness=1,
        )
        self.cam_pill.pack(side=tk.RIGHT)

        body = tk.Frame(self, bg=BONE_ALT)
        body.pack(fill=tk.BOTH, expand=True, padx=28, pady=(0, 22))
        body.columnconfigure(0, weight=3)
        body.columnconfigure(1, weight=2)
        body.rowconfigure(0, weight=1)

        main = Card(body)
        main.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        hold = main.body
        hold.configure(padx=16, pady=16)
        self.video = tk.Label(hold, bg="#111827", text="Session stopped", fg="white")
        self.video.pack(fill=tk.BOTH, expand=True)
        self.status = StatusBanner(hold)
        self.status.pack(fill=tk.X, pady=(12, 12))
        self.status.set("Ready", "Start a morning session when people arrive.", "idle")
        controls = tk.Frame(hold, bg=WHITE)
        controls.pack(fill=tk.X)
        self.btn_start = FAButton(controls, "Start session", command=self.start, variant="primary")
        self.btn_start.pack(side=tk.LEFT, padx=(0, 8))
        self.btn_stop = FAButton(controls, "Stop", command=self.stop, variant="danger")
        self.btn_stop.pack(side=tk.LEFT, padx=(0, 8))
        self.btn_pause = FAButton(controls, "Pause", command=self.toggle_pause, variant="secondary")
        self.btn_pause.pack(side=tk.LEFT)

        rail_card = Card(body)
        rail_card.grid(row=0, column=1, sticky="nsew")
        rail = rail_card.body
        rail.configure(padx=14, pady=14)
        title = tk.Frame(rail, bg=WHITE)
        title.pack(fill=tk.X, pady=(0, 8))
        tk.Label(
            title, text="Today’s check-ins", bg=WHITE, fg=INK, font=F(12, "bold")
        ).pack(side=tk.LEFT)
        self.count_badge = tk.Label(
            title, text="0", bg=NAVY, fg=WHITE, font=F(9, "bold"), padx=8, pady=2
        )
        self.count_badge.pack(side=tk.RIGHT)
        self.rail_host = tk.Frame(rail, bg=WHITE)
        self.rail_host.pack(fill=tk.BOTH, expand=True)

    def on_show(self) -> None:
        self._refresh_header()
        self._draw_rail()
        self._load_today_rail()

    def on_hide(self) -> None:
        self.stop()

    def refresh(self) -> None:
        self._refresh_header()
        self._load_today_rail()

    def _refresh_header(self) -> None:
        self.session_label.configure(text=f"Morning attendance · {format_date()}")
        live = "Live · " if self._running and not self._paused else ""
        self.cam_pill.configure(text=f"{live}Camera: Local")

    def start(self) -> None:
        if self._running and self._paused:
            self._paused = False
            self.btn_pause.set_text("Pause")
            self._refresh_header()
            return
        if self._running:
            return
        try:
            self._cap = open_camera(self.app.cfg.camera_index)
        except Exception as exc:
            self.status.set("Camera", str(exc), "danger")
            return
        try:
            self.app.reload_encodings()
        except RecognitionUnavailable as exc:
            self._cap.release()
            self._cap = None
            self.status.set("Recognition unavailable", str(exc), "danger")
            return
        self._running = True
        self._paused = False
        self.btn_pause.set_text("Pause")
        self.app.cfg.setup.camera_connected = True
        self.app.save_cfg()
        self._refresh_header()
        self._tick()

    def stop(self) -> None:
        self._running = False
        self._paused = False
        if self._job is not None:
            try:
                self.after_cancel(self._job)
            except Exception:
                pass
            self._job = None
        if self._cap is not None:
            self._cap.release()
            self._cap = None
        self.video.configure(image="", text="Session stopped", fg="white")
        self._imgtk = None
        self.btn_pause.set_text("Pause")
        self._refresh_header()

    def toggle_pause(self) -> None:
        if not self._running:
            return
        self._paused = not self._paused
        self.btn_pause.set_text("Resume" if self._paused else "Pause")
        self._refresh_header()

    def _tick(self) -> None:
        if not self._running or self._cap is None:
            return
        frame = grab_frame(self._cap)
        if frame is not None:
            display = frame.copy()
            if not self._paused:
                self._frame_i += 1
                if self._frame_i % 6 == 0:
                    self._recognize(display)
                if self._unknown_cool > 0:
                    self._unknown_cool -= 1
            self._show(display)
        self._job = self.after(33, self._tick)

    def _recognize(self, display) -> None:
        try:
            faces = encode_bgr_frame(display)
        except RecognitionUnavailable as exc:
            self.status.set("Recognition unavailable", str(exc), "danger")
            self.stop()
            return
        if not faces:
            return
        for (top, right, bottom, left), encoding in faces:
            person = match(encoding, self.app.known, self.app.cfg.strictness)
            if person is None:
                cv2.rectangle(display, (left, top), (right, bottom), (180, 180, 180), 2)
                cv2.putText(
                    display, "Unknown", (left, max(20, top - 8)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (180, 180, 180), 2,
                )
                self.status.set("Unknown — not marked", "", "unknown")
                if self._unknown_cool == 0:
                    self._push_rail(RailItem("Unknown", "Not marked", format_time(), "unknown"))
                    self._unknown_cool = 40
                continue
            color = (78, 127, 27)
            cv2.rectangle(display, (left, top), (right, bottom), color, 2)
            cv2.putText(
                display, person.full_name, (left, max(20, top - 8)),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2,
            )
            self._mark(person)

    def _mark(self, person: Person) -> None:
        kind, row = self.app.store.mark_attendance(person)
        when = format_time(row.time)
        if kind == "already":
            self.status.set("Already marked today", f"{person.full_name} · {when}", "already")
            return
        self.status.set(f"Present · {when}", person.full_name, "success")
        self._push_rail(
            RailItem(
                name=person.full_name,
                status="Present",
                time=when,
                kind="present",
                photo_path=person.photo_path,
            )
        )

    def _push_rail(self, item: RailItem) -> None:
        if item.kind == "present":
            self._rail = [x for x in self._rail if not (x.kind == "present" and x.name == item.name)]
        self._rail.insert(0, item)
        self._rail = self._rail[:40]
        self._draw_rail()

    def _load_today_rail(self) -> None:
        rows = self.app.store.list_attendance(date_from=today_iso(), date_to=today_iso())
        presents = [
            RailItem(
                name=row.name,
                status="Present",
                time=format_time(row.time),
                kind="present",
            )
            for row in rows
        ]
        unknowns = [item for item in self._rail if item.kind == "unknown"]
        self._rail = presents + unknowns
        self._draw_rail()

    def _draw_rail(self) -> None:
        for child in self.rail_host.winfo_children():
            child.destroy()
        self._thumbs.clear()
        marked = sum(1 for item in self._rail if item.kind == "present")
        self.count_badge.configure(text=str(marked))
        if not self._rail:
            tk.Label(
                self.rail_host,
                text="No check-ins yet today.",
                bg=WHITE,
                fg=MUTE,
                font=F(10),
            ).pack(anchor="w")
            return
        canvas = tk.Canvas(self.rail_host, bg=WHITE, highlightthickness=0)
        scroll = tk.Scrollbar(self.rail_host, orient=tk.VERTICAL, command=canvas.yview)
        inner = tk.Frame(canvas, bg=WHITE)
        inner.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=inner, anchor="nw")
        canvas.configure(yscrollcommand=scroll.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        for item in self._rail:
            self._rail_row(inner, item)

    def _rail_row(self, host: tk.Frame, item: RailItem) -> None:
        row = tk.Frame(host, bg=WHITE)
        row.pack(fill=tk.X, pady=6)
        thumb = tk.Label(row, bg=BONE, width=4, height=2)
        thumb.pack(side=tk.LEFT, padx=(0, 8))
        path = resolve_photo(self.app.data_dir, item.photo_path) if item.photo_path else None
        if path is not None and path.is_file():
            image = Image.open(path).convert("RGB").resize((32, 32))
            photo = ImageTk.PhotoImage(image)
            self._thumbs.append(photo)
            thumb.configure(image=photo, width=32, height=32)
        box = tk.Frame(row, bg=WHITE)
        box.pack(side=tk.LEFT, fill=tk.X, expand=True)
        tk.Label(box, text=item.name, bg=WHITE, fg=INK, font=F(10, "bold"), anchor="w").pack(fill=tk.X)
        color = SUCCESS if item.kind == "present" else MUTE
        tk.Label(box, text=item.status, bg=WHITE, fg=color, font=F(9), anchor="w").pack(fill=tk.X)
        tk.Label(row, text=item.time, bg=WHITE, fg=MUTE, font=F(9)).pack(side=tk.RIGHT)

    def _show(self, frame) -> None:
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image = Image.fromarray(rgb)
        image.thumbnail((720, 480))
        self._imgtk = ImageTk.PhotoImage(image)
        self.video.configure(image=self._imgtk, text="")


# imported tokens reserved for later live-dot styling
_ = (DANGER,)
