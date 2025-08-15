import cv2
import numpy as np
from datetime import datetime
import mysql.connector
import threading

# Database connection
db = mysql.connector.connect(user='root', password='qwertyui', host='127.0.0.1', database='attendancedb')
cursor = db.cursor(buffered=True)

# Global variables for lazy loading
known_encodings = []
known_names = []
encodings_loaded = False

# Load encodings lazily in a separate thread
def load_encodings():
    global known_encodings, known_names, encodings_loaded
    if not encodings_loaded:
        cursor.execute("SELECT img_name, name FROM staff")
        for img_name, name in cursor.fetchall():
            img = cv2.imread(img_name, cv2.IMREAD_GRAYSCALE)
            if img is not None:
                recognizer = cv2.face.LBPHFaceRecognizer_create()
                recognizer.train([img], np.array([0]))
                known_encodings.append(recognizer)
                known_names.append(name)
        encodings_loaded = True

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

# Start loading encodings in background
threading.Thread(target=load_encodings, daemon=True).start()

while True:
    ret, frame = cap.read()
    if not ret:
        break
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.1, 3, minSize=(30, 30))  # Optimized for low-end

    if not encodings_loaded and faces:  # Load encodings only when a face is detected
        load_encodings()

    for (x, y, w, h) in faces:
        face_roi = gray[y:y+h, x:x+w]
        if encodings_loaded:
            for recognizer, name in zip(known_encodings, known_names):
                label, confidence = recognizer.predict(face_roi)
                if confidence < 50:  # Recognition threshold
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                    cv2.putText(frame, name, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
                    register(name)
                    break
            else:
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 255), 2)
                cv2.putText(frame, "Unknown", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)

    cv2.imshow('Attendance', cv2.resize(frame, (640, 480)))  # Reduced resolution for performance
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
db.close()