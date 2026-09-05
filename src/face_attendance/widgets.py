"""Shared controls painted with the designer tokens."""

from __future__ import annotations

import tkinter as tk
from collections.abc import Callable
from tkinter import ttk

from face_attendance.theme import (
    AMBER,
    BORDER,
    DANGER,
    F,
    INK,
    MUTE,
    NAVY,
    NAVY_ACTIVE,
    SIDEBAR_W,
    SUCCESS,
    SUCCESS_BG,
    WHITE,
    BONE,
    BONE_ALT,
    draw_scan_face,
)

_VARIANTS = {
    "primary": (NAVY, WHITE, NAVY),
    "secondary": (WHITE, INK, BORDER),
    "amber": (AMBER, INK, AMBER),
    "danger": (DANGER, WHITE, DANGER),
    "ghost": (BONE, INK, BORDER),
}


class FAButton(tk.Frame):
    def __init__(
        self,
        master: tk.Misc,
        text: str,
        command: Callable[[], None] | None = None,
        variant: str = "primary",
        width: int | None = None,
        **kwargs,
    ) -> None:
        bg, fg, border = _VARIANTS.get(variant, _VARIANTS["primary"])
        super().__init__(master, bg=border, highlightthickness=0, **kwargs)
        self._command = command
        self._bg = bg
        self._label = tk.Label(
            self,
            text=text,
            bg=bg,
            fg=fg,
            font=F(11, "bold"),
            cursor="hand2",
            padx=16,
            pady=8,
        )
        if width:
            self._label.configure(width=width)
        self._label.pack(padx=1, pady=1, fill=tk.BOTH, expand=True)
        self._label.bind("<Button-1>", self._on_click)
        self.bind("<Button-1>", self._on_click)

    def _on_click(self, _event=None) -> None:
        if self._command:
            self._command()

    def set_text(self, text: str) -> None:
        self._label.configure(text=text)


class LabeledField(tk.Frame):
    def __init__(
        self,
        master: tk.Misc,
        label: str,
        hint: str = "",
        required: bool = False,
        bg: str = WHITE,
        **kwargs,
    ) -> None:
        super().__init__(master, bg=bg, **kwargs)
        title = label + (" *" if required else "")
        tk.Label(self, text=title, bg=bg, fg=INK, font=F(10, "bold"), anchor="w").pack(
            fill=tk.X
        )
        self.var = tk.StringVar()
        wrap = tk.Frame(self, bg=BORDER)
        wrap.pack(fill=tk.X, pady=(4, 0))
        self.entry = tk.Entry(
            wrap,
            textvariable=self.var,
            bg=WHITE,
            fg=INK,
            relief=tk.FLAT,
            font=F(11),
            insertbackground=INK,
        )
        self.entry.pack(fill=tk.X, padx=8, pady=7)
        if hint:
            tk.Label(self, text=hint, bg=bg, fg=MUTE, font=F(9), anchor="w").pack(
                fill=tk.X, pady=(4, 0)
            )

    def get(self) -> str:
        return self.var.get().strip()

    def set(self, value: str) -> None:
        self.var.set(value or "")


class LabeledSelect(tk.Frame):
    def __init__(
        self,
        master: tk.Misc,
        label: str,
        values: tuple[str, ...] | list[str],
        hint: str = "",
        required: bool = False,
        bg: str = WHITE,
        **kwargs,
    ) -> None:
        super().__init__(master, bg=bg, **kwargs)
        title = label + (" *" if required else "")
        tk.Label(self, text=title, bg=bg, fg=INK, font=F(10, "bold"), anchor="w").pack(
            fill=tk.X
        )
        self.var = tk.StringVar()
        wrap = tk.Frame(self, bg=BORDER)
        wrap.pack(fill=tk.X, pady=(4, 0))
        self.combo = ttk.Combobox(
            wrap,
            textvariable=self.var,
            values=list(values),
            state="readonly",
            font=F(11),
        )
        self.combo.pack(fill=tk.X, padx=6, pady=6)
        if hint:
            tk.Label(self, text=hint, bg=bg, fg=MUTE, font=F(9), anchor="w").pack(
                fill=tk.X, pady=(4, 0)
            )

    def get(self) -> str:
        return self.var.get().strip()

    def set(self, value: str) -> None:
        self.var.set(value or "")


class Card(tk.Frame):
    def __init__(self, master: tk.Misc, **kwargs) -> None:
        super().__init__(master, bg=BORDER, highlightthickness=0)
        self.body = tk.Frame(self, bg=WHITE, **kwargs)
        self.body.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)


