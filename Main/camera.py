"""
Interface for camera
"""
import cv2
from time import time

import constants as c
try:
    from GPS import gps
except ImportError:
    print("Could not import GPS")
    
# TODO: write drivers for camera servo and image capture

class Frame():
    """Image with context metadata"""
    def __init__(self, img=None, time=None, cords=None):
        self.img = img
        self.time = time
        self.cords = cords
        self.pitch = Camera.pitch
        self.yaw = Camera.yaw
        self.detections = []
            
    def __str__(self):
        print(f": ")
        
class Camera():
    """Drivers and interface for camera"""
    def __init__(self):
        self.pitch = 0 # TODO: set to curr servo angle
        self.yaw = 0 # TODO: set to curr servo angle
        self.cap = cv2.VideoCapture(int(c.config["CAMERA"]["source"]))
        
    def __del__(self):
        self.cap.release()
        cv2.destroyAllWindows()
        
    def capture(self, save=True, context=True, show=False) -> Frame:
        """Takes a single picture from camera
        Args:
            context (bool): whether to include time, gps, and camera angle in return Frame
            save (bool): whether to include the image in return Frame
            show (bool): whether to show the image that is captured
        """
        ret, img = self.cap.read()
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
        
    @property
    def pitch(self):
        return self._pitch
    @pitch.setter
    def pitch(self, angle: int):
        if (angle < -90 or angle > 90):
            raise ValueError(f"Impossible angle: {angle} for pitch")
        self._pitch = angle
        
    @property
    def yaw(self):
        return self.yaw
    @yaw.setter
    def yaw(self, angle: int):
        if (angle < -90 or angle > 90):
            raise ValueError(f"Impossible angle: {angle} for yaw")
        self._yaw = angle
    

if __name__ == "__main__":
    cam = Camera()