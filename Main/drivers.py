import board
import busio
import adafruit_pca9685 as pcaLib
import constants as c
import stepper
from threading import Thread
from windvane import windVane
from RPi import GPIO
from time import sleep

class stepperMotor():
    def __init__(self):
        self.motorPin = 5
        self.dirPin = 6
        self.sleepTime = .00005
        self.stepping = False

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.motorPin, GPIO.OUT)
        GPIO.setup(self.dirPin, GPIO.OUT)
    def step(self, steps):
        if self.stepping == True:
            return False
        
        stepThread = Thread(target=self.step_Thread, args=[steps])
        stepThread.start()
        
    def step_Thread(self, steps):
        
        if steps < 0:
            GPIO.output(self.dirPin, 0)
            steps = -steps
        else:
            GPIO.output(self.dirPin, 1)

        for i in range(steps):
            GPIO.output(self.motorPin, 1)
            sleep(self.sleepTime)
            GPIO.output(self.motorPin, 0)
            sleep(self.sleepTime)

        self.stepping = False
            
class obj_sail:
            
    servo_min = float(c.config['CONSTANTS']['sail_servo_min'])
    servo_max = float(c.config['CONSTANTS']['sail_servo_max'])
            
    angle_min = float(c.config['CONSTANTS']['sail_angle_min'])
    angle_max = float(c.config['CONSTANTS']['sail_angle_max'])
            
    def __init__(self, pca, channel_index, auto):
        #self.channel =  pca.channels[channel_index]
        self.autoAdjust = auto
        self.windvane = windVane()
        pump_thread2 = Thread(target=self.autoAdjustSail)
        pump_thread2.start()

    def map(self, x, min1, max1, min2, max2):
        x = min(max(x, min1), max1)
        return min2 + (max2-min2)*((x-min1)/(max1-min1))

    def set(self, degrees):
            
        val = self.map(degrees, self.angle_min, self.angle_max,
                  self.servo_min, self.servo_max)

        self.channel.duty_cycle = int(val)
        return
    
    def autoAdjustSail(self):
        while True:
            if self.autoAdjust == True:
                windDir = self.windvane.angle
                if windDir > 180:
                    windDir = 180 - (windDir - 180)
                targetAngle = max(min(windDir / 2, 90), 3)
                self.set(targetAngle)

                
class obj_rudder:
    # 200 steps = 360 degrees
    #between -45 and 45 degrees
    def __init__(self):
        self.current=0
        self.step = stepper.stepperDriver(17,27)
    
    def set(self, degrees):
        
        self.steps = int(400/360 * (self.current-degrees) )
        print(self.steps)
        
        if degrees < self.current:
            self.step.turn(False, self.steps, .001, True, .05)
        else:
            self.step.turn(True, -self.steps, .001, True, .05)
            
<<<<<<< HEAD
        self.current = degrees

    """        
    servo_min = c.config['MAIN']['RUDDER_SERVO_MIN']
    servo_ctr = c.config['MAIN']['RUDDER_SERVO_CTR']
    servo_max = c.config['MAIN']['RUDDER_SERVO_MAX']
=======
    servo_min = float(c.config['CONSTANTS']['rudder_servo_min'])
    servo_ctr = float(c.config['CONSTANTS']['rudder_servo_ctr'])
    servo_max = float(c.config['CONSTANTS']['rudder_servo_max'])
>>>>>>> 02b11201d0834258508f476e1a90bbc9e3bc91de
            
    angle_min = float(c.config['CONSTANTS']['rudder_angle_min'])
    angle_max = float(c.config['CONSTANTS']['rudder_angle_max'])
    angle_ctr = angle_min + (angle_max - angle_min) / 2
            
    def __init__(self, pca, channel_index):
        self.channel =  pca.channels[channel_index]

    def map(self, x, min1, max1, min2, max2):
        x = min(max(x, min1), max1)
        return min2 + (max2-min2)*((x-min1)/(max1-min1))

    def set(self, degrees):
        
        steps = 200/360 * degrees
        
        if degrees < self.current:
            step.turn(self, False,
                 steps, .0001, False, .05)
            
            val = self.map(degrees, self.angle_min, self.angle_ctr,
                  self.servo_min, self.servo_ctr)
        else:
            step.turn(self, True,
                 steps, .0001, False, .05)
            
            val = self.map(degrees, self.angle_ctr, self.angle_max,
                  self.servo_ctr, self.servo_max)
        
        
        
        self.current = degrees
        self.channel.duty_cycle = int(val)
        return
"""
class driver:

    def __init__(self, sail_channel = 0, rudder_channel = 1, sailAuto = True):
        """
        self.i2c = busio.I2C(board.SCL, board.SDA)
        self.pca = pcaLib.PCA9685(self.i2c)
        self.pca.frequency = 50

        self.sail = obj_sail(self.pca, sail_channel, sailAuto)
        """
        self.rudder = obj_rudder()
        print('n', sailAuto)

if __name__ == "__main__":
<<<<<<< HEAD
    drive = driver(0, 1)
=======
    #drive = driver(0, 1)
>>>>>>> 02b11201d0834258508f476e1a90bbc9e3bc91de
    #drive.sail.autoAdjust = False

    
    while True:
        string = input("  > Enter Input:")
        
        if string == "quit":
            break
        
        arr = string.split(" ")
        
        if arr[0] == "sail":
             # dont set this below 15 for now, the exact min/max seems
             # to be a little off and setting it to 0 is not good
            val = int(arr[1])
            #val = int(arr[1]) if int(arr[1]) >= 15 else 15
            
            #drive.sail.set(val)
            
        elif arr[0] == "rudder":
              drive.rudder.set(int(arr[1]))
              
        elif arr[0] == "stepper":
            stepper = stepperMotor()
            stepper.step(int(arr[1]))
