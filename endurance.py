import logging

from eventUtils import Event, EventFinished

"""
# Challenge Goal:
    - To demonstrate the boat's durability and capability to sail some distance
    
    # Description:
        - The boats will sail around 4 buoys (passing within 10 m inside of buoy is OK) for up to 7 hours
    
    # Scoring:
        - 10 pts max
        - 1 pt for each 1NM lap completed autonomously (1/2 pt/lap if RC is used at any point during the lap*)
        - An additional 1pt for each continuous (no pit-stop) hr sailed; up to 6 pts
        - At least one lap must be completed to earn points
        - All boats must start each subsequent lap at the Start line following a pit stop or support boat rescue. (*No penalty for momentary RC to avoid collisions.)
    
    # Assumptions: (based on guidelines)
        - left of start direction is upstream
    
    # Strategy:
        - TODO write psuedocode about how this event logic works
"""

REQUIRED_ARGS = 4

class Endurance(Event):
    """
    Attributes:
        - event_info (array) - 4 GPS coordinates forming a rectangle that the boat must sail around
            event_info = [(b1_long, b1_lat),(b2_long, b2_lat),(b3_long, b3_lat),(b4_long, b4_lat)]
    """
    
    def __init__(self, event_info):
        if (len(event_info) != REQUIRED_ARGS):
            raise TypeError(f"Expected {REQUIRED_ARGS} arguments, got {len(event_info)}")
        
        super().__init__(event_info)
        logging.info("Endurance moment")
        

    def next_gps(self):
        """The next GPS point that the boat should go to"""
        return 0,0
    
    def loop(self):
        """Event logic that will be executed continuously"""
        raise EventFinished

if __name__ == "__main__":
    pass