import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
import face_recognition
import numpy as np
from datetime import datetime
import mysql.connector
import shutil
import os
import threading
import logging

# Setup logging for debugging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

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
        staff_data = cursor.fetchall()
        if not staff_data:
            logging.warning("No staff data found in database.")
            return
        for img_name, name in staff_data:
            img = face_recognition.load_image_file(img_name)
            encoding = face_recognition.face_encodings(img)
            if encoding:
                known_encodings.append(encoding[0])
                known_names.append(name)
                logging.info(f"Loaded encoding for {name}")
            else:
                logging.error(f"Failed to encode image: {img_name}")
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
        logging.info(f"Registered attendance for {name} at {time}")

# Update video feed with face_recognition
def update_video():
    global cap, video_label, attendance_window
    if cap is None or video_label is None or attendance_window is None:
        return

    ret, frame = cap.read()
    if not ret:
        logging.error("Failed to capture video frame.")
        return

    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    face_locations = face_recognition.face_locations(rgb_frame)
    face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

    if not encodings_loaded and face_locations:
        threading.Thread(target=load_encodings, daemon=True).start()

    for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
        matches = face_recognition.compare_faces(known_encodings, face_encoding, tolerance=0.6)
        name = "Unknown"
        if True in matches:
            match_index = matches.index(True)
            name = known_names[match_index]
            logging.debug(f"Match found for {name} with tolerance 0.6")
            register(name)

        # Draw rectangle and label
        color = (0, 255, 0) if name != "Unknown" else (0, 0, 255)
        cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
        cv2.putText(frame, name, (left, top-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)

    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    img = Image.fromarray(frame_rgb)
    imgtk = ImageTk.PhotoImage(image=img)
    video_label.imgtk = imgtk
    video_label.configure(image=imgtk)
    video_label.after(10, update_video)

# Start face attendance
def start_face_attendance():
    global cap, attendance_window, video_label
    if attendance_window is not None:
        return

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
            # Verify image load
            test_img = face_recognition.load_image_file(img_name)
            if test_img is None:
                messagebox.showerror("Error", f"Failed to load image: {img_name}")
                os.remove(img_name)
                return
            cursor.execute("INSERT INTO staff (name, img_name) VALUES (%s, %s)", (name_entry.get(), img_name))
            db.commit()
            messagebox.showinfo("Success", "Staff registered! Restart attendance to retrain.")
            reg_window.destroy()
            global encodings_loaded
            encodings_loaded = False

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
if cap is not None:
    cap.release()
db.close()