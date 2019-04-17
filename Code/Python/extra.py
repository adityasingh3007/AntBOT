"""
  * Team Id : 288
  * Author List : Aditya Kumar Singh
  * Filename: extra.py
  * Theme: AntBOT
  * Functions: None
  * Global Variables: Buzzer(object), RGB(object)
"""

import RPi.GPIO as GPIO                                               #Importing RPi GPIO library y
from time import sleep                                                #Importing sleep from Time library

GPIO.setwarnings(False)                                               #Disabling GPIO warnings
GPIO.setmode(GPIO.BOARD)                                              #Setting PIN numbering system

"""
  * Class Name: buzzer
  * Member(s): pin
  * Functions: __init__(self), on(self), off(self)
  * Example for Object Creation: buzzer()
"""
class buzzer:
      pin = 7                                                         #PIN number to which buzzer's I\O pin will be connected
      
      """
         Construction function for the class
      """
      def __init__(self):
            GPIO.setup(self.pin,GPIO.OUT)
            GPIO.output(self.pin,GPIO.LOW)
      """
        * Function Name: on
        * Input: None
        * Output: none
        * Logic: This function turns the buzzer ON for 5 seconds. 
        * Example Call: buzzer.on()
      """      
      def on(self):
            GPIO.output(self.pin,GPIO.HIGH)
            sleep(5)                            #Finals 5sec
            self.off()
      
      """
        * Function Name: off
        * Input: None
        * Output: none
        * Logic: This function turn the buzzer OFF. 
        * Example Call: buzzer.on()
      """      
      def off(self):
            GPIO.output(self.pin,GPIO.LOW)

"""
  * Class Name: rgb
  * Member(s): red, blue, green, R, G, B
  * Functions: __init__(self), Red(self), Green(self), Blue(self), Yellow(self), off(self)
  * Example for Object Creation: rgb()
"""
class rgb:
      red = 15
      blue = 13
      green = 11
      R = False
      B = False
      G = False
      
      """
         Construction function for the class
      """
      def __init__(self):
            GPIO.setup(self.red,GPIO.OUT)
            GPIO.setup(self.blue,GPIO.OUT)
            GPIO.setup(self.green,GPIO.OUT)
            
            self.R=GPIO.PWM(self.red,100)
            self.G=GPIO.PWM(self.green,100)
            self.B=GPIO.PWM(self.blue,100)
            
            self.R.start(100)
            self.G.start(100)
            self.B.start(100)
      
      """
        * Function Name: Red
        * Input: None
        * Output: none
        * Logic: This function will glow the RED colour on RGB LED
        * Example Call: rgb.Red()
      """         
      def Red(self):
            self.R.ChangeDutyCycle(0)
            self.G.ChangeDutyCycle(100)
            self.B.ChangeDutyCycle(100)
            sleep(1)
            self.off()
      
      """
        * Function Name: Green
        * Input: None
        * Output: none
        * Logic: This function will glow the GREEN colour on RGB LED
        * Example Call: rgb.Green()
      """ 
      def Green(self):
            self.R.ChangeDutyCycle(100)
            self.G.ChangeDutyCycle(0)
            self.B.ChangeDutyCycle(100)
            sleep(1)
            self.off()
      
      """
        * Function Name: Blue
        * Input: None
        * Output: none
        * Logic: This function will glow the BLUE colour on RGB LED
        * Example Call: rgb.Blue()
      """      
      def Blue(self):
            self.R.ChangeDutyCycle(100)
            self.G.ChangeDutyCycle(100)
            self.B.ChangeDutyCycle(0)
            sleep(1)
            self.off()
      
      """
        * Function Name: Yellow
        * Input: None
        * Output: none
        * Logic: This function will glow the Yellow colour on RGB LED
        * Example Call: rgb.Yellow()
      """     
      def Yellow(self):
            self.R.ChangeDutyCycle(0)
            self.G.ChangeDutyCycle(0)
            self.B.ChangeDutyCycle(100)
            sleep(1)
            self.off()
      
      """
        * Function Name: off
        * Input: None
        * Output: none
        * Logic: This function will turn off the RGB LED
        * Example Call: rgb.off()
      """      
      def off(self):
            self.R.ChangeDutyCycle(100)
            self.G.ChangeDutyCycle(100)
            self.B.ChangeDutyCycle(100)
            sleep(1)

#Creating object of each class                  
Buzzer=buzzer()
RGB = rgb()
RGB.off()

"""
RGB.Red()
RGB.Blue()
RGB.Green()
RGB.Yellow()
Buzzer.on()
GPIO.cleanup()
"""