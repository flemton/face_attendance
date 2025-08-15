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
- `main.py`: Main GUI application for registration, viewing attendance, and face attendance
- `README.md`: Instructions
- `requirements.txt`: Dependencies

## Usage
1. Create database using `01 - Create Database.sql`.
2. Update database credentials in `main.py` if needed (default: user='root', password='qwertyui').
3. Run the app: `python main.py`
4. Use the GUI buttons:
   - Register Staff: Select image and enter name.
   - View Attendance: See the attendance table.
   - Start Face Attendance: Open camera for live recognition.

## Dependencies
- `opencv-contrib-python`
- `mysql-connector-python`
- `numpy`
- `pillow` (for GUI image handling)

### Thanks
- Nick
- Prof. David J. Malan
- Brian Yu
- Doug Llyod
- All CS50 team, students