import logging
import argparse

from sailbot.utils.utils import singleton
from sailbot.controls import boatMovement
from sailbot.sensors import transceiver
from sailbot.events import stationKeeping, manualControl, collisionAvoidance, search, endurance, precisionNavigation
from sailbot.utils import eventUtils

# TODO: move to config
events = {"RC": manualControl.ManualControl,
          "CA": collisionAvoidance.CollisionAvoidance,
          "ED": endurance.Endurance,
          "PN": precisionNavigation.Precision_Navigation,
          "SE": search.Search,
          "SK": stationKeeping.Station_Keeping}


@singleton
class Boat:
    def __init__(self, event="RC", event_data=None):
        self.event = get_event(name=event,
                               event_data=event_data)

        self.transceiver = transceiver.Transceiver()

    def __del__(self):
        # TODO: auto send log entries through transceiver?
        logging.info("Shutting down")
        transceiver.send("Shutting down")

    def main_loop(self):
        """
        The main control logic which runs each tick

        """
        # TODO: Listen for new info from transceiver
            # TODO: Args: change event, stop, send heartbeat, etc.

        try:
            boatMovement.go_to_gps(self.event.next_gps())
        except eventUtils.EventFinished:
            logging.info("Event finished. Returning to RC")
            self.event = get_event("RC", [])

        # TODO: send data


def get_event(name, event_data):
    return events[name](event_data)


def main(args=None):
    # TODO: add functionality to args
    parser = argparse.ArgumentParser(prog='Sailbot')
    parser.add_argument("-e", "--event",
                        help="the mode that the boat starts in, default is RC")
    parser.add_argument("-d", "--debug",
                        help="raises exceptions instead of ignoring them (so that the boat doens't crash during competition), default is off")

    boat = Boat(event="RC")

    while True:
        boat.main_loop()


if __name__ == "__main__":
    main()