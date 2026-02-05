import cv2
import numpy as np
from datetime import datetime
import mysql.connector
import threading
import os
import json
from typing import List, Tuple, Optional

# Configuration
CONFIG_FILE = 'config.json'

def load_config():
    """Load configuration from JSON file"""
    default_config = {
        "database": {
            "user": "root",
            "password": "qwertyui",
            "host": "127.0.0.1",
            "database": "attendancedb"
        },
        "recognition": {
            "confidence_threshold": 50,
            "scale_factor": 1.1,
            "min_neighbors": 3,
            "min_size": [30, 30]
        },
        "display": {
            "width": 640,
            "height": 480,
            "font": "FONT_HERSHEY_SIMPLEX",
            "font_scale": 0.9,
            "thickness": 2
        }
    }
    
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return {**default_config, **json.load(f)}
    return default_config

config = load_config()

# Database connection with error handling
def get_db_connection():
    """Create database connection"""
    try:
        db_config = config['database']
        return mysql.connector.connect(
            user=db_config['user'],
            password=db_config['password'],
            host=db_config['host'],
            database=db_config['database']
        )
    except mysql.connector.Error as err:
        print(f"Database Error: {err}")
        raise

try:
    db = get_db_connection()
    cursor = db.cursor(buffered=True)
except Exception as e:
    print(f"Failed to connect to database: {e}")
    print("Please check your config.json and ensure MySQL is running")
    exit(1)

# Global variables for lazy loading
known_encodings: List = []
known_names: List[str] = []
encodings_loaded = False

# Load encodings lazily in a separate thread
def load_encodings():
    """Load face encodings from database"""
    global known_encodings, known_names, encodings_loaded
    if not encodings_loaded:
        try:
            cursor.execute("SELECT img_name, name FROM staff")
            for img_name, name in cursor.fetchall():
                img = cv2.imread(img_name, cv2.IMREAD_GRAYSCALE)
                if img is not None:
                    recognizer = cv2.face.LBPHFaceRecognizer_create()
                    recognizer.train([img], np.array([0]))
                    known_encodings.append(recognizer)
                    known_names.append(name)
            encodings_loaded = True
            print(f"Loaded {len(known_names)} face encodings")
        except Exception as e:
            print(f"Error loading encodings: {e}")

# Register attendance
def register(name: str) -> bool:
    """Register attendance for a recognized staff member"""
    try:
        time = datetime.now().strftime("%H:%M:%S")
        date_now = datetime.now().strftime("%Y-%m-%d")
        
        cursor.execute("SELECT id FROM staff WHERE name=%s", (name,))
        result = cursor.fetchone()
        if not result:
            print(f"Staff member '{name}' not found in database")
            return False
            
        staff_id = result[0]
        cursor.execute(
            "SELECT 1 FROM attended WHERE staff_id=%s AND date=%s", 
            (staff_id, date_now)
        )
        
        if not cursor.fetchone():
            cursor.execute(
                "INSERT INTO attended (staff_id, name, time, date) VALUES (%s, %s, %s, %s)",
                (staff_id, name, time, date_now)
            )
            db.commit()
            print(f"✓ Attendance registered: {name} at {time}")
            return True
    except Exception as e:
        print(f"Error registering attendance: {e}")
        return False
    return False

def main():
    """Main attendance tracking loop"""
    global encodings_loaded
    
    # Initialize webcam
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open webcam")
        return
    
    # Load face cascade
    cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
    face_cascade = cv2.CascadeClassifier(cascade_path)
    
    print("=" * 50)
    print("Face Attendance System")
    print("=" * 50)
    print("Press 'q' to quit")
    print("Loading face encodings in background...")
    print("=" * 50)
    
    # Start loading encodings in background
    threading.Thread(target=load_encodings, daemon=True).start()
    
    # Get recognition config
    recog_config = config['recognition']
    display_config = config['display']
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Error: Failed to capture frame")
                break
                
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(
                gray, 
                recog_config['scale_factor'],
                recog_config['min_neighbors'],
                minSize=tuple(recog_config['min_size'])
            )
            
            if not encodings_loaded and len(faces) > 0:
                load_encodings()
            
            for (x, y, w, h) in faces:
                face_roi = gray[y:y+h, x:x+w]
                
                if encodings_loaded:
                    recognized = False
                    for recognizer, name in zip(known_encodings, known_names):
                        label, confidence = recognizer.predict(face_roi)
                        if confidence < recog_config['confidence_threshold']:
                            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                            cv2.putText(
                                frame, name, (x, y-10),
                                cv2.FONT_HERSHEY_SIMPLEX,
                                display_config['font_scale'],
                                (0, 255, 0),
                                display_config['thickness']
                            )
                            register(name)
                            recognized = True
                            break
                    
                    if not recognized:
                        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 255), 2)
                        cv2.putText(
                            frame, "Unknown", (x, y-10),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            display_config['font_scale'],
                            (0, 0, 255),
                            display_config['thickness']
                        )
                else:
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 255, 0), 2)
                    cv2.putText(
                        frame, "Loading...", (x, y-10),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        display_config['font_scale'],
                        (255, 255, 0),
                        display_config['thickness']
                    )
            
            # Display stats
            status_text = f"Loaded: {len(known_names)} faces | Press 'q' to quit"
            cv2.putText(
                frame, status_text, (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2
            )
            
            display_size = (display_config['width'], display_config['height'])
            cv2.imshow('Attendance', cv2.resize(frame, display_size))
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                print("\nShutting down...")
                break
                
    except KeyboardInterrupt:
        print("\nInterrupted by user")
    finally:
        cap.release()
        cv2.destroyAllWindows()
        db.close()
        print("Cleanup complete")

if __name__ == "__main__":
    main()
