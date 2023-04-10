import logging

from eventUtils import Event, EventFinished

REQUIRED_ARGS = 0

class ManualControl(Event):
    """
    Attributes:
        - event_info (array) - customizable arguments (unusued)
            event_info = []
    """
    def __init__(self, event_info=[]):
        if (len(event_info) != REQUIRED_ARGS):
            raise TypeError(f"Expected {REQUIRED_ARGS} arguments, got {len(event_info)}")
        
        super().__init__(event_info)
        logging.info("Manual control moment")
    
    def next_gps(self):
        """The next GPS point that the boat should go to"""
        return 0,0
    
    def loop(self):
        """Event logic that will be executed continuously"""
        raise EventFinished

if __name__ == "__main__":
    pass