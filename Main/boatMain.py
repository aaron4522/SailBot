import constants as c
import logging

from windvane import windVane
from GPS import Gps 
from drivers import driver
from transceiver import arduino
from datetime import date, datetime


class boat:

    def __init__(self):
        with open('boatMainLog.log', 'a') as logfile:
            logfile.write('\n\n---------------------------------\n')
        logging.basicConfig(level=logging.INFO, filename='boatMainLog.log', filemode='a', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        self.gps = Gps()
        self.windvane = windVane()
        self.drivers = driver(autoSail = False)
        self.arduino = arduino(c.config['MAIN']['ARDU_PORT'])

        self.currentTarget = None # (longitude, latitude) tuple
        self.targets = [] # holds (longitude, latitude) tuples

        noGoZoneDegs = 20

        tempTarget = False

    def move(self):
        if self.gps.distanceTo(currentTarget) < c.config['MAIN']['ACCEPTABLE_RANGE'] and len(self.targets) > 0:
            #next target

            targetAngle = TargetAngleRelativeToNorth() #Func doesnt exist yet

            windAngleRelativeToNorth = convertWindAngle(self.windVane.angle)

            if tempTarget == False and targetAngle - windAngleRelativeToNorth < (noGoZoneDegs/2):
                if targetAngle < windAngleRelativeToNorth or abs(targetAngle - 360) < windAngleRelativeToNorth:
                    #newTargetAngle < targetangle
                    newTargetAngle = windAngleRelativeToNorth - (noGoZoneDegs/2 + 10) 
                else:
                    #newTargetAngle > targetAngle
                    newTargetAngle = windAngleRelativeToNorth + (noGoZoneDegs/2 + 10)

                tempTarget = True
                rotateToAngle(newTargetAngle)
                logging.info('Heading to temp target at: %d' , newTargetAngle)

            elif tempTarget and targetAngle - windAngleRelativeToNorth > (noGoZoneDegs/2):
                tempTarget = False
                logging.info('Heading to target at: %d', targetAngle)
                rotateToAngle(targetAngle)

            elif tempTarget == False:
                logging.info('Heading to target at: %d', targetAngle)
                rotateToAngle(targetAngle)

            # else:
            #     self.currentTarget = self.targets.pop(0)

        else:
            #move towards target
            self.adjustSail()
            self.adjustRudder()
            
    def adjustSail(self):
        if self.currentTarget:
            windDir = self.windvane.angle
            targetAngle = windDir + 35
            self.drivers.sail.set(targetAngle)
            logging.info('Adjusted sail to: %d', targetAngle)
        else:
            #move sail to home position
            self.drivers.sail.set(0)
            logging.info('Adjusted sail to home position')
            
    def adjustRudder(self):
        if self.currentTarget:
            #adjust rudder for best wind
            angleTo = gps.angleTo(self.currentTarget)
            d_angle = angleTo - gps.track_angle_deg

            if d_angle > 180: d_angle -= 180

            self.drivers.rudder.set(d_angle)
            logging.info('Adjusted rudder to: %d', d_angle)
            
        else:
            #move sail to home position
            self.drivers.rudder.set(0)
            logging.info('Adjusted rudder to home position')

    def readMessages(self):
        msgs = self.arduino.read()

        for msg in msgs:
            ary = msg.split(' ')
            if len(ary) > 1:
                if ary[0] == 'sail': 
                    self.drivers.sail.set(float(ary[1]))
                    logging.info('Received message to adjust sail')
                elif ary[0] == 'rudder': 
                    self.drivers.rudder.set(float(ary[1]))
                    logging.info('Received message to adjust rudder')
                elif ary[0] == 'mode': print("TODO: add Modes")

if __name__ == "__main__":

    boat()

