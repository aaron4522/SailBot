"""
Interface for detecting buoys
"""
from ultralytics import YOLO # Documentation: https://docs.ultralytics.com/cfg/
#from supervision.tools.detections
import cv2
import numpy as np
import torch
from time import time
import logging
from dataclasses import dataclass

import constants as c
from camera import Camera, Frame
#from GPS import gps # TODO: ROS subscriber

@dataclass(order=True)
class Detection:
    """
    Object containing the confidence level, bounding box, and location of a buoy from a given image
    Attributes:
        - x (int): - x coordinate for bottom left corner of bounding box
        - y (int): - y coordinate for bottom left corner of bounding box
        - w (int): - width (in pixels) of bounding box rectangle
        - h (int): - height (in pixels) of bounding box rectangle
        - conf (float): - confidence level that detected object is a buoy [0-1]
    """
    
    def __init__(self, result: torch.tensor):
        _bbox: torch.tensor = result.boxes
        _xywh: np.array = _bbox.xywh.numpy()[0]
        
        self.x = _xywh[0]
        self.y = _xywh[1]
        self.w = _xywh[2]
        self.h = _xywh[3]
        self.conf = _bbox.conf.numpy()[0]
        #self.class_id: str = ObjectDetection.classes[int(_bbox.cls.numpy()[0])]
        #self.pos = None
        sort_index: int = self.conf
        

class ObjectDetection():
    """
    AI object detection model
    
    Functions: 
        - analyze() - checks image for buoys
    """
    
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        """Prevent duplicate classes from being created"""
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance
    
    def __init__(self):
        self.model = YOLO(c.config["OBJECTDETECTION"]["weights"])  # Initialize model for analysis
            # TODO: test performance after export to .onnx
            #model.export(format="onnx") or cmd -> yolo task=detect mode=export model=<PATH> format = onnx
    
    def analyze(self, image) -> list[Detection]:
        """Detects buoys within a given image. Can be supplied from cv2 or using the Camera.capture()/Camera.survey() methods.
        Args:
            - image (np.ndarray, .jpg, .png): The RGB image to search for buoys
        Returns:
            - A list buoys found (if any) stored as a list of Detection objects
        """
        # TODO: test results.cpu() or results.to("cpu") for performance on Pi
        result = self.model.predict(source=image, conf=float(c.config["OBJECTDETECTION"]["conf_thresh"]), save=False, line_thickness=1)
        result = result[0] # metadata -> list[tensor]
        
        # Add each buoy found by the model into a list
        detections: list[Detection] = []
        for detection in result:
            logging.info("Buoy ({detection.conf}): at ({detection.x},{detection.y})\n")
            detections.append(Detection(detection)) # Convert tensors into readable Detection class and append to list
        return detections
            
class ObjectDetectionTester(ObjectDetection):
    """Debug class to test ObjectDetection functionality"""
    # Basic model function can be tested by running `yolo predict model=CV/buoy_weights.pt source=0`
    def __init__(self):
        super().__init__()
        
    def cam_detect(self):
        """Detects buoys from camera source specified in settings""" 
        # TODO: Doesn't show detections on frame
        cam = Camera()
        while True:
            start = time()
            
            frame: Frame = cam.capture(context=False)
            Frame.detections = self.analyze(frame.img)
            
            end = time()
            fps = 1/np.round(end - start, 2)
            cv2.putText(frame.img, f'FPS: {int(fps)}', (20,50), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0,255,0), 2)
            
            cv2.imshow('YOLOv8 Detection', frame.img)
            
            if cv2.waitKey(5) == ord('q'):
                break
        
    
    def img_detect(self, img: str):
        """Detects buoys from specified image path(s)
        Args:
            img (str): file path of selected image
        """
        self.model.predict(source=img, show=True, conf=float(c.config["OBJECTDETECTION"]["conf_thresh"]), save=False, line_thickness=1)
        

if __name__ == "__main__":
    import sys
    
    object_det_tester = ObjectDetectionTester()
    try: 
        mode = sys.argv[1]
    except (IndexError):
        mode = input("Specifiy test mode (cam/img): ")
    
    if mode == "cam":
        object_det_tester.cam_detect()
    elif mode == "img":
        import tkinter
        from tkinter.filedialog import askopenfilenames
        import keyboard
        
        tkinter.Tk().withdraw()
        imgs = askopenfilenames()
        
        for img in imgs:
            object_det_tester.img_detect(img)
            keyboard.wait('enter')
            cv2.destroyAllWindows()
    else:
        quit("No mode selected!")
