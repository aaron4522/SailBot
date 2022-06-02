
import constants as c
import logging
import boatMath
import math
try:
    from windvane import windVane
    from GPS import gps
    from compass import compass
    import GPS
    
    from drivers import driver
    from transceiver import arduino
except Exception as e:
    print("Failed to import some modules, if this is not a simulation fix this before continuing")
    print(F"Exception raised: {e}")
from datetime import date, datetime
from threading import Thread
from time import sleep

import numpy

class boat:

    def __init__(self):
        with open('boatMainLog.log', 'a') as logfile:
            logfile.write('\n\n---------------------------------\n')
        logging.basicConfig(level=logging.INFO, filename='boatMainLog.log', filemode='a', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        self.gps = GPS.gps()
        self.compass = compass()
        self.windvane = windVane()
        self.drivers = driver()
        #self.arduino = arduino(c.config['MAIN']['ardu_port'])
        print("arduino disabled")	

        self.manualControl = True
        self.cycleTargets = False
        self.currentTarget = None # (longitude, latitude) tuple
        self.targets = [] # holds (longitude, latitude) tuples

        noGoZoneDegs = 20

        tempTarget = False

        self.mainLoop()        
        # pump_thread = Thread(target=self.pumpMessages)
        # pump_thread.start()

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
            
    def adjustRudder(self, angleTo):
        if self.currentTarget:
            #adjust rudder for best wind
            #angleTo = gps.angleTo(self.currentTarget)
            
            d_angle = angleTo - self.gps.track_angle_deg

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

    def mainLoop(self):
        while True:
            self.readMessages()

            if not manualControl:
                if not self.currentTarget:
                    if self.targets != []:
                        self.currentTarget = self.targets.pop(0)    
                if self.currentTarget:
                    self.goToGPS(self.currentTarget[0], self.currentTarget[1])
            

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

                elif ary[0] == "manual":
                    if ary[1] == '1' or ary[1].lower() == 'true':
                        self.manualControl = True
                    else:
                        self.manualControl = False

                elif ary[0] == 'addTarget':
                    self.targets.append((self.gps.latitude, self.gps.longitude))

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


    def goToGPS(self, lat, long):

        self.gps.updategps()
        while self.gps.latitude == None or self.gps.longitude == None:
            print("no gps")
            self.gps.updategps()
            sleep(1)

        
        compassAngle = self.compass.angle
        deltaAngle = boatMath.angleToPoint(compassAngle, self.gps.latitude, self.gps.longitude, lat, long)
        targetAngle = (compassAngle + deltaAngle) % 360
        windAngle = self.windvane.angle
        if (deltaAngle + windAngle)%360 < self.windvane.noGoMin and (deltaAngle + windAngle)%360 > self.windvane.noGoMax:
            #turn to target
            #print("case1", targetAngle, compassAngle, windAngle, deltaAngle)
            self.turnToAngle(targetAngle)
        else:
            #print("case2", compassAngle, targetAngle, windAngle, deltaAngle)
            if (targetAngle - compassAngle) % 360 <= 180:
                #turn left
                self.turnToAngle(self.windvane.noGoMin)
            else:
                #turn right
                self.turnToAngle(self.windvane.noGoMax)

        if abs(boatMath.distanceInMBetweenEarthCoordinates(lat, long, self.gps.latitude, self.gps.longitude)) < 5:
            if self.cycleTargets:
                self.targets.append((lat,long))
            self.currentTarget = None
            
    def turnToAngle(self, angle):
        leftPositive = -1 #change to negative one if boat is rotating the wrong way
        # if angle > 180:
        #     angle = angle - 360

        logging.info("starting turnToAngle")
        #print("turning to angle", angle)
        compassAngle = self.compass.angle
        while abs(compassAngle - angle) > int(c.config['CONSTANTS']['angle_margin_of_error']):
            #print(int(compassAngleX), int(compassAngleY), int(compassAngleZ), angle)
            compassAngle = self.compass.angle

            if ( (angle - compassAngle) % 360 <= 180): #turn Left
                rudderPos = leftPositive*min(45, 3*abs(compassAngle - angle)) #/c.rotationSmoothingConst)
                #logging.info(F'turning to angle: {angle} from angle: {compassAngle} by turning rudder to {rudderPos}')
                #print("c1:",rudderPos, compassAngle, angle)
                self.adjustRudder(int(rudderPos))
            else: #turn Other way
                rudderPos = -1*leftPositive*min(45, 3*abs(compassAngle - angle)) #/c.rotationSmoothingConst)
                #logging.info(F'turning to angle: {angle} from angle: {compassAngle} by turning rudder to {rudderPos}')
                #print("c2:",rudderPos, compassAngle, angle)
                self.adjustRudder(int(rudderPos))

        logging.info("finished turnToAngle")


if __name__ == "__main__":

    b = boat()
    b.goToGPS(40.44368167, -79.9580000)


