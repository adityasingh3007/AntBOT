"""
  * Team Id : 288
  * Author List : Karthik S.
  * Filename: Aruco_Detect.py
  * Theme: AntBOT
  * Functions: scan_block(), scan_yellow():
  * Global Variables: None
"""
import time
from time import sleep                      #Importing sleep from time library 
import RPi.GPIO as GPIO                     #Importing RPi.GPIO library
from picamera import PiCamera
from picamera.array import PiRGBArray
import cv2                                  #Importing cv2 and numpy for image processing
import numpy as np

"""
 * Function Name:  scan_block
 * Input: None
 * Output: Colour which is detected (Red or Green or Blue as string)
 * Logic: At each of the service area node, bot will stop and then picam will be turnned on. It will try to detect all
          the three contours corresponding to Blue, Green, Red colour respectively. Then that colurs is returned which
          is having the maximum contour among them plus the area should be greater than 200 (considering noises). 
          If no contour is detected "none" is returned.
 * Example Call: scan_block()
"""      
def scan_block():
    camera=PiCamera()                       # starting the picam and giving the neccesary information
    camera.resolution=(160,112)             
    rc=PiRGBArray(camera,(160,112))
    camera.framerate=90
    sleep(0.5)

    param1 = [[70,20,20],[50,30,30],[0,30,30]]                              #Lower bound for all the three colours (BGR in HSV values)
    param2 = [[120,255,255],[84,255,255],[5,255,255]]                    #Upper bound for all the three colours (BGR in HSV values)
    kernelOpen=np.ones((5,5))
    kernelClose=np.ones((20,20))
    max=0                                                                 #To store the max contour area
    val=-1                                                                #To store the index value for which max contour area was detected
    for image in camera.capture_continuous(rc, format="bgr", use_video_port=True):
                 frame = image.array                                      #storing the current frame in an image
                 hsv = cv2.cvtColor(frame,cv2.COLOR_BGR2HSV)              #converting to HSV format
                 max=0
                 for i in range(0,3):                                     #checking contours starting from Blue->Green->Red
                   #Getting the corresponding boundary values
                   lower = np.array(param1[i])
                   upper = np.array(param2[i])
                   mask  = cv2.inRange(hsv, lower, upper)
                   #Applying the morphological tranformations
                   maskOpen=cv2.morphologyEx(mask,cv2.MORPH_OPEN,kernelOpen)   
                   maskClose=cv2.morphologyEx(maskOpen,cv2.MORPH_CLOSE,kernelClose)
                   maskFinal=maskClose
                   max_area= (cv2.countNonZero(maskFinal))                     #Getting area for the current contour
                   print(max_area)
                   if(max_area>max):                                      #Updating the max contour(if possible)
                      max=max_area
                      val=i                                               #Storing the index for which max contour area was detected
                 if val==0 and max>200:
                    camera.close()
                    return "blue"
                 elif val==1 and max>200:
                    camera.close()
                    return "green"
                 elif val==2 and max>200:
                    camera.close()
                    return "red"
                 else:
                    camera.close()
                    return "none"
                 rc.truncate(0)                

"""
 * Function Name:  scan_yellow
 * Input: None
 * Output: True or False (based on whether Yellow colour was detected or not)
 * Logic: This will scan the yellow colour in the frame, if found within 2s, return true or else return false
 * Example Call: scan_yellow()
"""      
def scan_yellow():
    camera=PiCamera()                       # starting the picam and giving the neccesary information
    camera.resolution=(160,112)             
    rc=PiRGBArray(camera,(160,112))
    camera.framerate=90
    sleep(0.5)

    param1 = [15,30,30]                    #Lower bound for yellow colour(in HSV values)
    param2 = [40,255,100]                 #Upper bound for yellow(in HSV values)
    time_start = time.time()
    kernelOpen=np.ones((5,5))
    kernelClose=np.ones((20,20))
    for image in camera.capture_continuous(rc, format="bgr", use_video_port=True):
                 frame = image.array                                      #storing the current frame in an image
                 hsv = cv2.cvtColor(frame,cv2.COLOR_BGR2HSV)              #converting to HSV format
                 #Getting the corresponding boundary values
                 lower = np.array(param1)
                 upper = np.array(param2)
                 mask  = cv2.inRange(hsv, lower, upper)
                 #Applying the morphological tranformations
                 maskOpen=cv2.morphologyEx(mask,cv2.MORPH_OPEN,kernelOpen)   
                 maskClose=cv2.morphologyEx(maskOpen,cv2.MORPH_CLOSE,kernelClose)
                 maskFinal=maskClose
                 max_area= (cv2.countNonZero(maskFinal))                     #Getting area for the current contour
                 if(max_area >= 2000):
                    camera.close()
                    print("Yellow")
                    return True
                 time_current=time.time()
                 if(time_current - time_start >= 2):
                    camera.close()
                    return False
                 rc.truncate(0)                
