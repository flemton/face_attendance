"""Settings — org, camera, data folder, strictness, English, About, Advanced MySQL."""

from __future__ import annotations

import tkinter as tk
from tkinter import filedialog, messagebox

from face_attendance import BYLINE, PRODUCT_NAME, SELL_LINE, VENDOR, __version__
from face_attendance.camera import list_cameras, open_camera
from face_attendance.config import STRICTNESS
from face_attendance.db import StoreError, mysql_available, test_mysql
from face_attendance.legacy import detect_legacy_mysql, import_legacy_mysql
from face_attendance.theme import BONE, BONE_ALT, BORDER, F, INK, MUTE, NAVY, WHITE
from face_attendance.widgets import Card, FAButton, LabeledField, LabeledSelect


class SettingsScreen(tk.Frame):
    def __init__(self, master, app) -> None:
        super().__init__(master, bg=BONE_ALT)
        self.app = app
        self._advanced_open = False

        header = tk.Frame(self, bg=BONE_ALT)
        header.pack(fill=tk.X, padx=28, pady=(22, 8))
        tk.Label(header, text="Settings", bg=BONE_ALT, fg=INK, font=F(22, "bold")).pack(anchor="w")

        canvas = tk.Canvas(self, bg=BONE_ALT, highlightthickness=0)
        scroll = tk.Scrollbar(self, orient=tk.VERTICAL, command=canvas.yview)
        self.form = tk.Frame(canvas, bg=BONE_ALT)
        form_id = canvas.create_window((0, 0), window=self.form, anchor="nw")

        def _sync_scroll(_event=None) -> None:
            canvas.configure(scrollregion=canvas.bbox("all"))
            canvas.itemconfigure(form_id, width=canvas.winfo_width())

        self.form.bind("<Configure>", _sync_scroll)
        canvas.bind("<Configure>", _sync_scroll)
        canvas.configure(yscrollcommand=scroll.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(28, 0), pady=(0, 16))
        scroll.pack(side=tk.RIGHT, fill=tk.Y, pady=(0, 16), padx=(0, 12))

        card = Card(self.form)
        card.pack(fill=tk.X, pady=(0, 12))
        body = card.body
        body.configure(padx=20, pady=18)

        self.org = LabeledField(
            body, "Organisation name", hint="The name of your organisation or institution."
        )
        self.org.pack(fill=tk.X, pady=(0, 14))

        cam_row = tk.Frame(body, bg=WHITE)
        cam_row.pack(fill=tk.X, pady=(0, 14))
        self.camera = LabeledSelect(cam_row, "Camera", ["Camera 0"])
        self.camera.pack(side=tk.LEFT, fill=tk.X, expand=True)
        FAButton(cam_row, "Test camera", command=self._test_camera, variant="secondary").pack(
            side=tk.LEFT, padx=(10, 0), pady=(18, 0)
        )

        folder_row = tk.Frame(body, bg=WHITE)
        folder_row.pack(fill=tk.X, pady=(0, 14))
        self.folder = LabeledField(folder_row, "Data folder")
        self.folder.entry.configure(state="readonly")
        self.folder.pack(side=tk.LEFT, fill=tk.X, expand=True)
        FAButton(folder_row, "Change", command=self._change_folder, variant="secondary").pack(
            side=tk.LEFT, padx=(10, 0), pady=(18, 0)
        )

        tk.Label(
            body, text="Recognition sensitivity", bg=WHITE, fg=INK, font=F(10, "bold"), anchor="w"
        ).pack(fill=tk.X)
        tk.Label(
            body,
            text="Strict needs a closer match. Loose is more forgiving. Simple is the default.",
            bg=WHITE,
            fg=MUTE,
            font=F(9),
            anchor="w",
        ).pack(fill=tk.X, pady=(2, 6))
        self.strictness = tk.StringVar(value="simple")
        radios = tk.Frame(body, bg=WHITE)
        radios.pack(fill=tk.X, pady=(0, 14))
        for key, label in (("strict", "Strict"), ("simple", "Simple"), ("loose", "Loose")):
            tk.Radiobutton(
                radios,
                text=label,
                value=key,
                variable=self.strictness,
                bg=WHITE,
                fg=INK,
                selectcolor=WHITE,
                activebackground=WHITE,
                font=F(11),
                command=self._save_simple,
            ).pack(side=tk.LEFT, padx=(0, 16))

        self.language = LabeledSelect(body, "Language", ("English",))
        self.language.set("English")
        self.language.pack(fill=tk.X, pady=(0, 14))

        FAButton(body, "Save settings", command=self._save, variant="primary").pack(
            anchor="w", pady=(4, 8)
        )

        note = tk.Frame(body, bg="#E8EEF6")
        note.pack(fill=tk.X, pady=(12, 0))
        tk.Label(
            note,
            text="Note: MySQL is optional for advanced use; default database is SQLite on this PC.",
            bg="#E8EEF6",
            fg=NAVY,
            font=F(9),
            wraplength=640,
            justify=tk.LEFT,
            padx=12,
            pady=10,
            anchor="w",
        ).pack(fill=tk.X)

        about = tk.Frame(body, bg=WHITE)
        about.pack(fill=tk.X, pady=(12, 0))
        tk.Label(about, text="About", bg=WHITE, fg=INK, font=F(12, "bold"), anchor="w").pack(fill=tk.X)
        tk.Label(
            about,
            text=f"{PRODUCT_NAME} by {VENDOR} · local app · version {__version__}",
            bg=WHITE,
            fg=INK,
            font=F(10),
            anchor="w",
        ).pack(fill=tk.X, pady=(4, 0))
        tk.Label(about, text=SELL_LINE, bg=WHITE, fg=MUTE, font=F(10), anchor="w").pack(fill=tk.X)
        tk.Label(about, text=BYLINE, bg=WHITE, fg=MUTE, font=F(9), anchor="w").pack(
            fill=tk.X, pady=(2, 0)
        )

        self.adv_toggle = FAButton(
            body, "Advanced", command=self._toggle_advanced, variant="ghost"
        )
        self.adv_toggle.pack(anchor="w", pady=(18, 8))
        self.adv = tk.Frame(body, bg=WHITE)
        self._build_advanced(self.adv)

    def _build_advanced(self, host: tk.Frame) -> None:
        tk.Label(
            host,
            text="Optional MySQL. Leave off unless you already run a local MySQL server.",
            bg=WHITE,
            fg=MUTE,
            font=F(9),
            wraplength=640,
            justify=tk.LEFT,
            anchor="w",
        ).pack(fill=tk.X, pady=(0, 8))
        self.use_mysql = tk.BooleanVar(value=False)
        tk.Checkbutton(
            host,
            text="Use MySQL",
            variable=self.use_mysql,
            bg=WHITE,
            fg=INK,
            font=F(11),
            selectcolor=WHITE,
            activebackground=WHITE,
        ).pack(anchor="w", pady=(0, 8))
        self.mysql_host = LabeledField(host, "Host")
        self.mysql_host.pack(fill=tk.X, pady=4)
        self.mysql_port = LabeledField(host, "Port")
        self.mysql_port.pack(fill=tk.X, pady=4)
        self.mysql_user = LabeledField(host, "User")
        self.mysql_user.pack(fill=tk.X, pady=4)
        self.mysql_password = LabeledField(host, "Password")
        self.mysql_password.entry.configure(show="•")
        self.mysql_password.pack(fill=tk.X, pady=4)
        self.mysql_db = LabeledField(host, "Database")
        self.mysql_db.pack(fill=tk.X, pady=4)
        row = tk.Frame(host, bg=WHITE)
        row.pack(fill=tk.X, pady=(10, 0))
        FAButton(row, "Test connection", command=self._test_mysql, variant="secondary").pack(
            side=tk.LEFT, padx=(0, 8)
        )
        FAButton(
            row, "Import old attendancedb", command=self._import_legacy, variant="secondary"
        ).pack(side=tk.LEFT)

    def on_show(self) -> None:
        self._load()

    def refresh(self) -> None:
        self._load()

    def _load(self) -> None:
        cfg = self.app.cfg
        self.org.set(cfg.org_name)
        cameras = list_cameras()
        labels = [c.label for c in cameras]
        self.camera.combo.configure(values=labels)
        current = f"Camera {cfg.camera_index}"
        self.camera.set(current if current in labels else labels[0])
        self.folder.entry.configure(state="normal")
        self.folder.set(str(self.app.data_dir))
        self.folder.entry.configure(state="readonly")
        if cfg.strictness in STRICTNESS:
            self.strictness.set(cfg.strictness)
        self.language.set("English")
        self.use_mysql.set(cfg.engine == "mysql")
        self.mysql_host.set(cfg.mysql.host)
        self.mysql_port.set(str(cfg.mysql.port))
        self.mysql_user.set(cfg.mysql.user)
        self.mysql_password.set(cfg.mysql.password)
        self.mysql_db.set(cfg.mysql.database)

    def _toggle_advanced(self) -> None:
        self._advanced_open = not self._advanced_open
        if self._advanced_open:
            self.adv.pack(fill=tk.X, pady=(0, 8))
            self.adv_toggle.set_text("Hide advanced")
        else:
            self.adv.pack_forget()
            self.adv_toggle.set_text("Advanced")

    def _save_simple(self) -> None:
        self.app.cfg.strictness = self.strictness.get()
        self.app.save_cfg()

    def _save(self) -> None:
        cfg = self.app.cfg
        cfg.org_name = self.org.get()
        label = self.camera.get()
        try:
            cfg.camera_index = int(label.rsplit(" ", 1)[-1])
        except (ValueError, IndexError):
            cfg.camera_index = 0
        cfg.strictness = self.strictness.get()
        cfg.language = "en"
        cfg.mysql.host = self.mysql_host.get() or "127.0.0.1"
        try:
            cfg.mysql.port = int(self.mysql_port.get() or 3306)
        except ValueError:
            cfg.mysql.port = 3306
        cfg.mysql.user = self.mysql_user.get()
        cfg.mysql.password = self.mysql_password.get()
        cfg.mysql.database = self.mysql_db.get() or "attendancedb"
        wanted = "mysql" if self.use_mysql.get() else "sqlite"
        if wanted == "mysql" and not mysql_available():
            messagebox.showerror(
                "Settings",
                "mysql-connector-python is not installed. Stay on SQLite or install the optional package.",
                parent=self,
            )
            self.use_mysql.set(False)
            wanted = "sqlite"
        previous = cfg.engine
        cfg.engine = wanted
        try:
            if previous != wanted:
                self.app.store.reconnect(cfg)
            elif wanted == "mysql":
                self.app.store.reconnect(cfg)
        except StoreError as exc:
            cfg.engine = "sqlite"
            self.use_mysql.set(False)
            self.app.store.reconnect(cfg)
            messagebox.showerror("Settings", str(exc), parent=self)
            self.app.save_cfg()
            return
        self.app.save_cfg()
        messagebox.showinfo("Settings", "Saved.", parent=self)

    def _test_camera(self) -> None:
        label = self.camera.get()
        try:
            index = int(label.rsplit(" ", 1)[-1])
        except (ValueError, IndexError):
            index = 0
        try:
            cap = open_camera(index)
        except Exception as exc:
            messagebox.showerror("Test camera", str(exc), parent=self)
            return
        cap.release()
        self.app.cfg.camera_index = index
        self.app.cfg.setup.camera_connected = True
        self.app.save_cfg()
        messagebox.showinfo("Test camera", f"{label} opened successfully.", parent=self)

    def _change_folder(self) -> None:
        chosen = filedialog.askdirectory(
            title="Choose data folder",
            initialdir=str(self.app.data_dir),
            parent=self,
        )
        if not chosen:
            return
        self.app.use_data_dir(chosen, chosen_by_user=True)
        self._load()

    def _test_mysql(self) -> None:
        self._save()
        if not mysql_available():
            messagebox.showerror(
                "MySQL",
                "Install mysql-connector-python to test a MySQL connection.",
                parent=self,
            )
            return
        try:
            test_mysql(self.app.cfg)
        except StoreError as exc:
            messagebox.showerror("MySQL", str(exc), parent=self)
            return
        extra = ""
        try:
            if detect_legacy_mysql(self.app.cfg) and not self.app.cfg.mysql_import_done:
                extra = "\n\nAn older attendancedb was found. You can import it once from this screen."
        except StoreError:
            extra = ""
        messagebox.showinfo("MySQL", "Connected." + extra, parent=self)

    def _import_legacy(self) -> None:
        if not messagebox.askyesno(
            "Import old attendancedb",
            "Copy staff and attendance from the old MySQL attendancedb into this app? "
            "This is a one-time import. Photos are copied when the old files are still on disk.",
            parent=self,
        ):
            return
        try:
            stats = import_legacy_mysql(self.app.store, self.app.cfg, self.app.data_dir)
        except StoreError as exc:
            messagebox.showerror("Import", str(exc), parent=self)
            return
        self.app.cfg.mysql_import_done = True
        self.app.save_cfg()
        self.app.reload_encodings()
        messagebox.showinfo(
            "Import",
            f"Imported {stats['people']} people and {stats['attended']} attendance rows "
            f"({stats['skipped']} skipped).",
            parent=self,
        )


# token reserved
_ = (BONE, BORDER)
