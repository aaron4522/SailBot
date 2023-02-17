"""
Interface for detecting buoys
"""
from ultralytics import YOLO # Documentation: https://docs.ultralytics.com/cfg/
import cv2
import numpy as np
import torch
from time import time

import constants as c
try:
    from camera import Camera, Frame
    from GPS import gps
except: ImportError()

class Detection():
    """Bounding box and confidence for a detected object"""
    def __init__(self, result: torch.tensor):
        _bbox: torch.tensor = result.boxes
        _xywh: np.array = self._bbox.xywh.numpy()[0]
        
        self.x = _xywh[0]
        self.y = _xywh[1]
        self.w = _xywh[2]
        self.h = _xywh[3]
        self.conf = _bbox.conf.numpy()[0]
        #self.class_id: str = ObjectDetection.classes[int(_bbox.cls.numpy()[0])]
    
    def __str__(self):
        return f"Buoy ({self.conf}): at ({self.x},{self.y})\n"


class ObjectDetection():
    """Contains AI object detection model"""
    def __init__(self):
        self.model = YOLO(c.config["OBJECTDETECTION"]["weights"])  # Initialize model
            # TODO: test performance after export to .onnx
            #model.export(format="onnx") or cmd -> yolo task=detect mode=export model=<PATH> format = onnx
    
    def analyze(self, frame: Frame) -> Frame:
        """Detects buoys from a Camera.Frame object
        Args:
            frame (Camera.Frame): the Frame object to perform analysis on.   
        """
        if frame.img is None:
            raise ValueError("Attempting to analyze Frame with no image. Did you specify save=True with Camera.capture()?")
        # TODO: test results.cpu() or results.to("cpu") for performance on Pi
        result = self.model.predict(source=frame.img, conf=float(c.config["OBJECTDETECTION"]["conf_thresh"]), save=False, line_thickness=1)
        result = result[0] # metadata -> list[tensor]
        
        for detection in result:
            frame.detections.append(Detection(detection))
            
        return frame
    
            
class ObjectDetectionTester(ObjectDetection):
    """Debug class to test ObjectDetection functions for model verification and functionality"""
    def __init__(self):
        super().__init__()
        
    def cam_detect(self):
        """Detects buoys from camera source specified in settings"""
        cam = Camera()
        while True:
            start = time()
            
            frame: Frame = cam.capture(save=True, context=False)
            frame = self.analyze(frame)
            
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
        self.model.predict(source=img, show=True, conf=self.conf_thresh, save=False, line_thickness=1)
        

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
        quit()
    else:
        quit("No mode selected!")
        