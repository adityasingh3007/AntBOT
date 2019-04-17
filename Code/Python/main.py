"""
  * Team Id : 288
  * Author List : Aditya Kumar Singh, Karthik S.
  * Filename: main.py
  * Theme: AntBOT
  * Functions: process_colour(), sort_aruco_details(), main()
  * Global Variables: col[], aruco_id[], aruco_details, path
"""

import SIM_Decoding as SD
import path_planning as PP
import extra
import Aruco_Detect as AD
import ServiceArea_detection as SAD

import RPi.GPIO as GPIO
import serial
import time

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)

col=[]
aruco_id=[]
aruco_details=False
path=""

"""
  * Function Name : process_colour
  * Input : none
  * Output : none
  * Logic : The function assigns the type of supply according to the colours of blocks detected and stores the service locations for the task.
  * Example Call : process_colour()
"""
def process_colour():
    for i in range(0,len(col)):
        if(col[i]=="red"):
            col[i]="Honey Dew"
        elif(col[i]=="blue"):
            col[i]="Wood"
        elif(col[i]=="green"):
            col[i]="Leaves"
    print(col)
    PP.Plan.store_service_location(col)

"""
  * Function Name : sort_aruco_details
  * Input : x - Contains the complete details of the SIM.
  * Output : x.AH_num - Stores the anthill number of the SIM details sent
  * Logic : To extract the anthill number from the SIM details sent. The returned argument x.AH_num acts as a function parameter for the sort function, wherein the            Aruco IDs are sorted in ascending order.
  * Example Call : sort_aruco_details(x)
"""
def sort_aruco_details(x):
    return x.AH_num


"""
  * Function Name : main
  * Input : none
  * Output : none
  * Logic : Integrates the various parts of the main task : Starting off with Aruco detection, it moves on the identification of service blocks and their position.            Having detected the markers, the path planing script is called and the path for completing the run is stored. Subsquently, via serial communication               with arduino nano, the bot traverses the path according to values received previously.
  * Example Call : Called by default from the operating system
"""    

def reorder_index(path,i):
    index=i
    while(path[index]!='s' or path[index]!='o'):
        i=i-1
        if(i==0):
            break
    return index
    
