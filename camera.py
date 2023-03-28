"""
Interface for camera
"""
import cv2
from time import time
import math

import constants as c
try:
    from GPS import gps
    from compass import compass
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
        #pitch: +up/-down; yaw: +left/-right
        self.pitch = 0 # TODO: set to curr servo angle
        self.yaw = 0 # TODO: set to curr servo angle
        self.cap = cv2.VideoCapture(int(c.config["CAMERA"]["source"]))
        self.obj_info = [0,0,0,0] #x,y,width,height
        
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

    #---------------------------------- 
    @property
    def pitch(self):
        return self._pitch
    #NOTE: PRIORITY[{!!!!!!!!!!!!!!!!!!!!}]
    @pitch.setter
    def pitch(self, angle: int):
        if (angle < -90 or angle > 90):
            #NOTE: print warning and just go to +-90 instead?
            raise ValueError(f"Impossible angle: {angle} for pitch")
        #NOTE: integrated code here
        self._pitch = angle

    #----------------------------------    
    @property
    def yaw(self):
        return self.yaw
    #NOTE: PRIORITY[{!!!!!!!!!!!!!!!!!!!!}]
    @yaw.setter
    def yaw(self, angle: int):
        if (angle < -90 or angle > 90):
            #NOTE: print warning and just go to +-90 instead?
            raise ValueError(f"Impossible angle: {angle} for yaw")
        #NOTE: integrated code here
        self._yaw = angle

    #----------------------------------
    #go far left,right,center looking for buoy whole time detect() - 3 set points in x axis
    def scanTHIRDS(self):
        #move to closest point in the trio, move to next (left has priority if it exists)
        #detect() at each set camera position (x axis wise)
        #speculation:
        #find y axis base for each based on gyroscope - calc on basis before going to point and at point (% variation consideration)
        #might not need dynamic y axis if stand is made well (just a thought)

        #NOTE: could be more dynamic between 90 and 45 but ehhhh
        if self.detect(): return
        #----
        sign = 1    #less if statements
        if self.yaw < 0: sign = -1  #right side
        #----
        self.pitch(sign*45)
        if self.detect(): return
        self.pitch(sign*90)
        if self.detect(): return
        self.pitch(sign*45)
        if self.detect(): return
        #----
        self.pitch(0)
        if self.detect(): return
        #----
        self.pitch(-1*sign*45)
        if self.detect(): return
        self.pitch(-1*sign*90)
        if self.detect(): return
        self.pitch(-1*sign*45)
        if self.detect(): return

    #----------------------------------
    #NOTE: NOT PRIORITY
    #tracking camera postion to center on object (possibly move rudder)
    #would detect be too computation heavy?
    def track(self):
        print("TODO")

    #----------------------------------
    #NOTE: PRIORITY[{!!!!!!!!!!!!!!!!!!!!}]
    #look for buoy in capture taken
    #aaron AI goku based code with capture()
    #verbose for showing a picture of it on the capture, save as seperate self.__variable__ (demonstration purposes)
    def detect(self, verbose=False):
        print("TODO")
        #set pixel width of object in self.obj_info object
        #set other variables, [{!!!}]return if detected object[{!!!}]
        return False

    #----------------------------------
    #NOTE: PRIORITY[{!!!!!!!!!!!!!!!!!!!!}]
    #calculate gps coords of object based on distance formula and angle
    #speculation:
    #rework events to work on ever updating gps coords rather then fantom radius area?
    #how would you differenciate them from eachother?
    def coordcalc(self):
        if c.config["OBJECTDETECTION"]["Width_Real"] == 0 or c.config["OBJECTDETECTION"]["Focal_Length"] == 0:
            raise Exception("MISSING WIDTH REAL/FOCAL LENGTH INFO IN CONSTANTS")
        dist = (c.config["OBJECTDETECTION"]["Width_Real"]*c.config["OBJECTDETECTION"]["Focal_Length"])/self.obj_info[2]
        comp = compass()    #assume 0 is north(y pos)
        geep = gps(); geep.updategps()

        t = math.pi/180
        return dist*math.cos(comp.angle*t)+geep.latitude, dist*math.sin(comp.angle*t)+geep.longitude

    #----------------------------------
    #NOTE: DEMONSTRATION PURPOSE
    #for lamda demonstration purposes
    def center(self):
        self.pitch(0)
        self.yaw(0)
    
    #----------------------------------
    #NOTE: DEMONSTRATION PURPOSE
    #backburner: free control movement wise with continuous capture feed for demonstration purposes
    def freemove(self):
        while True:
            keyboard.on_press_key("enter", lambda _: self.detect(True))
            keyboard.on_press_key("space", lambda _: self.center())

            keyboard.on_press_key("up arrow", lambda _: self.yaw(self.yaw+1))
            keyboard.on_press_key("down arrow", lambda _: self.yaw(self.yaw-1))
            keyboard.on_press_key("left arrow", lambda _: self.pitch(self.pitch+1))
            keyboard.on_press_key("right arrow", lambda _: self.pitch(self.pitch-1))

            cv2.imshow('capture', self.cap)
            if cv2.waitKey(1) & 0xFF == ord('q'): break

    #============================================================================================================================
    #NOTE: DEMONSTRATION PURPOSE
    def testloop(self):
        print('''
=============================
Accepted Command info:
[0] freemove(): free control movement wise with continuous capture feed for demonstration purposes
[1] scanTHIRDS(): go far left,right,center looking for buoy whole time detect() - 3 set points in x axis
[2] track(): follow object
-----------------------------''')
        inp = input("Command Test: ")
        
        if inp == "0":
            self.freemove()
        if inp == "1":
            self.scanTHIRDS()
        else:
            print("nah...")
            raise Exception("invalid command selection")

#============================================================================================================================

if __name__ == "__main__":
    import keyboard #might be annoying to auto-bug checkers
    cam = Camera()
    while True: cam.testloop()