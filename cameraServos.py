"""
Drivers and interface for camera servos
"""
# Code adapted from https://github.com/ArduCAM/PCA9685
import logging

import constants as c
try:
    import adafruit_servokit
except ImportError as e:
    print("Failed to import some modules, if this is not a simulation fix this before continuing")
    print(f"Exception raised: {e}")
   


# Yaw and Pitch assumed to have same range limits
MAX_ANGLE = 180
MIN_ANGLE = 0

DEFAULT_ANGLE = 90

# Servo connection ports, if inputs are reversed then switch
# If servos don't move try setting ports to 2 and 3
PITCH_PORT = 0
YAW_PORT = 1


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
        self.pitch: property
        self.yaw: property
        
        logging.info("Initializing camera servos")
        self.reset()
        
    def reset(self):
        """Return camera servos to center"""
        self.pitch = DEFAULT_ANGLE
        self.yaw = DEFAULT_ANGLE
    
    # ============ HERE BE DRAGONS ============
    # Python boilerplate for creating implicit setters and getters
    # Instead of writing 'servos.set_pitch(90)' just write 'servos.pitch = 90'
    def _get_pitch(self):
        self._kit.servo[PITCH_PORT].angle
        
    def _set_pitch(self, angle):
        if angle < MIN_ANGLE:
            self._kit.servo[PITCH_PORT].angle = MIN_ANGLE
        elif angle > MAX_ANGLE:
            self._kit.servo[PITCH_PORT].angle = MAX_ANGLE
        else:
            self._kit.servo[PITCH_PORT].angle = angle
            logging.debug("Moving camera pitch to {angle}")
    
    pitch = property(fget=_get_pitch, fset=_set_pitch)
    
    
    def _get_yaw(self):
        self._kit.servo[YAW_PORT].angle
        
    def _set_yaw(self, angle):
        if angle < MIN_ANGLE:
            self._kit.servo[YAW_PORT].angle = MIN_ANGLE
        elif angle > MAX_ANGLE:
            self._kit.servo[YAW_PORT].angle = MAX_ANGLE
        else:
            self._kit.servo[YAW_PORT].angle = angle
            logging.debug("Moving camera yaw to {angle}")
    
    yaw = property(fget=_get_yaw, fset=_set_yaw)
        
    
if __name__ == "__main__":
    servos = CameraServos()
    
    while True:
        servos.pitch = int(input("Enter pitch: "))
        servos.yaw = int(input("Enter yaw: "))