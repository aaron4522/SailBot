import logging
import math
import time

from eventUtils import Event, EventFinished

"""
# Challenge Goal:
    - Demonstrate a successful autonomous collision avoidance system.
        
        # Description:
            - The boat will start between two buoys
            - will sail autonomously on a reach to another buoy and return
            - Sometime during the trip, a manned boat will approach on a collision course
            - RC is not permitted after the start.
            
        # Scoring:
            - 10 pts max
            - 7 pts if the boat responds but a collision still occurs
            - 2 pt deduction if the respective buoy(s) are not reached following the avoidance maneuver
            - 3 pts max by alternative dry-land demo of appropriate sensor/rudder interaction.
            
        # Assumptions: (based on guidelines)
            - left of start direction is upstream
            - going back is harder
            
        # Strategy:
            - TODO write psuedocode about how this event logic works
"""

REQUIRED_ARGS = 2

class CollisionAvoidance(Event):
    """
    Attributes:
        - event_info (array) - buoy coordinates of path to travel
            event_info = [(start_long, start_lat), (b1_long, b1_lat)]
    """
    
    def __init__(self, event_info):
        if (len(event_info) != REQUIRED_ARGS):
            raise TypeError(f"Expected {REQUIRED_ARGS} arguments, got {len(event_info)}")
        
        super().__init__(event_info)
        logging.info("Collision Avoidance moment")
        

    def next_gps(self):
        """The next GPS point that the boat should go to"""
        return 0,0
    
    def loop(self):
        """Event logic that will be executed continuously"""
        raise EventFinished
    