# PyInstaller spec — run from repo root on the OS you are packing.
# onedir is more reliable than onefile for OpenCV + dlib.
# Windows: docs/WINDOWS.md  Linux: docs/LINUX.md  macOS: docs/MACOS.md

import sys
from pathlib import Path

from PyInstaller.building.build_main import COLLECT, EXE, PYZ, Analysis
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

try:
    from PyInstaller.building.osx import BUNDLE
except ImportError:  # pragma: no cover - Windows / Linux PyInstaller
    BUNDLE = None

ROOT = Path(SPECPATH).resolve().parent
SRC = ROOT / "src"
ENTRY = SRC / "face_attendance" / "__main__.py"

datas = []
datas += collect_data_files("tzdata")
try:
    datas += collect_data_files("face_recognition_models")
except Exception:
    pass

hidden = []
hidden += collect_submodules("face_recognition")
hidden += collect_submodules("cv2")
hidden += collect_submodules("PIL")
hidden += ["face_attendance", "mysql.connector"]

a = Analysis(
    [str(ENTRY)],
    pathex=[str(SRC)],
    binaries=[],
    datas=datas,
    hiddenimports=hidden,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="FaceAttendance",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    name="FaceAttendance",
)

if sys.platform == "darwin" and BUNDLE is not None:
    app = BUNDLE(
        coll,
        name="Face Attendance.app",
        icon=None,
        bundle_identifier="tech.flemton.faceattendance",
        info_plist={
            "CFBundleName": "Face Attendance",
            "CFBundleDisplayName": "Face Attendance",
            "CFBundleShortVersionString": "1.0.0",
            "CFBundleVersion": "1.0.0",
            "NSHighResolutionCapable": True,
            "NSCameraUsageDescription": (
                "Face Attendance uses the camera on this computer to register "
                "people and take attendance. Nothing is uploaded."
            ),
            "LSApplicationCategoryType": "public.app-category.business",
        },
    )
