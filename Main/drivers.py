import board
import busio
#import adafruit_pca9685 as pcaLib
import constants as c
import stepper
from threading import Thread
from windvane import windVane
from RPi import GPIO
from time import sleep
            

SAIL_DIR_PIN = 17 #22
SAIL_PUL_PIN = 4 #27
RUDDER_DIR_PIN = 22 #17
RUDDER_PUL_PIN = 27 #4

class obj_sail:
            
    def __init__(self, auto = False):
        #self.channel =  pca.channels[channel_index]
        self.autoAdjust = auto
        #self.windvane = windVane()
        self.current = 0
        self.step = stepper.stepperDriver(SAIL_DIR_PIN, SAIL_PUL_PIN)
        #pump_thread2 = Thread(target=self.autoAdjustSail)
        #pump_thread2.start()

    def map(self, x, min1, max1, min2, max2):
        x = min(max(x, min1), max1)
        return min2 + (max2-min2)*((x-min1)/(max1-min1))

    def set(self, degrees):
            
        maxAngle = 90
        if degrees > maxAngle:
            degrees = maxAngle

        self.steps = int(400/360 * (self.current-degrees) ) * 10
        
        if degrees < self.current:
            self.step.turn(False, self.steps)
        else:
            self.step.turn(True, -self.steps)
            
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
        self.step = stepper.stepperDriver(RUDDER_DIR_PIN, RUDDER_PUL_PIN)
    
    def set(self, degrees):
        
        maxAngle = 30
        if degrees > maxAngle:
            degrees = maxAngle
        elif degrees < -maxAngle:
            degrees = -maxAngle
        self.steps = int(400/360 * (self.current-degrees) ) * 50
        
        if degrees < self.current:
            self.step.turn(False, self.steps)
        else:
            self.step.turn(True, -self.steps)
            

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
            
        elif arr[0] == "rudder":
              drive.rudder.set(int(arr[1]))
              
        elif arr[0] == "stepper":
            stepper = stepperMotor()
            stepper.step(int(arr[1]))
