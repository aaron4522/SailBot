"""
Drivers and interface for camera servos
"""
# Code adapted from https://github.com/ArduCAM/PCA9685
import logging

import constants as c
import adafruit_servokit
   
# Yaw and Pitch assumed to have same range limits
MIN_ANGLE = int(c.config["CAMERASERVOS"]["min_angle"])
MAX_ANGLE = int(c.config["CAMERASERVOS"]["max_angle"])

DEFAULT_ANGLE = int(c.config["CAMERASERVOS"]["default_angle"])

# Servo connection ports, if inputs are reversed then switch
# If servos don't move try setting ports to 2 and 3
PITCH_PORT = int(c.config["CAMERASERVOS"]["pitch_port"])
YAW_PORT = int(c.config["CAMERASERVOS"]["yaw_port"])


class CameraServos():
    """
    Drivers and interface for camera servos
    
    Attributes:
        - pitch: camera pitch
        - yaw: camera yaw
        
    Functions:
        - reset(): returns camera servos to center
    """
    _instance = None
    def __new__(cls, *args, **kwargs):
        """Prevent duplicate classes from being created"""
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance
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
    
if __name__ == "__main__":
    servos = CameraServos()
    
    while True:
        servos.pitch = int(input("Enter pitch: "))
        servos.yaw = int(input("Enter yaw: "))
        
        print(servos.pitch)
        print(servos.yaw)
