# face_attendance

## Installation
  * Linux, Mac or Windows

### Requirements
  * install python 3.8.0 (very important)
  * install Mysql (Community edition)
  * install Cmake (`pip3 install cmake`)
  * open terminal or cmd in project folder and run `pip3 install -r requirements.txt`

#### Works on Windows, Linux and Mac

#### Files and Folders: 
  * /img: Folder to Save images of faces to recognize
  * README.md: Contains all info and instructions for app
  * attendancedb: This is where the Database is stored
  * face_attendance.py: This is the app that does the matching and writing databases
##### dependencies/libraries used:
   * OpenCV (cv2) for getting access to camera
   * face_recognition for identifying faces and running recognitions
   * datetime for getting access to and date-stamping
   * mysql connector for creating, connecting and manipulating databases
## Usage
   * Make sure all requirements are in place
   * If first time using, 
   * 1. create database with the mysql script (01 - Create Database.sql)
   * 2. Open face_attendance.py with a text editor (notepad or any) go to line 8, change user and password to your database user and password. 
   * Name image files with simple short names, note image file extensions and copy to 'img' folder
   * Configure by running register_staff.py with python (run `python register_staff.py` on windows or `python3 register_face.py` on Mac/Linux) and follow the prompts
   * After successfully registering all staffs, make sure camera is connected
   * Run face_attendance and it'll automatically start register after a known person gets in camera
   * Attendance is stored in attended table.
   * Continue your daily activities or grab a cup and coffee and sleep after that.
###### Thanks
   * Nick
   * Prof. David J. Malan
   * Brian Yu
   * Doug Llyod
   * All CS50 team
   * Students of CS50
   * All Computer Scientists around the globe.
