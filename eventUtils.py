"""
Event blueprint class and common utility functions used in events
"""
# Event descriptions can be found here: https://www.sailbot.org/wp-content/uploads/2022/05/SailBot-2022-Events.pdf

from abc import abstractmethod
from dataclasses import dataclass
import math
import time

try:
    from GPS import gps
    import constants as c

except Exception as e:
    from sailbot.GPS import gps
    import sailbot.constants as c
@dataclass(slots=True)
class Waypoint:
    """
    A GPS marker for buoys, travel destinations, etc.
    - Initialize using Waypoint(latitude, longitude)
    """
    
    lat: float
    long: float
    
class Event():
    """
    Basic blueprint for creating new events
    
    Attributes: 
        - event_info (array) - provided starter information about the event
            - event_info = []
    
    Functions:
        - next_gps() - event logic which determines where to sail to next
    """
    
    def __init__(self, event_info):        
        self.event_info = event_info
        
    @abstractmethod
    def next_gps(self):
        """
        Main event script logic. Executed continuously by boatMain.
        
        Returns either:
            - The next GPS point that the boat should sail to stored as a Waypoint object
            - OR None to signal the boat to drop sails and clear waypoint queue
            - OR EventFinished exception to signal that the event has been completed
        """

        raise NotImplementedError
            
class EventFinished(Exception):
    """Signals that the event is finished and that it is safe to return to manual control"""
    pass

"""
def PID():  #hana
    total_error = 0.0
    oldError = 0.0
    oldTime = time.time()
    last_pnt_x, .last_pnt_y = None,None
    gps_class = gps()
    # New PID stuff
    if (time.time() - oldTime < 100):  # Only runs every tenth of a second #new
        # Finds the angle the boat should take
        error = boat_RefObj.targetAngle - compass.angle  # Finds how far off the boat is from its goal
        totalError += error  # Gets the total error to be used for the integral gain
        derivativeError = (error - oldError) / (time.time() - oldtime)  # Gets the change in error for the derivative portion
        deltaAngle = c.config['CONSTANTS']["P"] * error + c.config['CONSTANTS']["I"] * totalError + c.config['CONSTANTS']["D"] * derivativeError  # Finds the angle the boat should be going

        # Translates the angle into lat and log so goToGPS won't ignore it
        boat_RefObj.currentAngle = getCoordinateADistanceAlongAngle(1000, deltaAngle + self.boat_RefObj.compass.angle)

        # Resets the variable
        oldTime = time.time()
        oldError = error
"""

def SK_f(self,x,a1,b1,a2,b2): return self.SK_m(a1,b1,a2,b2)*x + self.SK_v(a1,b1,a2,b2)  #f(x)=mx+b
def SK_m(self,a1,b1,a2,b2): return (b2-b1)/(a2-a1)                                      #m: slope between two lines
def SK_v(self,a1,b1,a2,b2): return b1-(self.SK_m(a1,b1,a2,b2)*a1)                       #b: +y between two lines
def SK_I(self,M1,V1,M2,V2): return (V2-V1)/(M1-M2)                                      #find x-cord intersect between two lines
def SK_d(self,a1,b1,a2,b2): return math.sqrt((a2-a1)**2 + (b2-b1)**2)                   #find distance between two points


# TODO: Return multiple waypoints when multiple buoys (append onto Detection class?)
def GPS_from_buoy(self, buoy):
    """Approximates the location of a detected buoy
        - Compares the ratio of buoy_size/distance to a fixed measured ratio
    # Args:
        - buoy (objectDetection.Detection): 
    # Returns:
        - eventUtils.Waypoint(Latitude, Longitude) object
    """
    # buoy_size_in_pixels = buoy.w * buoy.h
    #buoy_distance = None # What we want to find
    
    # measured_buoy_size_in_pixels = c.config["OBJECTDETECTION"]["Buoy_Width"] * c.config["OBJECTDETECTION"]["Buoy_Height"]
    # measured_buoy_distance = c.config["OBJECTDETECTION"]["Measured_distance"]
    # boat_gps = 0
    
    
    if c.config["OBJECTDETECTION"]["Width_Real"] == 0 or c.config["OBJECTDETECTION"]["Focal_Length"] == 0:
        raise Exception("MISSING WIDTH REAL/FOCAL LENGTH INFO IN CONSTANTS")
    dist = (c.config["OBJECTDETECTION"]["Width_Real"]*c.config["OBJECTDETECTION"]["Focal_Length"])/self.obj_info[2]
    comp = compass()    #assume 0 is north(y pos)
    geep = gps(); geep.updategps()

    t = math.pi/180
    
    latitude = dist*math.cos(comp.angle*t)+geep.latitude
    longitude =  dist*math.sin(comp.angle*t)+geep.longitude
    return Waypoint(latitude, longitude)
