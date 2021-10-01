# face_attendance

## Installation
  * Linux, Mac or Windows(tricky)

### Requirements
  * OpenCV
  * face_recognition

#### Mac or Linux
  * install [pip](https://pip.pypa.io/en/stable/installation/).
  * install [face_recognition](https://github.com/ageitgey/face_recognition/blob/master/README.md#installing-on-mac-or-linux)
  * install OpenCV (just install with pip3 install opencv-python on terminal)

#### Windows
  * Microsoft Visual Studio 2019 (or newer) with C/C++ Compiler installed.
  * install [pip](https://pip.pypa.io/en/stable/installation/) if you haven't already.
  * [Cmake](https://cmake.org/download/)
  * face_recognition (just install with pip install face_recognition ).
  * install OpenCV (just install with pip install opencv-python on terminal)

#### Files and Folders: 
  * /img: Folder to Save images of faces to recognize
  * README.md: Contains all info and instructions for app
  * attendance.db: This is where the Database is stored
  * face_attendance.py: This is the app that does the matching and writing databases
##### dependencies/libraries used:
   * OpenCV (cv2) for getting access to camera
   * face_recognition for identifying faces and running recognitions
   * datetime for getting access to and date-stamping
   * SQLite3 for creating, connecting and manipulating databases
## Usage
   * Make sure all requirements are in place
   * Name image files with simple numbers(staff id/ student id) and save in /img folder
   * Configure by running register_face.py with python (run python register_face.py on windows or python3 register_face.py or Mac/Linux) and follow the prompts
   * After successfully registering all faces, make sure camera is connected
   * Run face_attendance and it'll automatically start register after a known person gets in camera
   * Attendance is stored in attendance.db in Attended table.
   * Continue your daily activities or grab a cup and coffee and sleep after that.
###### Thanks
   * Prof. David J. Malan
   * Brian Yu
   * Doug Llyod
   * CS50
   * All CS50 team
   * Students of CS50
   * All Computer Scientists around the globe.
