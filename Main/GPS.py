
#https://learn.adafruit.com/adafruit-ultimate-gps/circuitpython-parsing
import time

import board
import busio
import adafruit_gps
# import adafruit_lsm303_accel
import adafruit_lsm303dlh_mag

from time import sleep
from threading import Thread
import math
from boatMath import degreesToRadians, getCoordinateADistanceAlongAngle, distanceInMBetweenEarthCoordinates, computeNewCoordinate, angleBetweenCoordinates, convertDegMinToDecDeg, convertWindAngle







class gps():

    def __init__(self):

        # a slightly higher timeout (GPS modules typically update once a second).
        # These are the defaults you should use for the GPS FeatherWing.
        # For other boards set RX = GPS module TX, and TX = GPS module RX pins.
        #self.uart = busio.UART(board.TX, board.RX, baudrate=9600, timeout=10)
        #

        # for a computer, use the pyserial library for uart access
        import serial
        self.latitude =  None
        self.longitude = None
        self.track_angle_deg = 0
        #self.uart = serial.Serial("/dev/ttyACM1", baudrate=9600, timeout=10)
        self.uart = serial.Serial("/dev/ttyUSB0", baudrate=9600, timeout=10)
        self.gps = adafruit_gps.GPS(self.uart, debug=False)


        # Turn on the basic GGA and RMC info (what you typically want)
        self.gps.send_command(b'PMTK314,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0')
        # Turn on just minimum info (RMC only, location):
        #gps.send_command(b'PMTK314,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0')
        # Turn off everything:
        #gps.send_command(b'PMTK314,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0')
        # Turn on everything (not all of it is parsed!)
        #gps.send_command(b'PMTK314,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0')

        # Set update rate to once a second (1hz) which is what you typically want.
        self.gps.send_command(b'PMTK220,1000')
        # Or decrease to once every two seconds by doubling the millisecond value.
        # Be sure to also increase your UART timeout above!
        #gps.send_command(b'PMTK220,2000')
        # You can also speed up the rate, but don't go too fast or else you can lose
        # data during parsing.  This would be twice a second (2hz, 500ms delay):
        #gps.send_command(b'PMTK220,500')

        #pump_thread = Thread(target=self.run)# creates a Thread running an infinite loop pumping server
        #pump_thread.start()

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
        while True:
            self.updategps()

    def readgps(self):
        timestamp = time.monotonic()
        while True:
            data = self.gps.read(64)

            if data is not None:
                data_string = ''.join([chr(b) for b in data])
                print(data_string, end="")

                if time.monotonic() - timestamp > 5:
                    self.gps.send_command(b'PMTK605')
                    timestamp = time.monotonic()

    def updategps(self, print_info = True):
            
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

class compass():
    def __init__(self):
        i2c = busio.I2C(board.SCL, board.SDA)
        self.mag = adafruit_lsm303dlh_mag.LSM303DLH_Mag(i2c)
        #self.accel = adafruit_lsm303_accel.LSM303_Accel(i2c)
        
    
        
    def printAccel(self):
        print("Acceleration (m/s^2)): X=%0.3f Y=%0.3f Z=%0.3f"%self.accel.acceleration)
    def printMag(self):
        print("Magnetometer (micro-Teslas)): X=%0.3f Y=%0.3f Z=%0.3f"%self.mag.magnetic)

if __name__ == "__main__":
    GPS = gps()
    while True:
        GPS.updategps()
        sleep(1)
