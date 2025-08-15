import cv2
import numpy as np
from datetime import datetime
import mysql.connector

# Database connection
db = mysql.connector.connect(user='root', password='qwertyui', host='127.0.0.1', database='attendancedb')
cursor = db.cursor(buffered=True)

# Load known faces
known_encodings = []
known_names = []
cursor.execute("SELECT img_name, name FROM staff")
for img_name, name in cursor.fetchall():
    img = cv2.imread(img_name)
    if img is not None:
        rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encoding = cv2.face.LBPHFaceRecognizer_create().train(rgb_img)
        known_encodings.append(encoding)
        known_names.append(name)

# Register attendance
def register(name):
    time = datetime.now().strftime("%H:%M:%S")
    date_now = datetime.now().strftime("%Y-%m-%d")
    cursor.execute("SELECT id FROM staff WHERE name=%s", (name,))
    staff_id = cursor.fetchone()[0]
    cursor.execute("SELECT 1 FROM attended WHERE staff_id=%s AND date=%s", (staff_id, date_now))
    if not cursor.fetchone():
        cursor.execute("INSERT INTO attended (staff_id, name, time, date) VALUES (%s, %s, %s, %s)", (staff_id, name, time, date_now))
        db.commit()

# Initialize webcam
cap = cv2.VideoCapture(0)
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

while True:
    ret, frame = cap.read()
    if not ret:
        break
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.1, 4)
    
    for (x, y, w, h) in faces:
        face_roi = gray[y:y+h, x:x+w]
        for encoding, name in zip(known_encodings, known_names):
            if cv2.face.LBPHFaceRecognizer_create().predict(face_roi) == 0:
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                cv2.putText(frame, name, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
                register(name)
                break
        else:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 255), 2)
            cv2.putText(frame, "Unknown", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)

    cv2.imshow('Attendance', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
db.close()