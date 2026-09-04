"""Designer UX pack tokens. Spec colors win over mood PNGs."""

from __future__ import annotations

import sys
import tkinter as tk
from tkinter import ttk

NAVY = "#0F1C2E"
NAVY_ACTIVE = "#1A2D48"
BONE = "#F6F1EA"
BONE_ALT = "#F3F4F6"
WHITE = "#FFFFFF"
INK = "#1A1A1A"
MUTE = "#6B7280"
SUCCESS = "#1B7F4E"
SUCCESS_BG = "#E7F4EE"
DANGER = "#B42318"
AMBER = "#F5A524"
BORDER = "#E7E0D6"
SIDEBAR_W = 232
WINDOW_W = 1280
WINDOW_H = 800


def font_family() -> str:
    if sys.platform == "win32":
        return "Segoe UI"
    return "Ubuntu"


def F(size: int = 11, weight: str = "normal") -> tuple:
    return (font_family(), size, weight)


def apply_root(root: tk.Tk) -> ttk.Style:
    root.configure(bg=BONE_ALT)
    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except tk.TclError:
        pass
    style.configure("TFrame", background=BONE_ALT)
    style.configure("Card.TFrame", background=WHITE)
    style.configure("Bone.TFrame", background=BONE)
    style.configure(
        "TLabel",
        background=BONE_ALT,
        foreground=INK,
        font=F(11),
    )
    style.configure("Card.TLabel", background=WHITE, foreground=INK, font=F(11))
    style.configure("Mute.TLabel", background=WHITE, foreground=MUTE, font=F(10))
    style.configure("Title.TLabel", background=BONE_ALT, foreground=INK, font=F(22, "bold"))
    style.configure("CardTitle.TLabel", background=WHITE, foreground=INK, font=F(22, "bold"))
    style.configure(
        "Treeview",
        background=WHITE,
        fieldbackground=WHITE,
        foreground=INK,
        rowheight=34,
        font=F(10),
        bordercolor=BORDER,
    )
    style.configure(
        "Treeview.Heading",
        background=BONE,
        foreground=INK,
        font=F(10, "bold"),
        relief="flat",
    )
    style.map("Treeview", background=[("selected", NAVY)], foreground=[("selected", WHITE)])
    style.configure(
        "TCombobox",
        fieldbackground=WHITE,
        background=WHITE,
        foreground=INK,
        arrowcolor=INK,
    )
    style.configure("TEntry", fieldbackground=WHITE, foreground=INK)
    style.configure(
        "Horizontal.TScale",
        background=WHITE,
        troughcolor=BONE,
    )
    return style


def draw_scan_face(canvas: tk.Canvas, x: int, y: int, size: int = 28, fill: str = WHITE) -> None:
    """Simple face-in-brackets mark used in the sidebar and welcome card."""
    pad = 2
    arm = max(6, size // 4)
    # Corner brackets
    canvas.create_line(x, y + arm, x, y, x + arm, y, fill=fill, width=2)
    canvas.create_line(x + size - arm, y, x + size, y, x + size, y + arm, fill=fill, width=2)
    canvas.create_line(x, y + size - arm, x, y + size, x + arm, y + size, fill=fill, width=2)
    canvas.create_line(
        x + size - arm, y + size, x + size, y + size, x + size, y + size - arm,
        fill=fill, width=2,
    )
    cx = x + size / 2
    cy = y + size / 2 + 1
    r = size / 2 - pad - 3
    canvas.create_oval(cx - r, cy - r, cx + r, cy + r, outline=fill, width=2)
    eye = max(1.4, size / 14)
    canvas.create_oval(cx - r * 0.35 - eye, cy - r * 0.15 - eye, cx - r * 0.35 + eye, cy - r * 0.15 + eye, fill=fill, outline=fill)
    canvas.create_oval(cx + r * 0.35 - eye, cy - r * 0.15 - eye, cx + r * 0.35 + eye, cy - r * 0.15 + eye, fill=fill, outline=fill)
    canvas.create_arc(
        cx - r * 0.45, cy - r * 0.1, cx + r * 0.45, cy + r * 0.55,
        start=200, extent=140, style=tk.ARC, outline=fill, width=2,
    )
