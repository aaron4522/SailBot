import constants as c
import logging

from windvane import windVane
from GPS import gps as Gps 
from drivers import driver
from transceiver import arduino
from datetime import date, datetime
from threading import Thread


class boat:

    def __init__(self):
        with open('boatMainLog.log', 'a') as logfile:
            logfile.write('\n\n---------------------------------\n')
        logging.basicConfig(level=logging.INFO, filename='boatMainLog.log', filemode='a', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        self.gps = Gps()
        self.windvane = windVane()
        self.drivers = driver(sailAuto = False)
        self.arduino = arduino(c.config['MAIN']['ardu_port'])

        self.currentTarget = None # (longitude, latitude) tuple
        self.targets = [] # holds (longitude, latitude) tuples

        noGoZoneDegs = 20

        tempTarget = False
        
        pump_thread = Thread(target=self.pumpMessages)
        pump_thread.start()

    def move(self):
        if self.gps.distanceTo(currentTarget) < float(c.config['MAIN']['acceptable_range']) and len(self.targets) > 0:
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
            
    def pumpMessages(self):
        while True:
            self.readMessages()

    def readMessages(self):
        msgs = self.arduino.read()
        print(msgs)
        
        #for msg in msgs:
        if True:
            msg = msgs
            ary = msg.split(' ')
            if len(ary) > 1:
                if ary[0] == 'sail': 
                    self.drivers.sail.set(float(ary[1]))
                    logging.info('Received message to adjust sail')
                elif ary[0] == 'rudder': 
                    self.drivers.rudder.set(float(ary[1]))
                    logging.info('Received message to adjust rudder')
                elif ary[0] == 'mode': print("TODO: add Modes")

    def goBetweenBuoy(self, LeftBuoyPixel, RightBuoyPixel):
        #Both in camera, assuming arguments = none if not in camera
        if LeftBuoyPixel and RightBuoyPixel:
            #Find distance of buoys to center line
            #TODO Add the total camera pixel size to constants (x,y)
            #Thought it only x distance needs to be checked
            distLeft = abs(LeftBuoyPixel[1] - c.cameraPixelSizeX/2.0)
            distRight = abs(RightBuoyPixel[1] - c.cameraPixelSizeX/2.0)

            #Check if one is significantly closer to center
            #TODO determine pixel wise what is significantly closer
            if distRight - distLeft > 20: #Left buoy is closer
                #Turn right
                newCompassAngle = (self.compass.mag + 10) % 360
                self.turnToAngle(newCompassAngle)
            elif distLeft - distRight > 20: #Right buoy closer
                #Turn left
                newCompassAngle = (self.compass.mag - 10) % 360
                self.turnToAngle(newCompassAngle)
        else:
            #Go to gps
            self.goToGps(self.currentTarget[0], self.currentTarget[1])


if __name__ == "__main__":

    boat()

