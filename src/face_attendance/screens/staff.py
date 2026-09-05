"""Register staff — capture a photo into {data}/faces/ and save the person."""

from __future__ import annotations

import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox

import cv2
from PIL import Image, ImageTk

from face_attendance.camera import grab_frame, open_camera
from face_attendance.clock import format_date
from face_attendance.config import ROLES
from face_attendance.db import Person, StoreError
from face_attendance.paths import faces_dir, resolve_photo
from face_attendance.recognizer import RecognitionUnavailable, encode_image_file
from face_attendance.theme import BONE, BONE_ALT, BORDER, F, INK, MUTE, NAVY, SUCCESS, WHITE
from face_attendance.widgets import Card, FAButton, LabeledField, LabeledSelect


class StaffScreen(tk.Frame):
    def __init__(self, master, app) -> None:
        super().__init__(master, bg=BONE_ALT)
        self.app = app
        self._cap = None
        self._preview_job = None
        self._photo_imgtk = None
        self._list_thumbs: list[ImageTk.PhotoImage] = []
        self._captured: Image.Image | None = None
        self._editing: Person | None = None
        self._existing_photo: str | None = None

        header = tk.Frame(self, bg=BONE_ALT)
        header.pack(fill=tk.X, padx=28, pady=(22, 8))
        tk.Label(header, text="Register staff", bg=BONE_ALT, fg=INK, font=F(22, "bold")).pack(
            anchor="w"
        )
        tk.Label(
            header,
            text="Capture a photo and fill in the details.",
            bg=BONE_ALT,
            fg=MUTE,
            font=F(11),
        ).pack(anchor="w", pady=(4, 0))

        top = tk.Frame(self, bg=BONE_ALT)
        top.pack(fill=tk.BOTH, expand=False, padx=28, pady=(8, 8))
        top.columnconfigure(0, weight=1, uniform="col")
        top.columnconfigure(1, weight=1, uniform="col")

        cam_card = Card(top)
        cam_card.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        cam = cam_card.body
        cam.configure(padx=16, pady=16)
        self.preview = tk.Label(cam, bg="#111827", width=48, height=16, text="")
        self.preview.pack(fill=tk.BOTH, expand=True)
        tip = tk.Frame(cam, bg=BONE)
        tip.pack(fill=tk.X, pady=(10, 10))
        tk.Label(
            tip,
            text="  Stand facing the camera. Good light. One face only.",
            bg=BONE,
            fg=INK,
            font=F(9),
            anchor="w",
            padx=8,
            pady=8,
        ).pack(fill=tk.X)
        FAButton(cam, "Capture photo", command=self._capture, variant="primary").pack(fill=tk.X)
        FAButton(
            cam, "Use photo file", command=self._pick_file, variant="secondary"
        ).pack(fill=tk.X, pady=(8, 0))

        form_card = Card(top)
        form_card.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        form = form_card.body
        form.configure(padx=18, pady=18)
        self.name = LabeledField(form, "Full name", required=True)
        self.name.pack(fill=tk.X, pady=(0, 10))
        self.ext_id = LabeledField(form, "Staff or student ID", hint="Optional")
        self.ext_id.pack(fill=tk.X, pady=(0, 10))
        self.role = LabeledSelect(
            form,
            "Role",
            ROLES,
            hint="Staff, teacher, student or other.",
            required=True,
        )
        self.role.set("Staff")
        self.role.pack(fill=tk.X, pady=(0, 10))
        self.dept = LabeledField(form, "Class or department", hint="Optional")
        self.dept.pack(fill=tk.X, pady=(0, 16))
        btns = tk.Frame(form, bg=WHITE)
        btns.pack(fill=tk.X, side=tk.BOTTOM)
        FAButton(btns, "Save person", command=self._save, variant="amber").pack(
            fill=tk.X, pady=(0, 8)
        )
        FAButton(btns, "Cancel", command=self._cancel, variant="secondary").pack(fill=tk.X)

        list_card = Card(self)
        list_card.pack(fill=tk.BOTH, expand=True, padx=28, pady=(4, 22))
        lst = list_card.body
        lst.configure(padx=16, pady=12)
        tk.Label(lst, text="Already registered", bg=WHITE, fg=INK, font=F(12, "bold")).pack(
            anchor="w", pady=(0, 8)
        )
        self.list_host = tk.Frame(lst, bg=WHITE)
        self.list_host.pack(fill=tk.BOTH, expand=True)
        self._empty = tk.Label(
            self.list_host,
            text="No one registered yet.",
            bg=WHITE,
            fg=MUTE,
            font=F(11),
        )

    def on_show(self) -> None:
        self._start_camera()
        self._reload_list()

    def on_hide(self) -> None:
        self._stop_camera()

    def refresh(self) -> None:
        self._reload_list()

    def _start_camera(self) -> None:
        if self._cap is not None:
            return
        try:
            self._cap = open_camera(self.app.cfg.camera_index)
        except Exception:
            self._cap = None
            self.preview.configure(
                text="Camera not available.\nUse photo file or check Settings.",
                fg="white",
                image="",
                compound=tk.CENTER,
            )
            return
        self._tick()

    def _stop_camera(self) -> None:
        if self._preview_job is not None:
            try:
                self.after_cancel(self._preview_job)
            except Exception:
                pass
            self._preview_job = None
        if self._cap is not None:
            self._cap.release()
            self._cap = None

    def _tick(self) -> None:
        if self._cap is None or self._captured is not None:
            return
        frame = grab_frame(self._cap)
        if frame is not None:
            self._show_bgr(frame)
        self._preview_job = self.after(33, self._tick)

    def _show_bgr(self, frame) -> None:
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image = Image.fromarray(rgb)
        self._set_preview(image)

    def _set_preview(self, image: Image.Image) -> None:
        fitted = _fit(image, 420, 280)
        self._photo_imgtk = ImageTk.PhotoImage(fitted)
        self.preview.configure(image=self._photo_imgtk, text="")

    def _capture(self) -> None:
        if self._cap is None:
            messagebox.showerror(
                "Capture photo",
                "Camera is not open. Use a photo file or test the camera in Settings.",
                parent=self,
            )
            return
        frame = grab_frame(self._cap)
        if frame is None:
            messagebox.showerror("Capture photo", "Could not read a frame.", parent=self)
            return
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        self._captured = Image.fromarray(rgb)
        self._set_preview(self._captured)

    def _pick_file(self) -> None:
        path = filedialog.askopenfilename(
            title="Use photo file",
            filetypes=[("Photos", "*.jpg *.jpeg *.png")],
            parent=self,
        )
        if not path:
            return
        image = Image.open(path).convert("RGB")
        self._captured = image
        self._set_preview(image)

    def _save(self) -> None:
        name = self.name.get()
        if not name:
            messagebox.showerror("Save person", "Full name is required.", parent=self)
            return
        if self._captured is None and not self._existing_photo:
            messagebox.showerror(
                "Save person",
                "Capture a photo or choose a photo file first.",
                parent=self,
            )
            return
        try:
            if self._editing:
                person = self.app.store.update_person(
                    self._editing.id,
                    full_name=name,
                    external_id=self.ext_id.get() or None,
                    role=self.role.get() or "Staff",
                    class_dept=self.dept.get() or None,
                    photo_path=self._editing.photo_path,
                )
            else:
                person = self.app.store.add_person(
                    full_name=name,
                    external_id=self.ext_id.get() or None,
                    role=self.role.get() or "Staff",
                    class_dept=self.dept.get() or None,
                    photo_path=None,
                )
            photo_rel = self._existing_photo
            if self._captured is not None:
                photo_rel = self._write_face(person.id, self._captured)
                person = self.app.store.update_person(
                    person.id,
                    full_name=person.full_name,
                    external_id=person.external_id,
                    role=person.role,
                    class_dept=person.class_dept,
                    photo_path=photo_rel,
                )
                self._check_face(faces_dir(self.app.data_dir) / Path(photo_rel).name)
            if not self.app.cfg.setup.first_person_registered:
                self.app.cfg.setup.first_person_registered = True
                self.app.save_cfg()
            self.app.reload_encodings()
            self._cancel()
            self._reload_list()
        except StoreError as exc:
            messagebox.showerror("Save person", str(exc), parent=self)
        except OSError as exc:
            messagebox.showerror("Save person", f"Could not save the photo: {exc}", parent=self)

    def _write_face(self, person_id: int, image: Image.Image) -> str:
        folder = faces_dir(self.app.data_dir)
        folder.mkdir(parents=True, exist_ok=True)
        path = folder / f"{person_id}.jpg"
        image.convert("RGB").save(path, format="JPEG", quality=92)
        cached = path.with_suffix(".npy")
        if cached.is_file():
            cached.unlink()
        return f"faces/{path.name}"

    def _check_face(self, path: Path) -> None:
        try:
            encoding = encode_image_file(path)
        except RecognitionUnavailable:
            return
        if encoding is None:
            messagebox.showwarning(
                "Save person",
                "No face found in the photo. Attendance may not recognise this person. "
                "Capture again in good light, one face only.",
                parent=self,
            )

    def _cancel(self) -> None:
        self._editing = None
        self._captured = None
        self._existing_photo = None
        self.name.set("")
        self.ext_id.set("")
        self.role.set("Staff")
        self.dept.set("")
        if self._cap is not None:
            self._tick()
        else:
            self.preview.configure(image="", text="Camera not available.")

    def _edit(self, person: Person) -> None:
        self._editing = person
        self._captured = None
        self._existing_photo = person.photo_path
        self.name.set(person.full_name)
        self.ext_id.set(person.external_id or "")
        self.role.set(person.role if person.role in ROLES else "Staff")
        self.dept.set(person.class_dept or "")
        path = resolve_photo(self.app.data_dir, person.photo_path)
        if path is not None and path.is_file():
            image = Image.open(path).convert("RGB")
            self._set_preview(image)

    def _delete(self, person: Person) -> None:
        if not messagebox.askyesno(
            "Delete",
            f"Remove {person.full_name} from this computer? Attendance history stays in the log.",
            parent=self,
        ):
            return
        self.app.store.delete_person(person.id)
        path = resolve_photo(self.app.data_dir, person.photo_path)
        if path is not None and path.is_file():
            try:
                path.unlink()
            except OSError:
                pass
            cached = path.with_suffix(".npy")
            if cached.is_file():
                try:
                    cached.unlink()
                except OSError:
                    pass
        if self._editing and self._editing.id == person.id:
            self._cancel()
        self.app.reload_encodings()
        self._reload_list()

    def _reload_list(self) -> None:
        for child in self.list_host.winfo_children():
            child.destroy()
        self._list_thumbs.clear()
        people = self.app.store.list_people()
        if not people:
            tk.Label(
                self.list_host,
                text="No one registered yet.",
                bg=WHITE,
                fg=MUTE,
                font=F(11),
            ).pack(anchor="w")
            return
        canvas = tk.Canvas(self.list_host, bg=WHITE, highlightthickness=0, height=180)
        scroll = tk.Scrollbar(self.list_host, orient=tk.VERTICAL, command=canvas.yview)
        inner = tk.Frame(canvas, bg=WHITE)
        inner.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=inner, anchor="nw")
        canvas.configure(yscrollcommand=scroll.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        for person in people:
            self._row(inner, person)

    def _row(self, host: tk.Frame, person: Person) -> None:
        row = tk.Frame(host, bg=WHITE, highlightbackground=BORDER, highlightthickness=1)
        row.pack(fill=tk.X, pady=4)
        thumb = tk.Label(row, bg=BONE, width=6, height=3)
        thumb.pack(side=tk.LEFT, padx=8, pady=8)
        path = resolve_photo(self.app.data_dir, person.photo_path)
        if path is not None and path.is_file():
            image = Image.open(path).convert("RGB").resize((40, 40))
            photo = ImageTk.PhotoImage(image)
            self._list_thumbs.append(photo)
            thumb.configure(image=photo, width=40, height=40)
        info = tk.Frame(row, bg=WHITE)
        info.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=8, pady=8)
        tk.Label(info, text=person.full_name, bg=WHITE, fg=INK, font=F(11, "bold"), anchor="w").pack(
            fill=tk.X
        )
        bits = [person.external_id or "No ID", person.role]
        if person.class_dept:
            bits.append(person.class_dept)
        tk.Label(info, text=" · ".join(bits), bg=WHITE, fg=MUTE, font=F(9), anchor="w").pack(fill=tk.X)
        created = person.created_at[:10] if person.created_at else ""
        if created:
            tk.Label(
                info, text=format_date(created), bg=WHITE, fg=MUTE, font=F(9), anchor="w"
            ).pack(fill=tk.X)
        actions = tk.Frame(row, bg=WHITE)
        actions.pack(side=tk.RIGHT, padx=8)
        tk.Button(
            actions,
            text="Edit",
            command=lambda p=person: self._edit(p),
            relief=tk.FLAT,
            bg=WHITE,
            fg=NAVY,
            font=F(9, "bold"),
            cursor="hand2",
        ).pack(side=tk.LEFT, padx=4)
        tk.Button(
            actions,
            text="Delete",
            command=lambda p=person: self._delete(p),
            relief=tk.FLAT,
            bg=WHITE,
            fg="#B42318",
            font=F(9, "bold"),
            cursor="hand2",
        ).pack(side=tk.LEFT, padx=4)


def _fit(image: Image.Image, width: int, height: int) -> Image.Image:
    copy = image.copy()
    copy.thumbnail((width, height))
    return copy


# Keep SUCCESS imported for possible live-dot reuse without flake unused in future
_ = SUCCESS