class Sidebar(tk.Frame):
    def __init__(self, master: tk.Misc, on_nav: Callable[[str], None]) -> None:
        super().__init__(master, bg=NAVY, width=SIDEBAR_W)
        self.pack_propagate(False)
        self._on_nav = on_nav
        self._buttons: dict[str, tk.Frame] = {}
        self._active = ""

        brand = tk.Frame(self, bg=NAVY)
        brand.pack(fill=tk.X, padx=18, pady=(22, 18))
        icon = tk.Canvas(brand, width=32, height=32, bg=NAVY, highlightthickness=0)
        icon.pack(side=tk.LEFT)
        draw_scan_face(icon, 2, 2, 28, WHITE)
        text = tk.Frame(brand, bg=NAVY)
        text.pack(side=tk.LEFT, padx=(10, 0))
        tk.Label(
            text, text="Face Attendance", bg=NAVY, fg=WHITE, font=F(11, "bold"), anchor="w"
        ).pack(fill=tk.X)
        tk.Label(
            text, text="Flemton Tech · local", bg=NAVY, fg="#C5CDD8", font=F(8), anchor="w"
        ).pack(fill=tk.X)

        items = (
            ("attendance", "Take attendance"),
            ("staff", "Staff"),
            ("log", "Log"),
            ("settings", "Settings"),
        )
        for key, label in items:
            self._buttons[key] = self._nav_item(key, label)

        foot = tk.Frame(self, bg=NAVY)
        foot.pack(side=tk.BOTTOM, fill=tk.X, padx=18, pady=18)
        tk.Label(
            foot,
            text="Data stays on this computer",
            bg=NAVY,
            fg="#8B95A5",
            font=F(8),
            wraplength=180,
            justify=tk.LEFT,
            anchor="w",
        ).pack(fill=tk.X)

    def _nav_item(self, key: str, label: str) -> tk.Frame:
        row = tk.Frame(self, bg=NAVY, cursor="hand2")
        row.pack(fill=tk.X, padx=10, pady=2)
        inner = tk.Label(
            row,
            text=f"  {label}",
            bg=NAVY,
            fg=WHITE,
            font=F(11),
            anchor="w",
            padx=12,
            pady=10,
        )
        inner.pack(fill=tk.X)
        for widget in (row, inner):
            widget.bind("<Button-1>", lambda _e, k=key: self._on_nav(k))
        row._label = inner  # type: ignore[attr-defined]
        return row

    def set_active(self, key: str) -> None:
        self._active = key
        for name, row in self._buttons.items():
            active = name == key
            bg = NAVY_ACTIVE if active else NAVY
            row.configure(bg=bg)
            row._label.configure(bg=bg, fg=WHITE)  # type: ignore[attr-defined]


class StepList(tk.Frame):
    def __init__(self, master: tk.Misc, steps: list[str], bg: str = WHITE) -> None:
        super().__init__(master, bg=bg)
        self._steps = steps
        self._bg = bg
        self._rows: list[tuple[tk.Canvas, tk.Label]] = []
        for index, label in enumerate(steps, start=1):
            row = tk.Frame(self, bg=bg)
            row.pack(fill=tk.X, pady=6)
            mark = tk.Canvas(row, width=26, height=26, bg=bg, highlightthickness=0)
            mark.pack(side=tk.LEFT)
            text = tk.Label(row, text=f"{index}. {label}", bg=bg, fg=INK, font=F(11), anchor="w")
            text.pack(side=tk.LEFT, padx=10)
            self._rows.append((mark, text))
        self.set_current(1)

    def set_current(self, current: int) -> None:
        for index, (mark, text) in enumerate(self._rows, start=1):
            mark.delete("all")
            done_or_current = index <= current
            if done_or_current:
                mark.create_oval(2, 2, 24, 24, fill=NAVY, outline=NAVY)
                mark.create_text(13, 13, text=str(index), fill=WHITE, font=F(9, "bold"))
                text.configure(fg=INK)
            else:
                mark.create_oval(2, 2, 24, 24, fill=WHITE, outline=BORDER, width=2)
                mark.create_text(13, 13, text=str(index), fill=MUTE, font=F(9, "bold"))
                text.configure(fg=MUTE)


class StatusBanner(tk.Frame):
    def __init__(self, master: tk.Misc, **kwargs) -> None:
        super().__init__(master, bg=BONE, **kwargs)
        self._label = tk.Label(
            self, text="", bg=BONE, fg=INK, font=F(12, "bold"), anchor="w", padx=14, pady=10
        )
        self._label.pack(fill=tk.X)
        self._detail = tk.Label(
            self, text="", bg=BONE, fg=MUTE, font=F(10), anchor="w", padx=14
        )
        self._detail.pack(fill=tk.X, pady=(0, 8))

    def set(self, title: str, detail: str = "", kind: str = "idle") -> None:
        colors = {
            "success": (SUCCESS_BG, SUCCESS),
            "already": ("#F3EFE6", INK),
            "unknown": (BONE, MUTE),
            "idle": (BONE, INK),
            "danger": ("#F8E8E6", DANGER),
        }
        bg, fg = colors.get(kind, colors["idle"])
        self.configure(bg=bg)
        self._label.configure(text=title, bg=bg, fg=fg)
        self._detail.configure(text=detail, bg=bg, fg=MUTE)


# Avoid unused import lint if BONE_ALT is only for future screens
_ = BONE_ALT
