#!/usr/bin/env python3
"""
Staff Registration Script for Face Attendance System
"""

import cv2
import mysql.connector
import os
import json
import sys

def load_config():
    """Load configuration from config.json"""
    if os.path.exists('config.json'):
        with open('config.json', 'r') as f:
            return json.load(f)
    return {
        "database": {
            "user": "root",
            "password": "qwertyui",
            "host": "127.0.0.1",
            "database": "attendancedb"
        }
    }

def get_db_connection(config):
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
        sys.exit(1)

def verify_image(img_path):
    """Verify that the image exists and contains a face"""
    if not os.path.exists(img_path):
        print(f"❌ Error: Image file not found: {img_path}")
        return False
    
    img = cv2.imread(img_path)
    if img is None:
        print(f"❌ Error: Could not read image: {img_path}")
        return False
    
    # Check for face in image
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    face_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
    )
    faces = face_cascade.detectMultiScale(gray, 1.1, 4)
    
    if len(faces) == 0:
        print("⚠️  Warning: No face detected in image")
        response = input("Continue anyway? (y/n): ")
        return response.lower() == 'y'
    elif len(faces) > 1:
        print(f"⚠️  Warning: Multiple faces detected ({len(faces)})")
        response = input("Continue anyway? (y/n): ")
        return response.lower() == 'y'
    else:
        print(f"✓ Face detected in image")
        return True

def main():
    print("=" * 50)
    print("Staff Registration")
    print("=" * 50)
    
    config = load_config()
    db = get_db_connection(config)
    cursor = db.cursor()
    
    try:
        # Get staff information
        name = input("\nEnter staff name: ").strip()
        if not name:
            print("❌ Error: Name cannot be empty")
            return
        
        img_name = input("Enter image filename (e.g., john_doe.jpg): ").strip()
        if not img_name:
            print("❌ Error: Image filename cannot be empty")
            return
        
        img_path = os.path.join("img", img_name)
        
        # Check if image exists and has face
        if not verify_image(img_path):
            print("❌ Registration cancelled")
            return
        
        # Check for duplicate names
        cursor.execute("SELECT id FROM staff WHERE name=%s", (name,))
        if cursor.fetchone():
            print(f"❌ Error: Staff member '{name}' already exists")
            return
        
        # Insert into database
        cursor.execute(
            "INSERT INTO staff (name, img_name) VALUES (%s, %s)",
            (name, img_path)
        )
        db.commit()
        
        # Get the ID
        cursor.execute("SELECT id FROM staff WHERE name=%s", (name,))
        staff_id = cursor.fetchone()[0]
        
        print("=" * 50)
        print(f"✓ Staff registered successfully!")
        print(f"  ID: {staff_id}")
        print(f"  Name: {name}")
        print(f"  Image: {img_path}")
        print("=" * 50)
        
    except mysql.connector.Error as err:
        print(f"❌ Database error: {err}")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        cursor.close()
        db.close()

if __name__ == "__main__":
    main()
