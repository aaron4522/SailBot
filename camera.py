"""
Interface for camera
"""
import cv2
from time import time
import logging
import math

import constants as c
try:
    from GPS import gps
    from compass import compass
except ImportError as e:
    print("Failed to import some modules, if this is not a simulation fix this before continuing")
    print(f"Exception raised: {e}")
    
try:
    from cameraServos import CameraServos
except ImportError as e:
    print("Failed to import some modules, if this is not a simulation fix this before continuing")
    print(f"Exception raised: {e}")
    
class Frame():
    """
    Image with context metadata
    
    Attributes:
        - img (np.ndarray): the RGB image taken
        - time: the UTC time at which the image was captured
        - gps: the position of the boat at time of capture
        - pitch: the camera's pitch angle at time of capture
        - yaw: the camera's yaw angle at time of capture
        - detections: a list of buoy Detections
            - initially empty! must call objectDetection.analyze(Frame.img) to populate
    """
    def __init__(self, img=None, time=None, gps=None, pitch=None, yaw=None):
        self.img = img
        self.time = time
        self.gps = gps
        self.pitch = pitch
        self.yaw = yaw
        self.detections = []
            
        
class Camera():
    """
    Drivers and interface for camera
    
    Attributes:
        - servos (CameraServo): interface to control camera servos
            - servos.pitch and servos.yaw will always have the immediate camera position
            - pitch and yaw can be modified to move the physical servos 
    
    Functions:
        - capture(): Takes a picture
        - survey(): Takes a panorama
    """
    def __init__(self):
        self._cap = cv2.VideoCapture(int(c.config["CAMERA"]["source"]))
        self.servos = CameraServos
        self.obj_info = [0,0,0,0] #x,y,width,height
        
    def capture(self, context=True, show=False) -> Frame:
        """Takes a single picture from camera
        Args:
            - context (bool): whether to include time, gps, and camera angle in return Frame
            - show (bool): whether to show the image that is captured
        Returns:
            - The captured image stored as a Frame object
        """
        
        img, time, cords, pitch, yaw = None, None, None, None, None
        
        ret, img = self._cap.read()
        if not ret:
            raise RuntimeError("No camera feed detected")
        
        if show:
            cv2.imshow(img)
            
        if context:
            time, gps, pitch, yaw = self.__get_context()
            return Frame(img=img, time=time, gps=gps, pitch=pitch, yaw=yaw)            
        else:
            return Frame(img=img)
        
    def survey(self, num_images=3, pitch=70, servo_range=180, context=True, show=False) -> list[Frame]:
        """Takes a horizontal panaroma over the camera's field of view
            - Maximum boat FoV is ~242.2 degrees (not tested)
        # Args:
            - num_images (int): how many images to take across FoV
                - Picamera2 lens covers an FoV of 62.2 degrees horizontal and 48.8 vertical
                
            - pitch (int): fixed camera pitch angle
                - must be between 0 and 180 degrees: 0 points straight down, 180 points straight up
                
            - servo_range (int): the allowed range of motion for camera servos, always centered
                - must be between 0 and 180 degrees: 0 means servo is fixed to center, 180 is full servo range of motion
                - ex. a range of 90 degrees limits servo movement to between 45-135 degrees for a total boat FoV of 152.2 degrees
                
            - context (bool): whether to include time, gps and camera angle of captured images
            
            - show (bool): whether to show each image as captured
            
        # Returns:
            - A list of the captured images stored as Frame objects
        """
        
        images: list[Frame] = []
        servo_step = servo_range / num_images
        
        # Move camera to desired pitch
        self.servos.pitch = pitch
        
        if self.yaw <= 90: 
            # Survey left -> right when camera is facing left or center
            for self.yaw in range(CameraServos.MIN_ANGLE, CameraServos.MAX_ANGLE, servo_step):
                images.append(self.capture(context=context, show=show))
        else:
            # Survey right -> left when camera is facing right
            for self.yaw in range(CameraServos.MAX_ANGLE, CameraServos.MIN_ANGLE, -servo_step):
                images.append(self.capture(context=context, show=show))
        
        return images

    # TODO:
    def track(self):
        """Centers camera on a detected buoy and attempts to keep it in frame"""
    
    def __get_context(self):
        """Helper method to get and format metadata for images"""
        time = time()
        gps.updategps() # TODO: replace with ROS subscriber
        gps = (gps.longitude, gps.latitude)
        pitch = self.servos.pitch
        yaw = self.servos.yaw
        
        return time, gps, pitch, yaw
    
    def __del__(self):
        self._cap.release()
        cv2.destroyAllWindows()
    
    
    
class CameraTester(Camera):
    def __init__(self):
        super.__init__()
        
    def freemove(self):
        while True:
            keyboard.on_press_key("enter", lambda _: self.detect(True))
            keyboard.on_press_key("space", lambda _: self.servos.reset())

            keyboard.on_press_key("up arrow", lambda _: self.yaw(self.yaw+1))
            keyboard.on_press_key("down arrow", lambda _: self.yaw(self.yaw-1))
            keyboard.on_press_key("left arrow", lambda _: self.pitch(self.pitch+1))
            keyboard.on_press_key("right arrow", lambda _: self.pitch(self.pitch-1))

            cv2.imshow('capture', self.cap)
            if cv2.waitKey(1) & 0xFF == ord('q'): break


if __name__ == "__main__":
    import keyboard #might be annoying to auto-bug checkers
    cam = CameraTester()
    while True:
        print('''
=============================
Accepted Command info:
[0] freemove(): free control movement wise with continuous capture feed for demonstration purposes
[1] survey(): go far left,right,center looking for buoy whole time detect() - 3 set points in x axis
[2] track(): follow object
-----------------------------''')
        inp = input("Command Test: ")
        
        if inp == "0":
            cam.freemove()
        if inp == "1":
            cam.survey()
        else:
            print("nah...")
            raise Exception("invalid command selection")