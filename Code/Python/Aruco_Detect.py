"""
  * Team Id : 288
  * Author List : Aditya Kumar Singh, Karthik S.
  * Filename: Aruco_Detect.py
  * Theme: AntBOT
  * Functions: start_camera(), aruco_detect(img), scan_arco()
  * Global Variables: ids, camera rc
"""

from picamera import PiCamera                              #Importing PiCamera library
from picamera.array import PiRGBArray
from time import sleep
import cv2
import aruco_lib as lib                                    #Importing Aruco_lib to detect the Arucos present in an image 
import serial 


global ids
global camera
global rc

ids=[]                                                     #To store all the ids detected
camera=False                                               #To store the camera object once it is created
rc=False                                                   #To store PiRGBArray object


"""
  * Function Name: start_camera
  * Input: None
  * Output: none
  * Logic: This function initialises the PiCamera with 432x320 resolution @ 90 fps. 
  * Example Call: start_camera()
"""
def start_camera():
  global camera
  global rc
  camera=PiCamera()
  camera.resolution=(432,320)
  rc=PiRGBArray(camera,(432, 320))
  camera.framerate=90
  sleep(1)

"""
  * Function Name: aruco_detect
  * Input: img, Image for which Aruco needs to be identified
  * Output: none
  * Logic: This function accepts the image and pass it to aruco_lib module for aruco detection. The value
           returned from the aruco_lib module is then processed and checked whether the
           sent image was having some Aruco in it or not. If it is there, then store the ID in the 'ids'
           list. This will also check if duplicate entry is going to be there, then it wont add that id.
  * Example Call: aruco_detect()
"""
def aruco_detect(img):
  id_aruco_trace = 0                                                       #to store the state of the bot (centre(x), centre(y), angle)
  det_aruco_list = {}                                                      #to store the detected aruco list dictionary with id and corners
  det_aruco_list = lib.detect_Aruco(img)                                   #detecting arucos in the given image
  if det_aruco_list:
    img3 = lib.mark_Aruco(img,det_aruco_list)
    id_aruco_trace = lib.calculate_Robot_State(img3,det_aruco_list)
    for x,y in id_aruco_trace.items():                                     #id value will be stored in x
      if(str(x).isnumeric()):
        if x not in ids:
          print("ID detected: "+str(x))
          ids.append(x)

"""
  * Function Name: scan_aruco
  * Input: None
  * Output: returns the list of ids detected when all the Four ids are detected
  * Logic: This function will start the PiCam and start reading each image frame by frame.
           Each frame is checked whether it contains any aruco markers or not. Once all 4 ids are detected,
           automatically it will break from the loop and will return the id list. Or else, to manually exit from loop
           'q' is pressed.
  * Example Call: scan_aruco()
"""
def scan_aruco():
  global camera
  global rc
  for image in camera.capture_continuous(rc, format="bgr", use_video_port=True):           #Scan frame by frame
      frame = image.array                                                                    #storing the image in frame variable
      """
      Converting the image into binary image to show on laptop screen 
      gray=cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)                                            
	    ret,bin=cv2.threshold(gray,60,255,cv2.THRESH_BINARY)
      cv2.imshow('frame',bin)
      """
      ret=aruco_detect(frame)                                                                #Check for Aruco markers
      key=cv2.waitKey(1) & 0xFF
      rc.truncate(0)
      if key==ord('q') or len(ids)==4:
          camera.close()                                                               #Close the camera
          return ids
