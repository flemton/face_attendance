"""Attendance log — filters, CSV export, print, local data path."""

from __future__ import annotations

import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from face_attendance.clock import format_date, format_time, today_iso
from face_attendance.config import ROLES
from face_attendance.export import open_print, write_csv
from face_attendance.theme import BONE, BONE_ALT, BORDER, F, INK, MUTE, NAVY, WHITE
from face_attendance.widgets import Card, FAButton, LabeledField, LabeledSelect


class LogScreen(tk.Frame):
    def __init__(self, master, app) -> None:
        super().__init__(master, bg=BONE_ALT)
        self.app = app
        self._sort_col = "date"
        self._sort_desc = True

        header = tk.Frame(self, bg=BONE_ALT)
        header.pack(fill=tk.X, padx=28, pady=(22, 8))
        tk.Label(header, text="Attendance log", bg=BONE_ALT, fg=INK, font=F(22, "bold")).pack(
            anchor="w"
        )
        tk.Label(
            header,
            text="View and export records stored on this computer.",
            bg=BONE_ALT,
            fg=MUTE,
            font=F(11),
        ).pack(anchor="w", pady=(4, 0))

        filters = Card(self)
        filters.pack(fill=tk.X, padx=28, pady=(8, 10))
        bar = filters.body
        bar.configure(padx=14, pady=12)
        grid = tk.Frame(bar, bg=WHITE)
        grid.pack(fill=tk.X)
        for i in range(4):
            grid.columnconfigure(i, weight=1)
        self.date_from = LabeledField(grid, "From date", hint="YYYY-MM-DD")
        self.date_from.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        self.date_to = LabeledField(grid, "To date", hint="YYYY-MM-DD")
        self.date_to.grid(row=0, column=1, sticky="ew", padx=8)
        self.role = LabeledSelect(grid, "Role", ("All roles",) + ROLES)
        self.role.set("All roles")
        self.role.grid(row=0, column=2, sticky="ew", padx=8)
        self.search = LabeledField(grid, "Search name", hint="Search by name…")
        self.search.grid(row=0, column=3, sticky="ew", padx=(8, 0))
        actions = tk.Frame(bar, bg=WHITE)
        actions.pack(fill=tk.X, pady=(10, 0))
        FAButton(actions, "Apply filters", command=self.refresh, variant="primary").pack(
            side=tk.LEFT, padx=(0, 8)
        )
        FAButton(actions, "Today", command=self._today, variant="secondary").pack(side=tk.LEFT)

        table_card = Card(self)
        table_card.pack(fill=tk.BOTH, expand=True, padx=28, pady=(0, 8))
        table = table_card.body
        table.configure(padx=8, pady=8)
        cols = ("name", "id", "role", "time", "date")
        self.tree = ttk.Treeview(table, columns=cols, show="headings", selectmode="browse")
        headings = {
            "name": "Name",
            "id": "ID",
            "role": "Role",
            "time": "Time",
            "date": "Date",
        }
        for key, label in headings.items():
            self.tree.heading(key, text=label, command=lambda c=key: self._sort(c))
            self.tree.column(key, width=140 if key == "name" else 100, stretch=True)
        scroll = ttk.Scrollbar(table, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)

        footer = tk.Frame(self, bg=BONE)
        footer.pack(fill=tk.X, side=tk.BOTTOM)
        inner = tk.Frame(footer, bg=BONE)
        inner.pack(fill=tk.X, padx=28, pady=10)
        self.count = tk.Label(inner, text="", bg=BONE, fg=MUTE, font=F(10))
        self.count.pack(side=tk.LEFT)
        FAButton(inner, "Print", command=self._print, variant="secondary").pack(
            side=tk.RIGHT, padx=(8, 0)
        )
        FAButton(inner, "Export CSV", command=self._export, variant="primary").pack(side=tk.RIGHT)
        self.path_label = tk.Label(
            self, text="", bg=BONE_ALT, fg=NAVY, font=F(9), anchor="w", padx=28, pady=6
        )
        self.path_label.pack(fill=tk.X, side=tk.BOTTOM)

        self._rows = []

    def on_show(self) -> None:
        if not self.date_from.get() and not self.date_to.get():
            self._today()
        else:
            self.refresh()

    def refresh(self) -> None:
        role = self.role.get()
        if role == "All roles":
            role = None
        self._rows = self.app.store.list_attendance(
            date_from=self.date_from.get() or None,
            date_to=self.date_to.get() or None,
            role=role,
            name_query=self.search.get() or None,
        )
        self._render()
        self.path_label.configure(
            text=f"Stored on this computer · {self.app.store.location}"
        )

    def _today(self) -> None:
        day = today_iso()
        self.date_from.set(day)
        self.date_to.set(day)
        self.refresh()

    def _sort(self, column: str) -> None:
        if self._sort_col == column:
            self._sort_desc = not self._sort_desc
        else:
            self._sort_col = column
            self._sort_desc = False
        key_map = {
            "name": lambda r: (r.name or "").lower(),
            "id": lambda r: (r.external_id or "").lower(),
            "role": lambda r: (r.role or "").lower(),
            "time": lambda r: r.time or "",
            "date": lambda r: r.date or "",
        }
        self._rows.sort(key=key_map[column], reverse=self._sort_desc)
        self._render()

    def _render(self) -> None:
        self.tree.delete(*self.tree.get_children())
        for row in self._rows:
            self.tree.insert(
                "",
                tk.END,
                values=(
                    row.name,
                    row.external_id or "",
                    row.role or "",
                    format_time(row.time),
                    row.date,
                ),
            )
        total = len(self._rows)
        self.count.configure(
            text=f"Showing {total} record{'s' if total != 1 else ''} · {format_date()}"
        )

    def _export(self) -> None:
        path = filedialog.asksaveasfilename(
            title="Export CSV",
            defaultextension=".csv",
            filetypes=[("CSV", "*.csv")],
            initialfile=f"attendance-{today_iso()}.csv",
            parent=self,
        )
        if not path:
            return
        write_csv(path, self._rows)
        messagebox.showinfo("Export CSV", f"Saved {len(self._rows)} rows to:\n{path}", parent=self)

    def _print(self) -> None:
        open_print(
            self._rows,
            org_name=self.app.cfg.org_name,
            data_path=self.app.store.location,
        )
