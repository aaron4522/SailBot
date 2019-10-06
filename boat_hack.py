import board
import busio
import adafruit_pca9685 as pcaLib
import constants as c

def map(x, min1, max1, min2, max2):
    x = min(max(x, min1), max1)
    return min2 + (max2-min2)*((x-min1)/(max1-min1))
            
class obj_sail:
            
    servo_min = c.SAIL_SERVO_MIN
    servo_max = c.SAIL_SERVO_MAX
            
    angle_min = c.SAIL_ANGLE_MIN
    angle_max = c.SAIL_ANGLE_MAX
            
    def __init__(self, channel_index):
        self.channel =  pca.channels[channel_index]

    def set(self, degrees):
        val = map(degrees, self.angle_min, self.angle_max,
                  self.servo_min, self.servo_max)

        self.channel.duty_cycle = int(val)
        return
            
class obj_rudder:
            
    servo_min = c.RUDDER_SERVO_MIN
    servo_ctr = c.RUDDER_SERVO_CTR
    servo_max = c.RUDDER_SERVO_MAX
            
    angle_min = c.RUDDER_ANGLE_MIN
    angle_max = c.RUDDER_ANGLE_MAX
    angle_ctr = angle_min + (angle_max - angle_min) / 2
            
    def __init__(self, channel_index):
        self.channel =  pca.channels[channel_index]

    def set(self, degrees):
        if degrees < self.angle_ctr:
            
            val = map(degrees, self.angle_min, self.angle_ctr,
                  self.servo_min, self.servo_ctr)
        else:
            val = map(degrees, self.angle_ctr, self.angle_max,
                  self.servo_ctr, self.servo_max)


        self.channel.duty_cycle = int(val)
        return

if __name__ == "__main__":

    i2c = busio.I2C(board.SCL, board.SDA)
    pca = pcaLib.PCA9685(i2c)
    pca.frequency = 50

    mSail = obj_sail(0)
    mRudder = obj_rudder(1)
    
    while True:
        string = input("  > Enter Input:")
        
        if string == "quit":
            break
        
        arr = string.split(" ")
        
        if arr[0] == "sail":
             # dont set this below 15 for now, the exact min/max seems
             # to be a little off and setting it to 0 is not good
            val = int(arr[1]) if int(arr[1]) >= 15 else 15
            mSail.set(val)
            
        elif arr[0] == "rudder":
              mRudder.set(int(arr[1]))


                  