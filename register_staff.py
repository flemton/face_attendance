import cv2
import mysql.connector

db = mysql.connector.connect(user='root', password='qwertyui', host='127.0.0.1', database='attendancedb')
cursor = db.cursor()

img_name = "img/" + input("Enter image name (e.g., 1.jpg): ")
name = input("Enter staff name: ")

cursor.execute("INSERT INTO staff (name, img_name) VALUES (%s, %s)", (name, img_name))
db.commit()

cursor.execute("SELECT id FROM staff WHERE name=%s", (name,))
staff_id = cursor.fetchone()[0]
print("Registered ID:", staff_id)
db.close()