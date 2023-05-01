import cv2
import numpy as np
from time import time
import sys
import tkinter
from tkinter.filedialog import askopenfilenames
import keyboard

import constants as c
from camera import Camera
from objectDetection import ObjectDetection


# Basic model function can be tested by running `yolo predict model=CV/buoy_weights.pt source=0`
object_detection = ObjectDetection()

def test_cam_detect():
    """Detects buoys from camera source specified in settings""" 
    # TODO: Doesn't show detections on frame
    cam = Camera()
    while True:
        start = time()
        
        frame = cam.capture(context=False, detect=True)
        
        for detection in frame.detections:
            x,y,w,h = detection.x, detection.y, detection.w, detection.h
            cv2.rectangle(frame.img,(x-.5*w,y-.5*h),(x+.5*w,y+.5*h),(0,255,0),2)
            cv2.putText(frame.img,f'Buoy ({detection.conf})',(x+.5*w+10,y+.5*h),0,0.3,(0,255,0))
            
        end = time()
        fps = 1/np.round(end - start, 2)
        cv2.putText(frame.img, f'FPS: {fps}', (20,50), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0,255,255), 2)
        
        cv2.imshow('YOLOv8 Detection', frame.img)
        
        if cv2.waitKey(5) == ord('q'):
            break
        
def test_img_detect(img: str):
    """Detects buoys from specified image path(s)
    Args:
        img (str): file path of selected image
    """
    object_detection.model.predict(source=img, 
                                   show=True, 
                                   conf=float(c.config["OBJECTDETECTION"]["conf_thresh"]), 
                                   save=False, 
                                   line_thickness=1)
        

if __name__ == "__main__":
    try: 
        mode = sys.argv[1]
    except (IndexError):
        mode = input("Specifiy test mode (cam/img): ")
    
    if mode == "cam":
        test_cam_detect()
    elif mode == "img":
        tkinter.Tk().withdraw()
        imgs = askopenfilenames()
        
        for img in imgs:
            test_img_detect(img)
            keyboard.wait('enter')
            cv2.destroyAllWindows()
    else:
        quit("No mode selected!")
