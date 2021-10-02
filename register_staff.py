import sqlite3

#Opening connection to database.
facedb = sqlite3.connect('attendance.db')
cur = facedb.cursor()

#taking image url and staff ID/ index number from user
image_name = input("Enter image name and directory like 'img/1.jpg' : ")
staff_id = int(input("Enter staff id number: "))
name = input("Enter name of staff: ")
encoded = input("Enter encoded name to give: ")

cur.execute("INSERT INTO staff VALUES (?, ?, ?, ?)", (staff_id, name, image_name, encoded))
#Saving changes to database
facedb.commit()

facedb.close()
print("Sucess!")