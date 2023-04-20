import logging
import math
import time

from eventUtils import Event, EventFinished, Waypoint, GPS_from_buoy, distance_between
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
        - Travel between each waypoint checking for buoys
            - Pan camera and take pictures for maximum FoV
            - Detect buoys
                - If x% match:
                    - Error Check:
                        - Take a confirmation picture and confirm its not one-off false positive
                        - Check if estimated position is outside of given bounds + buffer
                    - Approximate buoy's gps location
                    - Divert course and travel to buoy gps
                    - Focus camera on expected buoy position
                    - Take pictures intermittently & analyze
                    - Move camera to keep buoy in center frame
                    - If confidence stays above threshold:
                        - Keep moving towards buoy
                    - Else:
                        - False positive! PANIC! Return to previous search course
"""

REQUIRED_ARGS = 2

class Search(Event):
    """
    Attributes:
        - event_info (array) - center and radius of search circle
            event_info = [(center_lat, center_long), radius]
    """
    
    def __init__(self, event_info):
        if (len(event_info) != REQUIRED_ARGS):
            raise TypeError(f"Expected {REQUIRED_ARGS} arguments, got {len(event_info)}")
        
        super().__init__(event_info)
        logging.info("Search moment")
        self.object_detection = ObjectDetection()
        self.camera = Camera()
        
        self.waypoint_queue = self.create_search_pattern()
        self.tracking_buoy = False
    
    def next_gps(self):
        """
        Main event script logic. Executed continuously by boatMain.
        
        Returns either:
            - The next GPS point that the boat should sail to stored as a Waypoint object
            - OR None to signal the boat to drop sails and clear waypoint queue
            - OR EventFinished exception to signal that the event has been completed
        """
        
        if (self.tracking_buoy):
            # move towards buoy and keep in frame
            # if conf lowers
            # if conf stays same and far away
            # if nearby -> ram that shit & signal (unless accelerometer to detect?)
            if (distance_between(gps, waypoint) < 3):
                return
            return
        else:

            imgs: list[Frame] = self.camera.survey(num_images=3) # (detect=True?)
            
            for img in imgs:
                detections = self.object_detection.analyze(img)
            
            if len(detections) == 0:
                logging.info("No buoys spotted!")
                return None
            else:
                logging.info(f"{len(detections)} buoy(s) found!")
                
                #verify_detection(detections[0])
                
                waypoint = GPS_from_buoy(detections[0])
                logging.info(f"Moving to buoy at ({waypoint.lat}, {waypoint.long})")
                self.tracking_buoy = True
            
            return waypoint
    
    def create_search_pattern(self):
        """
        Generates a 5-point zig-zag search pattern to maximimize area coverage 
        
        Returns:
            - 5 gps coordinates stored as a list of Waypoints [Waypoint(lat, long), ...]
        """
        
        # Metrics used to fine-tune optimal coverage
        # TODO: test different values
        # Camera cone of vision from 
        BOAT_FOV = 242
        # Furthest distance object detection can reliably spot a buoy (m)
        MAX_DETECTION_DISTANCE = 20 # untested
        
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
    
    # TODO:
    def verify_detection(self, detection):
        """
        Take a 2nd verification picture to counter false positive
        """
        return
    
if __name__ == "__main__":
    pass