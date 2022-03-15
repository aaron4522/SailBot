#sudo pip3 install adafruit-circuitpython-lis2mdl


from time import sleep
import board
import busio
import adafruit_lis2mdl
import adafruit_lsm303_accel
import adafruit_lsm303dlh_mag
#^^from Thread import thread
#import RPi.GPIO as GPIO


class compass:
        #included "compass" to fix syntax with pi
    def __init__(self):
        i2c = busio.I2C(board.SCL, board.SDA)
        self.mag = adafruit_lsm303dlh_mag.LSM303DLH_Mag(i2c)
        self.accel = adafruit_lsm303_accel.LSM303_Accel(i2c)

    def run(self):
        pass

    @property
    def vector(self):
        return sensor.magnetic # (mag_x, mag_y, mag_z)
    
    def printAccel(self):
        print("Acceleration (m/s^2)): X=%0.3f Y=%0.3f Z=%0.3f"%self.accel.acceleration)
    def printMag(self):
        print("Magnetometer (micro-Teslas)): X=%0.3f Y=%0.3f Z=%0.3f"%self.mag.magnetic)        
            
if __name__ == "__main__":
    comp = compass()
    while True:
        comp.printMag()
        sleep(1)
        

    


