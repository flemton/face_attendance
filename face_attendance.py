import sqlite3
import face_recognition
import cv2
import numpy as np
import datetime

#Opening connection to database.
attend = sqlite3.connect('attendance.db')

#Creating table to store attendees and time
cur = attend.cursor()

#For adding name and time to attendance
def register(matches, time):
	
	cur.execute("INSERT INTO Attended VALUES (?, ?)", (matches, time))
	attend.commit()

#For add face seperately if not staff. Good for seeing people who visit or number of people who visit
##under development
##def match_error(no_match):
	##cur.execute("INSERT INTO Error VALUES (?, ?)", no_match)

#Getting access to webcam. 0 for main cam
video_capture = cv2.VideoCapture(0)

#Loading sample pic and learning to recognize
newton_image = face_recognition.load_image_file("newton.jpg")
newton_face_encoding = face_recognition.face_encodings(newton_image)[0]

nick_image = face_recognition.load_image_file("nick.jpg")
nick_face_encoding = face_recognition.face_encodings(nick_image)[0]



#creating arrays of faces and names
known_face_encodings = [
	newton_face_encoding,
	nick_face_encoding
]
known_face_names = [
	"1",
	"Nick"
]

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
	
	#
	if process_this_frame:
		#Find all faces and encodings in current video frame
		face_locations = face_recognition.face_locations(rgb_small_frame)
		face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
		
		face_names = []
		for face_encoding in face_encodings:
			#If there is a match for known faces
			matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
			name = "Unknown"
            		# # If a match was found in known_face_encodings, just use the first one.
			if True in matches:
				first_match_index = matches.index(True)
				name = known_face_names[first_match_index]
				face_names.append(name)
				#Timestamping
				time = datetime.datetime.now()
				register(name, time)
            			
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

# Release handle to the webcam
video_capture.release()
cv2.destroyAllWindows()


#Closing database connection
##attend.close()
