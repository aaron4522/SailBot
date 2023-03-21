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
    
    #true center camera position
    def center(self):
        print("TODO")

    #go far left,right,center looking for buoy whole time detect() - 3 set points in x axis
    def scanTHIRDS(self):
        #move to closest point in the trio, move to next (left has priority if it exists)
        #detect() at each set camera position (x axis wise)

        #speculation:
        #find y axis base for each based on gyroscope - calc on basis before going to point and at point (% variation consideration)
        #might not need dynamic y axis if stand is made well (just a thought)
        print("TODO")

    #tracking camera postion to center on object (possibly move rudder)
    def track(self):
        print("TODO")

    #look for buoy in capture taken
    def detect(self):
        print("TODO")
        #aaron AI goku based code with capture()

    #calculate gps coords of object based on distance formula and angle
    def coordcalc(self):
        print("TODO")
        #rework events to work on ever updating gps coords rather then fantom radius area?
        #how would you differenciate them from eachother?
    
    #backburner: free control movement wise with continuous capture feed for demonstration purposes
    def freemove(self):
        print("TODO")

    #============================================================================================================================
    def testloop(self):
        print('''
=============================
Accepted Command info:
[0] freemove(): free control movement wise with continuous capture feed for demonstration purposes
[1] center():   true center camera position
[2] scanTHIRDS(): go far left,right,center looking for buoy whole time detect() - 3 set points in x axis
[3] detect(): look for buoy in capture taken
-----------------------------''')
        inp = input("Command Test: ")
        
        if inp == "0":
            self.freemove()
        if inp == "1":
            self.center()
        if inp == "2":
            self.scanTHIRDS()
        if inp == "3":
            self.detect()
        else:
            print("nah...")
            raise Exception("invalid command selection")

#============================================================================================================================

if __name__ == "__main__":
    cam = Camera()
    cam.testloop()