import sqlite3
import face_recognition
import cv2
import numpy as np
import datetime

#Opening connection to database.
attend = sqlite3.connect('attendance.db')

#Connecting to database
cur = attend.cursor()

#For adding name and time to attendance
def register(name):
	
	#Getting today's date
	date = datetime.datetime.now()
	day = date.strftime("%d")
	month = date.strftime("%m")
	year = date.strftime("%y")
	time = datetime.datetime.now().strftime("%X")
	#cur.execute("INSERT INTO dates(day, month, year) VALUES (?, ?, ?)", (day, month, year))
	#attend.commit()
	
	#date_id = cur.execute("SELECT id FROM dates WHERE day=? AND month = ? AND year = ?", (day, month, year))
	staff_id = 1

	cur.execute("INSERT INTO Attended VALUES (?, ?, ?, ?, ?, ?)", (staff_id, name, time, day, month, year))
	attend.commit()

#Getting access to webcam. 0 for main cam
video_capture = cv2.VideoCapture(0)

#creating arrays of faces and names(staff id's or student id's)
known_face_encodings = []
staff_ids = []
known_names = []

#querying face_encodings and corresponding ids from database
encs = cur.execute("SELECT img_name, name FROM Staff")
for row in encs:
	
	#Loading sample pic and learning to recognize
	face = face_recognition.load_image_file(row[0])
	encoding = face_recognition.face_encodings(face)[0]
	known_face_encodings.append(encoding)
	known_names.append(row[1])



#initializing some variables
face_locations = []
face_encodings = []
face_names = []
process_this_frame = True

while True:
	#Grab a frame from video
	ret, frame = video_capture.read()
	
	#Resizing video frame to 1/4 for faster recognition processing
	small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
	
	#Convert image from BGR color(OpenCV) to RGB color(face_recognition compatible)
	rgb_small_frame = small_frame[:, :, ::-1]

	if process_this_frame:
		#Find all faces and encodings in current video frame
		face_locations = face_recognition.face_locations(rgb_small_frame)
		face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
		
		face_names = []
		for face_encoding in face_encodings:
			#If there is a match for known faces
			matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
			name = "Unknown"

			#Timestamping

            #If a match was found in known_face_encodings, just use the first one.
			if True in matches:
				first_match_index = matches.index(True)
				name = known_names[first_match_index]
				face_names.append(name)
				register(name)
          			
	process_this_frame = not process_this_frame
	
	# Display the results
	for (top, right, bottom, left), name in zip(face_locations, face_names):
        	# Scale back up face locations since the frame we detected in was scaled to 1/4 size
		top *= 4
		right *= 4
		bottom *= 4
		left *= 4

        	# Draw a box around the face
		cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

        	# Draw a label with a name below the face
		cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
		font = cv2.FONT_HERSHEY_DUPLEX
		cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

	# Display the resulting image
	cv2.imshow('Video', frame)

	# Hit 'q' on the keyboard to quit!
	if cv2.waitKey(1) & 0xFF == ord('q'):
		break

#Closing database connection
attend.close()

# Release handle to the webcam
video_capture.release()
cv2.destroyAllWindows()