"""
Interface for camera
"""
import cv2
from time import time
import logging

import constants as c
try:
    from GPS import gps
except ImportError:
    print("Could not import GPS")
    
# TODO: 
# Write drivers for camera servo and image capture
# Stabilize for wave disruption by centering horizon?
# Target lock: Alter pitch & yaw to keep target in focus
MAX_PITCH: int = 90
MAX_YAW: int = 90

class Frame():
    """Image with context metadata"""
    def __init__(self, img=None, time=None, cords=None):
        self.img = img
        self.time = time
        self.cords = cords
        self.pitch = Camera.pitch
        self.yaw = Camera.yaw
        self.detections = [] # empty until objectDetection.analyze()
        
class Camera():
    """Drivers and interface for camera"""
    def __init__(self):
        self.pitch = 0 # TODO: set to curr servo angle
        self.yaw = 0 # TODO: set to curr servo angle
        self._cap = cv2.VideoCapture(int(c.config["CAMERA"]["source"]))
        
    @property
    def pitch(self):
        return self._pitch
    @pitch.setter
    def pitch(self, angle: int):
        if (angle < -MAX_PITCH or angle > MAX_PITCH):
            raise ValueError(f"Impossible angle: {angle} for pitch")
        # MOVE CAMERA
        logging.debug("Moving camera pitch to {angle}")
        self._pitch = angle
        
    @property
    def yaw(self):
        return self.yaw
    @yaw.setter
    def yaw(self, angle: int):
        if (angle < -MAX_YAW or angle > MAX_YAW):
            raise ValueError(f"Impossible angle: {angle} for yaw")
        # MOVE CAMERA
        logging.debug("Moving camera yaw to {angle}")
        self._yaw = angle
        
    def __del__(self):
        self._cap.release()
        cv2.destroyAllWindows()
        
    def capture(self, save=True, context=True, show=False) -> Frame:
        """Takes a single picture from camera
        Args:
            context (bool): whether to include time, gps, and camera angle in return Frame
            save (bool): whether to include the image in return Frame
            show (bool): whether to show the image that is captured
        """
        ret, img = self._cap.read()
        if not ret:
            raise RuntimeError("No camera feed detected")
        
        if show:
            cv2.imshow(img)
        
        if context:
            time = time()
            #gps.updategps() TODO: GPS missing imports
            #cords = (gps.latitude, gps.longitude)
            cords = None # TEMP
            if save:
                return Frame(img=img, time=time, cords=cords)
            else:
                return Frame(time=time, cords=cords)            
        elif save:
            return Frame(img=img)
        else:
            return Frame()
        
    def survey(self, num_images=3) -> list[Frame]:
        """Takes a series of x pictures over 270 degrees of vision
        Args:
            num_images (int): how many images to take across FoV
        """
        images: list[Frame] = []
        step = (MAX_YAW * 2) / num_images
        
        if self.yaw < 0: # survey left -> right
            for self.yaw in range(-MAX_YAW, MAX_YAW, step):
                images.append(self.capture())
        if self.yaw > 0: # survey right -> left
            for self.yaw in range(MAX_YAW, -MAX_YAW, -step):
                images.append(self.capture())
        
        return images
    

if __name__ == "__main__":
    cam = Camera()