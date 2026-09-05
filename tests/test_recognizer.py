from face_attendance.recognizer import TOLERANCE, face_recognition_available, tolerance_for


def test_strictness_mapping():
    assert tolerance_for("strict") == TOLERANCE["strict"]
    assert tolerance_for("simple") == TOLERANCE["simple"]
    assert tolerance_for("loose") == TOLERANCE["loose"]
    assert tolerance_for("unknown") == TOLERANCE["simple"]
    assert tolerance_for("strict") < tolerance_for("simple") < tolerance_for("loose")


def test_availability_is_bool():
    assert face_recognition_available() in (True, False)
