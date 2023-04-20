"""
Drivers and interface for camera servos
"""
# Code adapted from https://github.com/ArduCAM/PCA9685
import logging
from time import sleep
from math import abs

import constants as c
try:
    import adafruit_servokit
except ImportError as e:
    print("Failed to import some modules, if this is not a simulation fix this before continuing")
    print(f"Exception raised: {e}")
   
# Yaw and Pitch assumed to have same range limits
MIN_ANGLE = int(c.config(["CAMERASERVOS"]["min_angle"]))
MAX_ANGLE = int(c.config(["CAMERASERVOS"]["max_angle"]))

DEFAULT_ANGLE = int(c.config(["CAMERASERVOS"]["default_angle"]))

# Servo connection ports, if inputs are reversed then switch
# If servos don't move try setting ports to 2 and 3
PITCH_PORT = int(c.config(["CAMERASERVOS"]["pitch_port"]))
YAW_PORT = int(c.config(["CAMERASERVOS"]["yaw_port"]))


class CameraServos():
    """
    Drivers and interface for camera servos
    
    Attributes:
        - pitch: camera pitch
        - yaw: camera yaw
        
    Functions:
        - reset(): returns camera servos to center
    """
    
    def __init__(self):
        self._kit = adafruit_servokit.ServoKit(channels=16)
        self._pitch = DEFAULT_ANGLE
        self._yaw = DEFAULT_ANGLE
        
        logging.info("Initializing camera servos")
        self.reset()
        
    def reset(self):
        """Return camera servos to center"""
        self.pitch = DEFAULT_ANGLE
        self.yaw = DEFAULT_ANGLE
    
    # ============ HERE BE DRAGONS ============
    # Python boilerplate for creating implicit setters and getters
    # Instead of writing 'servos.set_pitch(90)' just write 'servos.pitch = 90'
    @property
    def pitch(self):
        return self._kit.servo[PITCH_PORT].angle
    
    @pitch.setter
    def pitch(self, angle):
        if angle < MIN_ANGLE:
            self._kit.servo[PITCH_PORT].angle = MIN_ANGLE
        elif angle > MAX_ANGLE:
            self._kit.servo[PITCH_PORT].angle = MAX_ANGLE
        else:
            logging.debug(f"Moving camera pitch to {angle}")
            self._kit.servo[PITCH_PORT].angle = angle
            
            while (abs(self.pitch - angle) < 0.1):
                sleep(0.1)
            logging.debug(f"Camera pitch set to {angle}")
            
    @property
    def yaw(self):
        return self._kit.servo[YAW_PORT].angle
    
    @yaw.setter
    def yaw(self, angle):
        if angle < MIN_ANGLE:
            self._kit.servo[YAW_PORT].angle = MIN_ANGLE
        elif angle > MAX_ANGLE:
            self._kit.servo[YAW_PORT].angle = MAX_ANGLE
        else:
            logging.debug(f"Moving camera yaw to {angle}") 
            self._kit.servo[YAW_PORT].angle = angle
            
            while (abs(self.yaw - angle) < 0.1):
                sleep(0.1)
            logging.debug(f"Camera yaw set to {angle}")
    
if __name__ == "__main__":
    servos = CameraServos()
    
    while True:
        servos.pitch = int(input("Enter pitch: "))
        servos.yaw = int(input("Enter yaw: "))
        
        print(servos.pitch)
        print(servos.yaw)
