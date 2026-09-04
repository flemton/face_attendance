"""Local webcam helpers. One camera at a time — no cloud, no multi-cam product."""

from __future__ import annotations

from dataclasses import dataclass

import cv2
import numpy as np


@dataclass
class CameraInfo:
    index: int
    label: str


def list_cameras(limit: int = 6) -> list[CameraInfo]:
    found: list[CameraInfo] = []
    for index in range(limit):
        cap = _open(index)
        if cap is None:
            continue
        cap.release()
        found.append(CameraInfo(index=index, label=f"Camera {index}"))
    if not found:
        # Still offer Camera 0 so Settings can show a selection.
        found.append(CameraInfo(index=0, label="Camera 0"))
    return found


def open_camera(index: int) -> cv2.VideoCapture:
    cap = _open(index)
    if cap is None:
        raise RuntimeError(
            f"Could not open camera {index}. Check the cable and that no other app is using it."
        )
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    return cap


def grab_frame(cap: cv2.VideoCapture) -> np.ndarray | None:
    ok, frame = cap.read()
    if not ok or frame is None:
        return None
    return frame


def _open(index: int) -> cv2.VideoCapture | None:
    cap = cv2.VideoCapture(index)
    if cap is None or not cap.isOpened():
        if cap is not None:
            cap.release()
        return None
    ok, _ = cap.read()
    if not ok:
        cap.release()
        return None
    return cap
