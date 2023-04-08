"""
Event blueprint class and common utility functions used in events
"""
# Event descriptions can be found here: https://www.sailbot.org/wp-content/uploads/2022/05/SailBot-2022-Events.pdf

from abc import abstract
import math
import time

try:
    from GPS import gps
    import constants as c

except Exception as e:
    from sailbot.GPS import gps
    import sailbot.constants as c
    

@abstract
class Event():
    """
    Basic blueprint for creating new events
    
    Attributes: TODO
        - event_info (array) - provided starter information about the event
            - further clarified in each specific class
        - total_error - 
        - old_error - 
        - old_time - 
        - last_pnt_x
        - last_pnt_y
    
    Functions: TODO
        - PID() - 
    """
    
    def __init__(self, event_info):        
        self.event_info = event_info
        self.total_error = 0.0
        self.oldError = 0.0
        self.oldTime = time.time()
        self.last_pnt_x, self.last_pnt_y = None,None
        self.gps_class = gps()
        
    def next_gps(self):
        """
        The next GPS point that the boat should go to
        
        Returns:
            - (long, lat) for next coordinates for boat to sail to
            - (None, None) signals to drop sails and clear target
        """

        raise NotImplementedError
    
    def loop(self):
        """Event logic that will be executed continuously"""
        raise NotImplementedError
    
    #TODO: find new place to relocate
    def PID(self):  #hana
        # New PID stuff
        if (time.time() - self.oldTime < 100):  # Only runs every tenth of a second #new
            # Finds the angle the boat should take
            error = self.boat_RefObj.targetAngle - self.compass.angle  # Finds how far off the boat is from its goal
            self.totalError += error  # Gets the total error to be used for the integral gain
            derivativeError = (error - self.oldError) / (time.time() - self.oldtime)  # Gets the change in error for the derivative portion
            deltaAngle = c.config['CONSTANTS']["P"] * error + c.config['CONSTANTS']["I"] * self.totalError + c.config['CONSTANTS']["D"] * derivativeError  # Finds the angle the boat should be going

            # Translates the angle into lat and log so goToGPS won't ignore it
            self.boat_RefObj.currentAngle = getCoordinateADistanceAlongAngle(1000, deltaAngle + self.boat_RefObj.compass.angle)

            # Resets the variable
            self.oldTime = time.time()
            self.oldError = error
            
class EventFinished(Exception):
    """Signals that the event is finished and that it is safe to return to manual control"""
    pass

# TODO: Jonah explain? Can move outside class?
def SK_f(self,x,a1,b1,a2,b2): return self.SK_m(a1,b1,a2,b2)*x + self.SK_v(a1,b1,a2,b2)  #f(x)=mx+b
def SK_m(self,a1,b1,a2,b2): return (b2-b1)/(a2-a1)                                      #m: slope between two lines
def SK_v(self,a1,b1,a2,b2): return b1-(self.SK_m(a1,b1,a2,b2)*a1)                       #b: +y between two lines
def SK_I(self,M1,V1,M2,V2): return (V2-V1)/(M1-M2)                                      #find x-cord intersect between two lines
def SK_d(self,a1,b1,a2,b2): return math.sqrt((a2-a1)**2 + (b2-b1)**2)                   #find distance between two points
