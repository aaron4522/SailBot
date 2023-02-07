from ultralytics import YOLO # Documentation: https://docs.ultralytics.com/cfg/
import cv2
import numpy as np
import torch

class Detection():
    def __init__(self, result: torch.tensor):
        self.bbox: torch.tensor = result.boxes
        self.xywh: np.array = self.bbox.xywh.numpy()[0] # TODO: keep as nparray or x, y, w, h vars?
        self.conf: float = self.bbox.conf.numpy()[0], 3
        self.class_id: str = BoatVision.classes[int(self.bbox.cls.numpy()[0])]
    
    def __str__(self):
        return f"{self.class_id} ({self.conf}) at ({self.xywh[0]},{self.xywh[1]})\n"
    
class Frame():
    '''list[Detections] with frame metadata'''
    def __init__(self, results):
        self.time = 0 # time of capture taken
        self.angle = 0 # angle of camera
        self.gps = 0 # gps pos of boat at capture
        self.detections = []

        results = results[0] # meta -> list[tensor]
        # TODO: test results.cpu() or results.to("cpu") for performance on Pi
        
        for result in results:
            self.detections.append(Detection(result))

class BoatVision():
    '''AI object detection model'''
    classes = ["buoy", "boat"]
    def __init__(self, source=0):
        # Settings TODO: migrate to settings file
        self.weights = "CV/buoy_weights.pt"
        self.confidence = 0.4
        self.source = source
        self.cap = cv2.VideoCapture(source)
        self.img_size = 640

        # Initialize model
        self.model = YOLO(self.weights)
        # TODO: test performance after export to .onnx
            #model.export(format="onnx")
            # or cmd -> yolo task=detect mode=export model=<PATH> format = onnx

    def cam_detect(self) -> Frame:
        '''Detects buoys from camera source specified in settings'''
        
        cap = cv2.VideoCapture(self.source)
        while cap.isOpened():
            start = time()
            
            ret, frame = cap.read()
            if not ret:
                print("Camera feed stopped. Exiting ...")
                break
            # frame = cv2.resize(frame, (img_size, img_size))
            
            result = self.model.predict(source=frame, conf=self.confidence, save=False, line_thickness=1)
            
            Frame(result)
            
            end = time()
            fps = 1/np.round(end - start, 2)
            cv2.putText(frame, f'FPS: {int(fps)}', (0,0), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0,255,0), 2)
            
            cv2.imshow('YOLOv8 Detection', frame)
            
            if cv2.waitKey(5) == ord('q'):
                break
            
        cap.release()
        cv2.destroyAllWindows()
    
    def img_detect(self, imgs: str) -> Frame:
        '''Detects buoys from specified image path(s)'''
        result = self.model.predict(source=imgs, show=True, conf=self.confidence, save=False, line_thickness=1)
        
        Frame(result)

if __name__ == "__main__":
    import sys
    from time import time
    
    Detect = BoatVision()
    try: 
        mode = sys.argv[1]
    except (IndexError):
        mode = "cam" # default
    
    
    if mode == "cam":
        start = time()
        Detect.cam_detect()
        end = time()
    elif mode == "img":
        import tkinter
        from tkinter.filedialog import askopenfilenames
        
        tkinter.Tk().withdraw()
        imgs = askopenfilenames()
        
        for img in imgs:
            Detect.img_detect(img)
            input()
    else:
        quit("No mode selected!")
        
    
       
    