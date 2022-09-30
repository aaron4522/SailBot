import board
import busio
#import adafruit_pca9685 as pcaLib
import constants as c
import stepper
from threading import Thread
from windvane import windVane
from RPi import GPIO
from time import sleep
from Odrive import Odrive

USE_ODRIVE_SAIL = False
USE_STEPPER_SAIL = False

USE_ODRIVE_RUDDER = True
USE_STEPPER_RUDDER = False

if USE_ODRIVE_SAIL or USE_ODRIVE_RUDDER:
    DRV = Odrive(calibrate=True)
            
if False:
    SAIL_DIR_PIN = 17 #22
    SAIL_PUL_PIN = 4 #27
    RUDDER_DIR_PIN = 22 #17
    RUDDER_PUL_PIN = 27 #4
else:
    SAIL_DIR_PIN = 22
    SAIL_PUL_PIN = 27
    RUDDER_DIR_PIN = 17
    RUDDER_PUL_PIN = 4

class obj_sail:
            
    def __init__(self, auto = False):
        #self.channel =  pca.channels[channel_index]
        self.autoAdjust = auto
        #self.windvane = windVane()
        self.current = 0
        if USE_STEPPER_SAIL:
            self.step = stepper.stepperDriver(SAIL_DIR_PIN, SAIL_PUL_PIN)
        if USE_ODRIVE_SAIL:
            self.odriveAxis = DRV.axis1
        #pump_thread2 = Thread(target=self.autoAdjustSail)
        #pump_thread2.start()

    def map(self, x, min1, max1, min2, max2):
        x = min(max(x, min1), max1)
        return min2 + (max2-min2)*((x-min1)/(max1-min1))

    def set(self, degrees):
        degrees = float(degrees)
            
        maxAngle = 900
        if degrees > maxAngle:
            degrees = maxAngle

        if USE_STEPPER_SAIL:
            self.steps = int(400/360 * (self.current-degrees) ) * 15
            
            if degrees < self.current:
                self.step.turn(False, self.steps)
            else:
                self.step.turn(True, -self.steps)

        if USE_ODRIVE_SAIL:
            val = self.map(degrees, 0, 90, 0, float(c.config['ODRIVE']['odriveSailRotations']))
            DRV.posSet(self.odriveAxis, val)
            
        self.current = degrees
    
    def autoAdjustSail(self):
        while True:
            if self.autoAdjust == True:
                windDir = self.windvane.angle
                if windDir > 180:
                    windDir = 180 - (windDir - 180)
                targetAngle = max(min(windDir / 2, 90), 3)
                self.set(targetAngle)

                
class obj_rudder:
    # 800 steps = 360 degrees
    #between -45 and 45 degrees
    def __init__(self):
        self.current = 0
        if USE_STEPPER_RUDDER:
            self.step = stepper.stepperDriver(RUDDER_DIR_PIN, RUDDER_PUL_PIN)
        if USE_ODRIVE_RUDDER:
            self.odriveAxis = DRV.axis0

    def map(self, x, min1, max1, min2, max2):
        x = min(max(x, min1), max1)
        return min2 + (max2-min2)*((x-min1)/(max1-min1))
    
    def set(self, degrees):

        degrees = float(degrees)
        
        maxAngle = 30

        if USE_STEPPER_RUDDER:
            if degrees > maxAngle:
                degrees = maxAngle
            elif degrees < -maxAngle:
                degrees = -maxAngle
            self.steps = int(400/360 * (self.current-degrees) ) * 50
            
            if degrees < self.current:
                self.step.turn(True, self.steps)
            else:
                self.step.turn(False, -self.steps)

        if USE_ODRIVE_RUDDER:
            val = self.map(degrees, -maxAngle, maxAngle, -float(c.config['ODRIVE']['odriveRudderRotations'])/2, float(c.config['ODRIVE']['odriveRudderRotations'])/2)
            DRV.posSet(self.odriveAxis, val)
            

        self.current = degrees

class driver:

    def __init__(self):
        self.sail = obj_sail()
        self.rudder = obj_rudder()

if __name__ == "__main__":
    drive = driver()

    while True:
        string = input("  > Enter Input:")
        
        if string == "quit":
            break
        
        arr = string.split(" ")
        
        if arr[0] == "sail":
            val = int(arr[1])
            drive.sail.set(val)
            
        elif arr[0] == "rudder" or arr[0] == 'r':
              drive.rudder.set(int(arr[1]))
              
        elif arr[0] == "stepper" or arr[0] == 's':
            stepper = stepperMotor()
            stepper.step(int(arr[1]))
