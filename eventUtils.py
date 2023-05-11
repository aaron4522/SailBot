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
    lon: float
    
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


def distance_between(waypoint1, waypoint2):
    """Calculates the distance between two GPS points using the Haversine formula
    # Args:
        - waypoint1 (eventUtils.Waypoint)
        - waypoint2 (eventUtils.Waypoint)
    # Returns:
        - distance in meters between points (float)
    """
    EARTH_RADIUS = 6371 # Km
    
    # Convert latitude and longitude to radians
    lat1, lon1, lat2, lon2 = map(math.radians, [waypoint1.lat, waypoint1.long, waypoint2.lat, waypoint2.long])

    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    distance = EARTH_RADIUS * c

    return distance
