"""
Handles interfacing with the I2C compass and accelerometer sensor
"""

#sudo pip3 install adafruit-circuitpython-lis2mdl


from time import sleep
import board
import busio
import adafruit_lis2mdl
import adafruit_lsm303_accel
import adafruit_lsm303dlh_mag
import math
#^^from Thread import thread
#import RPi.GPIO as GPIO


class compass:
    def __init__(self):
        # Setup I2C connections
        i2c = busio.I2C(board.SCL, board.SDA)
        self.mag = adafruit_lsm303dlh_mag.LSM303DLH_Mag(i2c)
        self.accel = adafruit_lsm303_accel.LSM303_Accel(i2c)
        self.compassAngle=0
        self.errcnt=0
        
        self.averagedAngle = 0

    def run(self):
        pass

    @property
    def vector(self):
        return sensor.magnetic # (mag_x, mag_y, mag_z)

    @property
    def angle_X(self):
        # return X component of compass, occasionally the compass fails to read, if this happens 10 times in a row raise error
        try:
            self.compassAngle1 = self.mag.magnetic[0]   
            self.errcnt=0
        except:
            self.errcnt+=1
            if self.errcnt>10:
                raise Exception("DISCONNECTED COMPASS")
        
        return self.compassAngle1
    @property
    def angle_Y(self):
        # return Y component of compass, occasionally the compass fails to read, if this happens 10 times in a row raise error
        try:
            self.compassAngle2 = self.mag.magnetic[1]    #issues
            self.errcnt=0
        except:
            self.errcnt+=1
            #print("haha" )#,compassAngle, angle)
            if self.errcnt>10:
                raise Exception("DISCONNECTED COMPASS")
        
        return self.compassAngle2
    @property
    def angle_Z(self):
        # return Z component of compass, occasionally the compass fails to read, if this happens 10 times in a row raise error
        try:
            self.compassAngle3 = self.mag.magnetic[2]    #issues
            self.errcnt=0
        except:
            self.errcnt+=1
            #print("haha" )#,compassAngle, angle)
            if self.errcnt>10:
                raise Exception("DISCONNECTED COMPASS")
        
        return self.compassAngle3
    
    @property
    def angleToNorth(self):
        return (math.atan2(-self.angle_Y, -self.angle_X) * 180 / math.pi)
    
    @property
    def angle(self):
        # returns smoothed angle measurement
        alpha = .9
        self.averagedAngle = self.averagedAngle * alpha + self.angleToNorth * (1-alpha)
        return self.averagedAngle
    
    def printAccel(self):
        print("Acceleration (m/s^2)): X=%0.3f Y=%0.3f Z=%0.3f"%self.accel.acceleration)
    def printMag(self):
        print("Magnetometer (micro-Teslas)): X=%0.3f Y=%0.3f Z=%0.3f"%self.mag.magnetic)
        print(F"Angle {self.angle}")
        #print(F"angle to north: {self.angleToNorth}")
            
if __name__ == "__main__":
    comp = compass()
    while True:
        comp.printMag()
        sleep(.2)
        

    


