"""OpenCV camera frames + face_recognition encodings. Offline only."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np

from face_attendance.db import Person

# face_recognition.compare_faces default is 0.6. Lower = stricter.
TOLERANCE = {
    "strict": 0.45,
    "simple": 0.60,
    "loose": 0.70,
}


class RecognitionUnavailable(Exception):
    pass


def tolerance_for(strictness: str) -> float:
    key = (strictness or "simple").lower()
    return TOLERANCE.get(key, TOLERANCE["simple"])


def face_recognition_available() -> bool:
    try:
        import face_recognition  # noqa: F401
        return True
    except Exception:
        return False


def _lib():
    try:
        import face_recognition
    except Exception as exc:
        raise RecognitionUnavailable(
            "face_recognition is not installed. On Windows this needs "
            "Visual C++ Build Tools and CMake. See docs/WINDOWS.md."
        ) from exc
    return face_recognition


def encode_image_file(path: Path) -> np.ndarray | None:
    fr = _lib()
    image = fr.load_image_file(str(path))
    encodings = fr.face_encodings(image)
    if not encodings:
        return None
    return encodings[0]


def encode_bgr_frame(frame_bgr: np.ndarray) -> list[tuple[tuple[int, int, int, int], np.ndarray]]:
    """Return (top, right, bottom, left) boxes plus encodings on a BGR frame."""
    fr = _lib()
    import cv2

    if frame_bgr is None or frame_bgr.size == 0:
        return []
    height, width = frame_bgr.shape[:2]
    scale = 1.0
    work = frame_bgr
    if width > 480:
        scale = 480.0 / width
        work = cv2.resize(frame_bgr, (int(width * scale), int(height * scale)))
    rgb = cv2.cvtColor(work, cv2.COLOR_BGR2RGB)
    locations = fr.face_locations(rgb, model="hog")
    encodings = fr.face_encodings(rgb, locations)
    results: list[tuple[tuple[int, int, int, int], np.ndarray]] = []
    inv = 1.0 / scale
    for (top, right, bottom, left), encoding in zip(locations, encodings):
        box = (
            int(top * inv),
            int(right * inv),
            int(bottom * inv),
            int(left * inv),
        )
        results.append((box, encoding))
    return results


@dataclass
class KnownFace:
    person: Person
    encoding: np.ndarray


def load_known(people: list[Person], data_dir: Path) -> list[KnownFace]:
    from face_attendance.paths import resolve_photo

    known: list[KnownFace] = []
    if not people:
        return known
    _lib()
    for person in people:
        path = resolve_photo(data_dir, person.photo_path)
        if path is None or not path.is_file():
            continue
        cached = path.with_suffix(".npy")
        encoding = None
        if cached.is_file():
            try:
                encoding = np.load(str(cached))
            except Exception:
                encoding = None
        if encoding is None:
            encoding = encode_image_file(path)
            if encoding is not None:
                try:
                    np.save(str(cached), encoding)
                except OSError:
                    pass
        if encoding is not None:
            known.append(KnownFace(person=person, encoding=encoding))
    return known


def match(encoding: np.ndarray, known: list[KnownFace], strictness: str) -> Person | None:
    if not known:
        return None
    fr = _lib()
    matrix = [item.encoding for item in known]
    distances = fr.face_distance(matrix, encoding)
    best = int(np.argmin(distances))
    if distances[best] <= tolerance_for(strictness):
        return known[best].person
    return None
