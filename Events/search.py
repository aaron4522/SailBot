import logging
import math
import time

from eventUtils import Event, EventFinished
from camera import Camera, Frame
from objectDetection import ObjectDetection, Detection

"""
# Challenge	Goal:
    - To demonstrate the boat’s ability to autonomously locate an object
    
    # Description:
        - An orange buoy will be placed somewhere within 100 m of a reference position
        - The boat must locate, touch, and signal* such within 10 minutes of entering the search area
        - RC is not allowed after entering the search area
        - 'Signal' means white strobe on boat and/or signal to a shore station and either turn into wind or assume station-keeping mode
    
    # Scoring:
        - 15 pts max
        - 12 pts for touching (w/o signal)
        - 9 pts for passing within 1m
        - 6 pts for performing a search pattern (creeping line, expanding square, direct tracking to buoy, etc)
    
    # Assumptions: (based on guidelines)
        - 
        
    # Strategy:
        - Define search path as series of GPS lines to cover the most ground in shortest time
        - If x% match verify:
            - Check if estimated position is outside of given bounds + buffer
        - Then deviate from course and go to position
            - If target confidence increases -> target lock & goto
            - if target confidence decreases -> 
"""

REQUIRED_ARGS = 2

class Search(Event):
    """
    Attributes:
        - event_info (array) - center and radius of search circle
            event_info = [(center_long, center_lat), radius]
    """
    
    def __init__(self, event_info):
        if (len(event_info) != REQUIRED_ARGS):
            raise TypeError(f"Expected {REQUIRED_ARGS} arguments, got {len(event_info)}")
        
        super().__init__(event_info)
        logging.info("Search moment")
        self.object_detection = ObjectDetection()
        self.camera = Camera()


        #make in boatMain along with mode switch, attach buoy coords and radius in ary
        #will need to redo GUI then ://////
        self.arr = self.SR_pattern()
    
    def next_gps(self):
        """The next GPS point that the boat should go to"""
        return 0,0
    
    def loop(self):
        """Event logic that will be executed continuously"""
        
        imgs: list[Frame] = self.camera.survey(3) # (3, analyze=True?)
        for i, img in enumerate(i, imgs):
            self.object_detection.analyze(img)
        imgs.sort(descending=True) # sort by confidence
        # Datapoints:
            # GPS pos of boat
            # GPS pos of detections
            # Confidence of detections
        # Abstract:
            # Create a heatmap of buoys which persists across surveys
                # (lat, long, confidence) 
    
    def create_search_pattern(self):
        """
        Generates a 5-point zig-zag search pattern to maximimize area coverage 
        
        Returns:
            - 5 gps coordinates stored as an array of tuples [(pt1_long, pt1_lat), ...]
        """
        
        # Metrics used to fine-tune optimal coverage
        # TODO: test different values
        # Camera cone of vision from 
        BOAT_FOV = 242
        # Furthest distance object detection can reliably spot a buoy (m)
        MAX_DETECTION_DISTANCE = 40
        
        pattern = []
        
        self.gps_class.updategps()
        gps_lat = self.gps_class.latitude
        gps_long = self.gps_class.longitude

        a = gps_lat - self.event_info[0][0]
        b = gps_long - self.event_info[0][1]
        ang = math.atan(b/a)
        ang *= 180/math.pi

        if(a<0): ang += 180

        tar_angs = [ang,ang+72,ang-72,ang-(72*3),ang-(72*2)]
        tarx = [0]*5
        tary = [0]*5

        for i in range(0,5):
            tarx[i] =  self.event_arr[0]  + self.event_arr[2]*math.cos( tar_angs[i] * (math.pi/180) )
            tary[i] =  self.event_arr[1] + self.event_arr[2]*math.sin( tar_angs[i] * (math.pi/180) )
        
        return tarx,tary
    