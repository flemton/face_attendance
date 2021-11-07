import mysql.connector

#Opening connection to database.
cnx = mysql.connector.connect(user='root', password='qwertyui', host='127.0.0.1', database='attendancedb')
cursor = cnx.cursor()

#taking image url and staff ID/ index number from user
image_name = "img/"+input("Enter image name and directory like '1.jpg' : ")
#staff_id = int(input("Enter staff id number: "))
name = input("Enter name of staff: ")

cursor.execute("INSERT INTO staff (name, img_name) VALUES (%s, %s)", (name, image_name))
#Saving changes to database
cnx.commit()

query = "SELECT id FROM staff WHERE name=%s"
where = (name,)
cursor.execute(query, where)
r = cursor.fetchone()
print("Id for registered person")
print(r[0])
cnx.close()
print("Sucess!")