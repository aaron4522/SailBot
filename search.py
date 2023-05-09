import logging
import math
import time
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from dataclasses import dataclass

import constants as c
from eventUtils import Event, EventFinished, Waypoint, distance_between
from camera import Camera, Frame

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
        - Define a Z-shaped search pattern
        - Travel along the search path while taking panoramas to detect buoys
            - If heatmap has a high confidence point of interest:
                - Save current position and divert course towards buoy
                - Focus camera on expected buoy position and take pictures
                - If that buoy still be a buoy:
                    - Keep moving towards buoy and ram that shit
                - Else:
                    - False positive (hopefully VERY rare)! PANIC! Return to previous search course
                    - Blacklist location (NOT IMPLEMENTED)
                    
            - If x% buoy match:
                - Ignore if estimated position is outside of bounds + buffer
                - Add to heatmap
                
"""

REQUIRED_ARGS = 2


class Search(Event):
    """
    Attributes:
        - search_center (Waypoint): the center of the search bounds
        - search_radius (float): the radius of the search bounds
        - start_time (float): the start time of the event

        - waypoint_queue (list[Waypoint]): the path for the boat to follow
        - heatmap (list[HeatmapChunk]): pools detections together
        - divert_conf_thresh (float): the required pooled confidence level of an area for the boat to move towards it
        - is_tracking_buoy (bool): whether the boat is deviating from search course to reach a potential buoy
    """

    def __init__(self, event_info):
        """
        Args:
            event_info (list[Waypoint(center_lat, center_long), radius]): center and radius of search circle
        """
        if len(event_info) != REQUIRED_ARGS:
            raise TypeError(f"Expected {REQUIRED_ARGS} arguments, got {len(event_info)}")
        super().__init__(event_info)
        logging.info("Search moment")

        self.search_center = event_info[0]
        self.search_radius = event_info[1]
        self.search_radius_tolerance = float(c.config["SEARCH"]["search_radius_tolerance"])
        self.start_time = time.time()

        self.heatmap = Heatmap(chunk_radius=float(c.config["SEARCH"]["heatmap_chunk_radius"]))
        self.waypoint_queue = self.create_search_pattern()
        self.divert_confidence_threshold = float(c.config["SEARCH"]["pooled_heatmap_confidence_threshold"])
        self.is_tracking_buoy = False
        self.best_chunk = None
        self.tracking_abandon_threshold = int(c.config["SEARCH"]["tracking_abandon_threshold"])

        self.camera = Camera()
        self.gps = self.create_subscription(String, 'GPS', self.ROS_GPSCallback, 10) # TODO: Fix this

    def next_gps(self):
        """
        Main event script logic. Executed continuously by boatMain.
        
        Returns either:
            - The next GPS point that the boat should sail to stored as a Waypoint object
            - OR None to signal the boat to drop sails and clear waypoint queue
            - OR EventFinished exception to signal that the event has been completed
        """

        # TRACKING STATE
        # A buoy is found and boat is heading towards it
        if self.is_tracking_buoy:
            distance_to_buoy = distance_between(self.gps, self.waypoint_queue[0])
            if distance_to_buoy < 3:
                # TODO: How to detect that boat touches buoy?
                #  Accelerometer?
                #  Just hit the shit out of the general area?
                # Boat is near the buoy, TIME TO RAM THAT SHIT
                logging.info(f"TRACKING: {distance_to_buoy}m away from buoy! RAMMING TIME")

                # TODO: Signal that boat touched buoy
                raise EventFinished

            else:
                # Boat is still far away from buoy
                logging.info(f"TRACKING: {distance_to_buoy}m away from buoy! Closing in!")
                try:
                    self.camera.focus(self.waypoint_queue[0])
                except RuntimeError as e:
                    logging.warning(f"""TRACKING: Exception raised: {e}\n
                    Camera can't focus on target!""")
                    return self.waypoint_queue[0]

                frame = self.camera.capture(context=True, detect=True)

                # Abandon if boat can't find buoy multiple times in a row (hopefully VERY rare)
                if len(frame.detections) == 0:
                    logging.info("TRACKING: Lost buoy")
                    self.tracking_abandon_threshold -= 1
                    if self.tracking_abandon_threshold == 0:
                        logging.warning("TRACKING: Can't find buoy! Abandoning course and returning to search")
                        self.is_tracking_buoy = False
                        self.tracking_abandon_threshold = int(c.config["SEARCH"]["tracking_abandon_threshold"])
                        # TODO: blacklist buoy gps from future tracking
                else:
                    self.tracking_abandon_threshold = int(c.config["SEARCH"]["tracking_abandon_threshold"])

                    for detection in frame.detections:
                        distance_from_center = distance_between(self.search_center, detection.gps)
                        if distance_from_center < self.search_radius + self.search_radius_tolerance:
                            logging.info(f"TRACKING: Buoy found at: {detection.gps}")
                            self.heatmap.append(detection)
                        else:
                            logging.info(f"TRACKING: Dropped buoy at: {detection.gps}, {distance_from_center}m from center")

                    logging.info(f"TRACKING: Continuing course to buoy at: {self.best_chunk.average_gps}")
                    self.waypoint_queue[0] = self.best_chunk.average_gps
                    return self.waypoint_queue[0]

        # SEARCHING STATE
        # Either no buoys found yet or boat is gathering more confidence before committing to divert course
        else:
            # Capture panorama of surroundings
            imgs = self.camera.survey(num_images=3, detect=True)

            # Error check detections & add to heatmap
            detections = 0
            for frame in imgs:
                for detection in frame.detections:
                    distance_from_center = distance_between(self.search_center, detection.gps)
                    if distance_from_center < self.search_radius + self.search_radius_tolerance:
                        logging.info(f"SEARCHING: Buoy found at: {detection.gps}")
                        self.heatmap.append(detection)
                    else:
                        logging.info(f"SEARCHING: Dropped buoy at: {detection.gps}, {distance_from_center}m from center")

            if detections == 0:
                # No detections, continue along preset search path
                logging.info("SEARCHING: No buoys spotted! Continuing along search path")
                if distance_between(self.gps, self.waypoint_queue[0]) < 1:
                    self.waypoint_queue.pop(0)
                return self.waypoint_queue[0]

            else:
                # Detection! Check if boat is confident enough to move to a buoy
                logging.info(f"SEARCHING: {detections} buoy(s) found!")
                self.best_chunk = self.heatmap.get_highest_confidence_chunk()

                if self.best_chunk.sum_confidence > self.divert_confidence_threshold:
                    logging.info(f"""SEARCHING: Divert confidence level reached! 
                    Bookmarking position and moving towards buoy at {self.best_chunk.average_gps}.""")
                    self.is_tracking_buoy = True
                    self.waypoint_queue.insert(0, self.gps)
                    self.waypoint_queue.insert(0, self.best_chunk.average_gps)
                    return self.waypoint_queue[0]

    def create_search_pattern(self):
        """
        Generates a 5-point zig-zag search pattern to maximimize area coverage 
        
        Returns:
            - 5 gps coordinates stored as a list of Waypoints [Waypoint(lat, long), ...]
        """
        # TODO: Fix
        # Metrics used to fine-tune optimal coverage
        # TODO: test different values
        # Camera cone of vision from 
        BOAT_FOV = 242
        # Furthest distance object detection can reliably spot a buoy (m)
        MAX_DETECTION_DISTANCE = 20  # untested

        pattern = []

        a = self.gps.latitude - self.search_center.lat
        b = self.gps.longitude - self.search_center.lon
        ang = math.atan(b / a)
        ang *= 180 / math.pi

        if (a < 0): ang += 180

        tar_angs = [ang, ang + 72, ang - 72, ang - (72 * 3), ang - (72 * 2)]
        for i in range(0, 5):
            pattern.append(
                Waypoint(
                    lat=self.event_arr[0] + self.event_arr[2] * math.cos(tar_angs[i] * (math.pi / 180)),
                    lon=self.event_arr[1] + self.event_arr[2] * math.sin(tar_angs[i] * (math.pi / 180))
                )
            )

        return pattern

    def ROS_GPSCallback(self, string):
        if string == "None, None, None":
            self.gps.latitude = None
            self.gps.longitude = None
            self.gps.track_angle_deg = None
            return

        lat, long, trackangle = string.replace("(", "").replace(")", "").split(",")
        self.gps.latitude = float(lat)
        self.gps.longitude = float(long)
        self.gps.track_angle_deg = float(trackangle)


