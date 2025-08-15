import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
import cv2
import numpy as np
from datetime import datetime
import mysql.connector
import shutil
import os
import threading

# Database connection
db = mysql.connector.connect(user='root', password='qwertyui', host='127.0.0.1', database='attendancedb')
cursor = db.cursor(buffered=True)

# Global variables for face attendance
known_encodings = []
known_names = []
encodings_loaded = False
cap = None
attendance_window = None
video_label = None

# Load encodings lazily
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

# Update video feed
def update_video():
    global cap, video_label, attendance_window
    if cap is None or video_label is None:
        return

    ret, frame = cap.read()
    if ret:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml').detectMultiScale(gray, 1.1, 3, minSize=(30, 30))

        if not encodings_loaded and len(faces) > 0:
            load_encodings()

        for (x, y, w, h) in faces:
            face_roi = gray[y:y+h, x:x+w]
            if encodings_loaded and face_roi.size > 0:
                recognized = False
                for recognizer, name in zip(known_encodings, known_names):
                    label, confidence = recognizer.predict(face_roi)
                    if confidence < 50:
                        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                        cv2.putText(frame, name, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
                        register(name)
                        recognized = True
                        break
                if not recognized:
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 255), 2)
                    cv2.putText(frame, "Unknown", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)

        # Convert to PIL format
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(frame_rgb)
        imgtk = ImageTk.PhotoImage(image=img)
        video_label.imgtk = imgtk
        video_label.configure(image=imgtk)

    if attendance_window is not None:
        video_label.after(10, update_video)

# Start face attendance
def start_face_attendance():
    global cap, attendance_window, video_label
    if attendance_window is not None:
        return

    threading.Thread(target=load_encodings, daemon=True).start()

    cap = cv2.VideoCapture(0)
    attendance_window = tk.Toplevel(root)
    attendance_window.title("Face Attendance")
    attendance_window.protocol("WM_DELETE_WINDOW", stop_face_attendance)

    video_label = tk.Label(attendance_window)
    video_label.pack()

    update_video()

# Stop face attendance
def stop_face_attendance():
    global cap, attendance_window, video_label
    if cap is not None:
        cap.release()
        cap = None
    if attendance_window is not None:
        attendance_window.destroy()
        attendance_window = None
        video_label = None

# Register staff GUI
def register_staff_gui():
    reg_window = tk.Toplevel(root)
    reg_window.title("Register Staff")

    tk.Label(reg_window, text="Staff Name:").pack(pady=5)
    name_entry = tk.Entry(reg_window)
    name_entry.pack(pady=5)

    def select_image():
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.png")])
        if file_path:
            img_name = f"img/{os.path.basename(file_path)}"
            os.makedirs("img", exist_ok=True)
            shutil.copy(file_path, img_name)
            cursor.execute("INSERT INTO staff (name, img_name) VALUES (%s, %s)", (name_entry.get(), img_name))
            db.commit()
            messagebox.showinfo("Success", "Staff registered!")
            reg_window.destroy()

    tk.Button(reg_window, text="Select Image and Register", command=select_image).pack(pady=10)

# View attendance GUI
def view_attendance_gui():
    view_window = tk.Toplevel(root)
    view_window.title("Attendance Register")

    tree = ttk.Treeview(view_window, columns=("ID", "Staff ID", "Name", "Time", "Date"), show="headings")
    tree.heading("ID", text="ID")
    tree.heading("Staff ID", text="Staff ID")
    tree.heading("Name", text="Name")
    tree.heading("Time", text="Time")
    tree.heading("Date", text="Date")
    tree.pack(fill=tk.BOTH, expand=True)

    cursor.execute("SELECT * FROM attended")
    for row in cursor.fetchall():
        tree.insert("", tk.END, values=row)

# Main GUI
root = tk.Tk()
root.title("Face Attendance System")

tk.Button(root, text="Register Staff", command=register_staff_gui).pack(pady=20)
tk.Button(root, text="View Attendance", command=view_attendance_gui).pack(pady=20)
tk.Button(root, text="Start Face Attendance", command=start_face_attendance).pack(pady=20)

root.mainloop()

# Cleanup on exit
db.close()