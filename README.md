# Face Attendance System

A Python-based face recognition attendance system using OpenCV and MySQL. Works on Linux, Mac, or Windows.

## Features

- 👤 Automatic face recognition using LBPH algorithm
- 📊 MySQL database for staff and attendance records
- ⚡ Lazy loading of face encodings for better performance
- 🔧 JSON-based configuration
- 📷 Face detection verification during registration
- 🎯 Duplicate attendance prevention (once per day)

## Requirements

- Python 3.7+
- MySQL Community Edition
- Webcam

## Installation

1. Clone the repository:
```bash
git clone https://github.com/flemton/face_attendance.git
cd face_attendance
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create the database:
```bash
mysql -u root -p < "01 - Create Database.sql"
```

4. Configure the application:
   - Copy `config.json` and update with your MySQL credentials
   - Ensure the `img/` directory exists

## Configuration

Edit `config.json`:
```json
{
  "database": {
    "user": "root",
    "password": "your_password",
    "host": "127.0.0.1",
    "database": "attendancedb"
  },
  "recognition": {
    "confidence_threshold": 50,
    "scale_factor": 1.1,
    "min_neighbors": 3,
    "min_size": [30, 30]
  }
}
```

## Usage

### Register Staff Members

1. Place staff face images in the `img/` directory
2. Run the registration script:
```bash
python register_staff.py
```
3. Follow prompts to enter name and image filename

### Run Attendance System

```bash
python face_attendance.py
```

- The system will load face encodings in the background
- When a face is recognized, attendance is automatically recorded
- Press 'q' to quit

## Project Structure

```
face_attendance/
├── img/                      # Staff face images
├── 01 - Create Database.sql  # Database schema
├── config.json              # Application configuration
├── face_attendance.py       # Main attendance application
├── register_staff.py        # Staff registration script
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## Database Schema

### staff table
- `id`: Primary key
- `name`: Staff member name
- `img_name`: Path to face image

### attended table
- `id`: Primary key
- `staff_id`: Foreign key to staff
- `name`: Staff member name
- `time`: Attendance time
- `date`: Attendance date

## Troubleshooting

### "Database Error: Access denied"
- Check your MySQL credentials in `config.json`
- Ensure MySQL server is running

### "No face detected in image"
- Ensure the image is clear and well-lit
- Face should be facing the camera
- Try a different image

### "Could not open webcam"
- Check that your webcam is connected
- Ensure no other application is using the webcam

## Credits

- Nick
- Prof. David J. Malan
- Brian Yu
- Doug Lloyd
- All CS50 team and students