class Heatmap:
    """Datastructure which splits the search radius into X-meter circular 'chunks'
        - Each detection has its confidence pooled with all others inside the same chunk
        - Lower chunk radius if two separate buoys are being grouped as one
        - Raise chunk radius if the same buoy is creating multiple chunks (caused by GPS estimation error)
        - NOTE: Chunks can overlap which may cause problems (if so, then use tri/square/hex chunks instead of circles)

        Attributes:
            - chunks (list[HeatmapChunk])
            - chunk_radius (float)
    """

    def __init__(self, chunk_radius):
        self.chunks = []
        self.chunk_radius = chunk_radius

    def __contains__(self, detection):
        """
        Checks if a detection is inside any of the heatmap's chunks' boundary
            - Invoke using the 'in' keyword ex. 'if detection in heatmap'
        """
        for chunk in self.chunks:
            if detection in chunk:
                return True
        return False

    def append(self, detection):
        # TODO (Low): Overload to support list[Detection]
        for chunk in self.chunks:
            if detection in chunk:
                chunk.append(detection)
        else:
            self.chunks.append(HeatmapChunk(radius=self.chunk_radius,
                                            detection=detection))

    def get_highest_confidence_chunk(self):
        max_confidence = 0
        max_chunk = None
        for chunk in self.chunks:
            if chunk.sum_confidence > max_confidence:
                max_confidence = chunk.sum_confidence
                max_chunk = chunk
        return max_chunk


class HeatmapChunk:
    """
    A circular boundary which combines nearby detections for better accuracy
        - Detections within the chunk's radius are assumed to be from the same buoy and averaged

    Attributes:
        - radius (float): the radial size of the chunk
        - average_gps (Waypoint): the average point between all detections within a chunk
        - detection_count (int): the number of detections within a chunk
        - sum_confidence (float): the combined total of all detections within the chunk
    """

    def __init__(self, radius, detection):
        self.radius = radius
        self.average_gps = detection.gps
        self.detection_count = 1
        self.sum_confidence = detection.conf

        self._sum_lat = detection.gps.latitude
        self._sum_lon = detection.gps.longitude

    def __contains__(self, detection):
        return distance_between(self.average_gps, detection.gps) <= self.radius

    def append(self, detection):
        self.detection_count += 1

        self._sum_lat += detection.gps.latitude
        self._sum_lon += detection.gps.longitude
        self.average_gps = Waypoint(self._sum_lat / self.detection_count, self._sum_lon / self.detection_count)

        self.sum_confidence += detection.conf
