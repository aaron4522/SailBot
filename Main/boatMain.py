import constants as c
import logging

from windvane import windVane
import GPS
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
        self.compass = GPS.compass()
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
        """
        Old Code, use goToGPS instead

        """
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

    def goToGPS(self, lat, long):
        angleToTarget = GPS.angleBetweenCoordinates(self.gps.latitude, self.gps.longitude) 
        compassAngle = self.compass.mag
        targetAngle = compassAngle + angleToTarget #angle of target relative to north
        windAngle = self.windvane.angle
        if windAngle > self.windvane.noGoMin and windAngle < self.windvane.noGoMax:
            #turn to target
            turnToAngle(targetAngle)
        else:
            if compassAngle - targetAngle < 0:
                #turn left
                turnToAngle(compassAngle + self.windvane.noGoMin)
            else:
                #turn right
                turnToAngle(compassAngle + self.windvane.noGoMax)

    def turnToAngle(self, angle):
        leftPositive = 1 #change to negative one if boat is rotating the wrong way
        logging.info("starting turnToAngle")
        compassAngle = self.compass.mag
        while abs(compassAngle - angle) > 2:
            compassAngle = self.compass.mag
            
            if compassAngle > angle and compassAngle < angle + 180: #turn right
                rudderPos = -1*leftPositive*min(-45, (compassAngle - angle)/c.rotationSmoothingConst)
                logging.info(F'turning to angle: {angle} from angle: {compassAngle} by turning rudder to {rudderPos}')
                adjustRudder(rudderPos)
            else: #turn left
                rudderPos = leftPositive*min(-45, (compassAngle - angle)/c.rotationSmoothingConst)
                logging.info(F'turning to angle: {angle} from angle: {compassAngle} by turning rudder to {rudderPos}')
                adjustRudder(rudderPos)
        logging.info("finished turnToAngle")

if __name__ == "__main__":

    boat()

