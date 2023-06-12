"""
interfaces with USB GPS sensor
"""
import logging
# https://learn.adafruit.com/adafruit-ultimate-gps/circuitpython-parsing
import time
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from time import sleep
import gpsd

from sailbot.utils.boatMath import convertDegMinToDecDeg
from sailbot.utils.utils import singleton


@singleton
class gps(Node):
    """
    Attributes:
        latitude (float): the current latitude of the boat
        longitude (float): the current longitude of the boat
    """

    def __init__(self):
        self.latitude = None
        self.longitude = None

        # Can also use adafruit_gps module (but didn't work at competition?)
        # Prev GPS version w/ adafruit: https://github.com/SailBotPitt/SailBot/blob/a56a18b06cbca78aace1990a4a3ce4dfd8c7a847/GPS.py
        # GPSD doesn't have gps track angle degree
        gpsd.connect()
        packet = gpsd.get_current()
        if packet.mode >= 2:
            self.latitude = packet.position()[0]
            self.longitude = packet.position()[1]
            logging.debug(f"GPS: {self.latitude} {self.longitude}")
        else:
            logging.warning(f"No GPS fix")

        super().__init__('GPS')
        self.pub = self.create_publisher(String, 'GPS', 10)
        timer_period = 0.5  # seconds
        self.timer = self.create_timer(timer_period, self.timer_callback)

    def timer_callback(self):
        msg = String()
        packet = gpsd.get_current().position()
        self.latitude = packet[0]
        self.longitude = packet[1]
        msg.data = F"{self.latitude},{self.longitude}"
        self.pub.publish(msg)
        self.get_logger().info('Publishing: "%s"' % msg.data)

    def __getattribute__(self, name):
        """
        if an attempt is made to access an attribute that does not exist, it will then attempt to get the attribute from gps object
        this means that rather than using gps_object.gps.longitude, it is possible to use gps_object.longitude
        """
        try:
            return super().__getattribute__(name)
        except:
            return self.gps.__getattribute__(name)

    def run(self):
        # TODO: Delete
        while True:
            return # This should use ROS now instead of a loop
            #self.updategps()

    def readgps(self):
        # TODO: delete
        timestamp = time.monotonic()
        while True:
            data = self.gps.read(64)

            if data is not None:
                data_string = ''.join([chr(b) for b in data])
                print(data_string, end="")

                if time.monotonic() - timestamp > 5:
                    self.gps.send_command(b'PMTK605')
                    timestamp = time.monotonic()

    def updategps(self, print_info = False):
        # TODO: Delete
        # must be called before reading latitude and longitude, just pulls data from the sensor
        # optionally prints data read from sensor
        self.gps.update()
        if(self.gps.has_fix):
            self.latitude = self.gps.latitude
            self.longitude = self.gps.longitude
            self.track_angle_deg = self.gps.track_angle_deg
        if print_info:
            #print(self.latitude,self.longitude, self.gps.latitude,self.gps.longitude)
            if not self.gps.has_fix:
                print("Waiting for fix")
                return

            print('Fix timestamp: {}/{}/{} {:02}:{:02}:{:02}'.format(
                self.gps.timestamp_utc.tm_mon,   # Grab parts of the time from the
                self.gps.timestamp_utc.tm_mday,  # struct_time object that holds
                self.gps.timestamp_utc.tm_year,  # the fix time.  Note you might
                self.gps.timestamp_utc.tm_hour,  # not get all data like year, day,
                self.gps.timestamp_utc.tm_min,   # month!
                self.gps.timestamp_utc.tm_sec))

            print('Latitude: {0:.8f} degrees'.format(self.gps.latitude))
            print('Longitude: {0:.8f} degrees'.format(self.gps.longitude))
            print('Lat in decDeg:', convertDegMinToDecDeg(self.gps.latitude) )
            print('long in decDeg:', convertDegMinToDecDeg(self.gps.longitude) )
            print('Fix quality: {}'.format(self.gps.fix_quality))
            self.latitude = self.gps.latitude
            self.longitude = self.gps.longitude
            # Some attributes beyond latitude, longitude and timestamp are optional
            # and might not be present.  Check if they're None before trying to use!
            """if gps.satellites is not None:
                print('# satellites: {}'.format(self.gps.satellites))
            if gps.altitude_m is not None:
                print('Altitude: {} meters'.format(self.gps.altitude_m))
            if gps.speed_knots is not None:
                print('Speed: {} knots'.format(self.gps.speed_knots))
            if gps.track_angle_deg is not None:
                print('Track angle: {} degrees'.format(self.gps.track_angle_deg))
            if gps.horizontal_dilution is not None:
                print('Horizontal dilution: {}'.format(self.gps.horizontal_dilution))
            if gps.height_geoid is not None:
                print('Height geo ID: {} meters'.format(self.gps.height_geoid))
            """

def main(args = None):
    rclpy.init(args=args)
    GPS = gps()
    rclpy.spin(GPS)

    # Destroy the node explicitly
    # (optional - otherwise it will be done automatically
    # when the garbage collector destroys the node object)
    GPS.destroy_node()
    rclpy.shutdown()
    

if __name__ == "__main__":
    rclpy.init()
    GPS = gps()
    rclpy.spin(GPS)
    while True:
        GPS.updategps(print_info=True)
        sleep(1)