if __name__== "__main__" :
    arduino = serial.Serial()
    #Restarting Serial Communication
    arduino.setDTR(1)
    arduino.setDTR(0)
    i=0                                                                    #Flag variable to track the number of times BOT has stopped
    try:
	    arduino = serial.Serial('/dev/ttyUSB0', timeout=1, baudrate=9600)
    except:
	    print("Serial not available")
	    exit()
    while(True):
        getVal = (arduino.readline())                                   #Reading from serial line
        val = str(getVal).strip("b'").strip("\\n").strip("\\r")
        #print(val)  
        if(val=="Stopped"):
            break
        else:
            arduino.write('s'.encode())                                #To start the bot to bring it to the start node. 's' stands for move straight
    arduino.write('n'.encode())                                        # To stop the bot.
    time.sleep(0.5)
    arduino.write('s'.encode())   
    time.sleep(0.5)
    #Execute Arucos Detection
    print("Starting Arucos Detection")
    AD.start_camera()     # Switching on the pi camera by calling the required function from the module Aruco_Detect(AD)
    time.sleep(0.1)
    arduino.write('z'.encode()) # z corresponds to calling a function in nano to make the bot specifically move for detecting the Aruco IDs
    time.sleep(0.5)  
    aruco_id=AD.scan_aruco()  #Calling upon the function in module Aruco_Detect(AD) to scan the SIMs by means of the aruco library files.
    aruco_id=[146,54,65,122]
    print("ARUCOs detetion complete....")
    #print(aruco_id)
    val=""
    aruco_details=SD.extract_full_details(aruco_id) #Calling upon a function from SIM_Decoding module to create a list of 4 objects(the 4 anthills). Each object contanins the specific details extracted from the Aruco IDs
    aruco_details.sort(key=sort_aruco_details) #Sorting the Anthill numbers in ascending order
    arduino.flushInput() #To flush the buffer of arduino nano and hence avoid errors
    while(True):
        getVal = (arduino.readline())                                   #Reading from serial line
        val = str(getVal).strip("b'").strip("\\n").strip("\\r")
        #print(val)  
        if(val=="Stopped"):
            arduino.write('r'.encode()) 
            time.sleep(0.5)
            break
    #Execute Block Detection
    print("\nStarting Service Area Detection...")  
    bl=['s','s','s','o','o','b','s','T','s','T','s','T','s','s','T','s','T','s','T','o','s','s','s','r','b','s','b','s']      #Array contaning the list of commands which the bot follows to detect the supply blocks in the shrub area. Here, s = Straight, o = 180 degree turn, r = right, 
    index=-1 
    arduino.flushInput()
    while(True):
        if(index>=len(bl)-1):
            break
        getVal = (arduino.readline())                                   #Reading from serial line
        val = str(getVal).strip("b'").strip("\\n").strip("\\r")
        #print(val)  
        if(val=="Stopped"):
            index+=1
            if(bl[index]!='T'):   
                arduino.write(bl[index].encode()) 
                time.sleep(0.5)
            else:
                ret=SAD.scan_block() #Calling upon a function from ServiceArea_detection module to detect the colour of the block
                col.append(ret) 
                print("Service Area Configuration: " + str(col))
                if(ret=="red"):
                    extra.RGB.Red() #Calling upon a function from 'extra' module to glow red light from the RGB LED
                elif(ret=="blue"):
                    extra.RGB.Blue() #Calling upon a function from 'extra' module to glow blue light from the RGB LED
                elif(ret=="green"):
                    extra.RGB.Green() #Calling upon a function from 'extra' module to glow green light from the RGB LED
                index+=1
                arduino.write(bl[index].encode()) 
                time.sleep(0.5)
    #print(col)
    process_colour()  #The respective parameters get assigned to the colour blocks detected.
    print("Service Area Detection Completed..")  
    
    #Execute path planning
    print("\nNow Executing path Planning..")
    path=PP.get_path(aruco_details)
    #print(path)
    #print(len(path))
    arduino.flushInput()
    arduino.write(path[0].encode()) 
    time.sleep(0.5)
    i=1
    while(1):
        getVal = (arduino.readline())                                   #Reading from serial line
        val = str(getVal).strip("b'").strip("\\n").strip("\\r")       
        if(val=="Stopped"):
            ch=path[i] #stores each character retrived from path planning. Each character corresponds to a command for the bot to move/ stop in a specific manner
            #print(ch)
            i+=1
            if(ch=="R" or ch=="G" or ch=="B" or ch=="Y"):
                if(ch=="R"):
                    extra.RGB.Red()
                elif(ch=="G"):
                    extra.RGB.Green()
                elif(ch=="B"):
                    extra.RGB.Blue()
                elif(ch=="Y"):
                    extra.RGB.Yellow()
                ch=path[i]
                i+=1
            if(ch=="g"): #Checking if
                arduino.write('g'.encode())                     # Writing 'b' on the serial line
                time.sleep(2)
                ret=SAD.scan_yellow()
                if(ret==True):
                    arduino.write('t'.encode())                     # Writing 'b' on the serial line
                    time.sleep(0.5)
                else:
                    arduino.write('T'.encode())                     # Writing 'b' on the serial line
                    time.sleep(0.5)
                arduino.flushInput()
                continue
            arduino.write(ch.encode())                     # Writing 'b' on the serial line
            time.sleep(1)
        if(val=="Repos"):
                print("Repositioning is required.....")
                i=reorder_index(path,i)
                print(i)
                while(True):
                   """
                   response=input("Continue? ")
                   if(response=="Yes" or response=="yes" or response=="Y" or response=="y"):
                    
                       break
                    else:
                       continue
                   """
                   getVal = (arduino.readline())                                   #Reading from serial line
                   val = str(getVal).strip("b'").strip("\\n").strip("\\r")   
                   print(val)    
                   if(val=="Reposdone"):
                      time.sleep(2)
                      break
                arduino.flushInput()
        if(i==len(path)):
            print("Run Over")
            extra.Buzzer.on() #Calling upon a function from 'extra' module to switch on the buzzer
            extra.RGB.off() #Calling upon a function from 'extra' module to switch off the buzzer
            GPIO.cleanup()
            break
        
