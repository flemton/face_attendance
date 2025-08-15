# Face Attendance

## Installation

- Works on Linux, Mac, or Windows.

### Requirements

- Python 3.x
- [pip](https://pip.pypa.io/en/stable/installation/)
- MySQL Community Edition
- Install dependencies: `pip install -r requirements.txt`

### Files

- `/img`: Store staff face images
- `01 - Create Database.sql`: Database setup
- `face_attendance.py`: Main attendance app
- `register_staff.py`: Staff registration script
- `README.md`: Instructions
- `requirements.txt`: Dependencies

## Usage

1. Create database using `01 - Create Database.sql`.
2. Update `face_attendance.py` (line 6) with your MySQL credentials.
3. Place staff images in the `img` folder.
4. Register staff with `python register_staff.py`.
5. Run `python face_attendance.py` to start attendance tracking.
6. Press 'q' to quit.

## Dependencies

- `opencv-python`
- `mysql-connector-python`

###### Thanks

- Nick
- Prof. David J. Malan
- Brian Yu
- Doug Llyod
- All CS50 team, students
