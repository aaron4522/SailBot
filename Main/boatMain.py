
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
        logging.basicConfig(level=logging.INFO, filename='boatMainLog.log', filemode='a',
                            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        self.gps = GPS.gps()
        self.compass = compass()
        self.windvane = windVane()
        self.drivers = driver()
        self.arduino = arduino(c.config['MAIN']['ardu_port'])

        self.manualControl = True   # check RC Mode to change manualControl, and manualControl checks for everything else (faster on memory)
        self.cycleTargets = False
        self.currentTarget = None  # (longitude, latitude) tuple
        self.targets = []  # holds (longitude, latitude) tuples

        self.targetSail = 0
        self.currentSail = 0
        self.targetRudder = 0
        self.currentRudder = 0

        noGoZoneDegs = 20

        tempTarget = False

        #self.override = False   #whether to automatically switch to RC when inputting manual commands or prevent the commands
        #self.MODE_SETTING = c.config['MODES']['MOD_RC']

        self.mainLoop()
        # pump_thread = Thread(target=self.pumpMessages)
        # pump_thread.start()

    def move(self):
        """
        Old Code, use goToGPS instead

        """
        if self.gps.distanceTo(currentTarget) < float(c.config['MAIN']['acceptable_range']) and len(self.targets) > 0:
            # next target

            targetAngle = TargetAngleRelativeToNorth()  # Func doesnt exist yet

            windAngleRelativeToNorth = convertWindAngle(self.windVane.angle)

            if tempTarget == False and targetAngle - windAngleRelativeToNorth < (noGoZoneDegs / 2):
                if targetAngle < windAngleRelativeToNorth or abs(targetAngle - 360) < windAngleRelativeToNorth:
                    # newTargetAngle < targetangle
                    newTargetAngle = windAngleRelativeToNorth - (noGoZoneDegs / 2 + 10)
                else:
                    # newTargetAngle > targetAngle
                    newTargetAngle = windAngleRelativeToNorth + (noGoZoneDegs / 2 + 10)

                tempTarget = True
                rotateToAngle(newTargetAngle)
                logging.info('Heading to temp target at: %d', newTargetAngle)

            elif tempTarget and targetAngle - windAngleRelativeToNorth > (noGoZoneDegs / 2):
                tempTarget = False
                logging.info('Heading to target at: %d', targetAngle)
                rotateToAngle(targetAngle)

            elif tempTarget == False:
                logging.info('Heading to target at: %d', targetAngle)
                rotateToAngle(targetAngle)

            # else:
            #     self.currentTarget = self.targets.pop(0)

        else:
            # move towards target
            self.adjustSail()
            self.adjustRudder()

    def adjustSail(self, angle=None):
        if self.manualControl and angle != None:
            self.drivers.sail.set(angle)
            logging.info(F"Adjusted Sail to: {angle} as requested by manual command")
        elif self.currentTarget or self.manualControl:
            windDir = self.windvane.angle
            targetAngle = windDir + 35
            self.drivers.sail.set(targetAngle)
            self.currentSail = targetAngle
            logging.info('Adjusted sail to: %d', targetAngle)

        else:
            # move sail to home position
            self.drivers.sail.set(0)
            self.currentSail = 0
            logging.info('Adjusted sail to home position')

    def adjustRudder(self, angleTo):
        if self.currentTarget or self.manualControl == True:
            # adjust rudder for best wind
            # angleTo = gps.angleTo(self.currentTarget)

            d_angle = angleTo - self.gps.track_angle_deg

            if d_angle > 180: d_angle -= 180

            self.drivers.rudder.set(d_angle)
            self.currentRudder = d_angle
            logging.info('Adjusted rudder to: %d', d_angle)

        else:
            # move sail to home position
            self.drivers.rudder.set(0)
            self.currentRudder = 0
            logging.info('Adjusted rudder to home position')

    def pumpMessages(self):
        while True:
            self.readMessages()

    def mainLoop(self):
        sailStep = 10
        rudderStep = 2
        while True:
            self.readMessages()

                #include in automation code's main loop:
                    #self.readmessages to see if it switches modes or RC commands, returning if another mode is true
                    #self.pumpMessages to export data

            if self.manualControl:
                #adjust sail and rudder to set targets
                if self.currentSail - sailStep > self.targetSail:
                    self.adjustSail(self.targetSail + sailStep)
                elif self.currentSail + sailStep < self.targetSail:
                    self.adjustSail(self.targetSail - sailStep)
                else:
                    self.adjustSail(self.targetSail)

                if self.currentRudder - rudderStep > self.targetRudder:
                    self.adjustRudder(self.targetRudder + rudderStep)
                elif self.currentRudder + sailRudder < self.targetRudder:
                    self.adjustRudder(self.targetRudder - rudderStep)
                else:
                    self.adjustRudder(self.targetRudder)

                self.arduino.send(F"R{self.currentRudder}")
                self.arduino.send(F"S{self.currentSail}")

            if not self.manualControl:  #automation
                if self.MODE_SETTING == c.config['MODES']['MOD_COLLISION_AVOID']:
                    logging.info("Received message to Automate: COLLISION_AVOIDANCE")
                    #collision_avoidance()
                elif self.MODE_SETTING == c.config['MODES']['MOD_PRECISION_NAVIGATE']:
                    logging.info("Received message to Automate: PRECISION_NAVIGATE")
                    #precision_navigate()
                elif self.MODE_SETTING == c.config['MODES']['MOD_ENDURANCE']:
                    logging.info("Received message to Automate: ENDURANCE")
                    #endurance()
                elif self.MODE_SETTING == c.config['MODES']['MOD_STATION_KEEPING']:
                    logging.info("Received message to Automate: STATION_KEEPING")
                    #station_keeping()
                elif self.MODE_SETTING == c.config['MODES']['MOD_SEARCH']:
                    logging.info("Received message to Automate: SEARCH")
                    #search()

                if not self.currentTarget:
                    if self.targets != []:
                        self.currentTarget = self.targets.pop(0)
                    else:
                        print('no targets')
                if self.currentTarget:
                    self.goToGPS(self.currentTarget[0], self.currentTarget[1])


    def readMessages(self):
        msgs = self.arduino.read()[:-3].replace('\n', '')
        print(msgs)

        # for msg in msgs:
        try:
            msg = msgs
            ary = msg.split(' ')
            processed = False

            #make it so you cant do manual commands unless in RC mode to avoid automation undoing work done
            #override is in place to switch to RC if given RC commands if potential accidents may happen
            if len(ary) > 0:
                    # manual adjust sail
                if ary[0] == 'sail':
                    if self.override:
                        logging.info("OVERRIDE: Switching to RC")
                        self.MODE_SETTING = c.config['MODES']['MOD_RC']
                        self.manualControl = True

                    if self.manualControl:  #faster
                        logging.info(F'Received message to adjust sail to {float(ary[1])}')
                        #self.adjustSail(float(ary[1]))
                        self.targetSail = float(ary[1])
                        processed = True
                    else:
                        logging.info("Refuse to change sail, not in RC Mode")

                    #manual adjust rudder
                elif ary[0] == 'rudder':
                    if self.override:
                        logging.info("OVERRIDE: Switching to RC")
                        self.MODE_SETTING = c.config['MODES']['MOD_RC']
                        self.manualControl = True

                    if self.manualControl:  #faster
                        logging.info(F'Received message to adjust rudder to {float(ary[1])}')
                        self.adjustRudder(float(ary[1]))
                        self.targetRudder = float(ary[1])
                        processed = True
                    else:
                        logging.info("Refuse to change sail, not in RC Mode")


                elif ary[0] == 'override':
                    self.override = not self.override
                    processed = True


                elif ary[0] == 'mode':
                    try:
                        if int(ary[1]) < 0 or int(ary[1]) > 5:
                            logging.info("Outside mode range")
                        else:
                            self.MODE_SETTING = int(ary[1])
                            logging.info(F'Setting mode to {int(ary[1])}')
                            processed = True
                    except Exception as e:
                        print(F"Error changing mode: {e}")
                        logging.info(F"Error changing mode: {e}")

                    if self.MODE_SETTING == c.config['MODES']['MOD_RC']:
                        logging.info("Setting manual mode to True")
                        self.manualControl = True
                    else:
                        logging.info("Setting manual mode to False")
                        self.manualControl = False

                    #redundent if RC is changing it
                #elif ary[0] == "manual":
                #    if ary[1] == '1' or ary[1].lower() == 'true':
                #        logging.info("set manual mode to True")
                #        self.manualControl = True
                #    else:
                #        logging.info("set manual mode to False")
                #        self.manualControl = False

                elif ary[0] == 'addTarget':
                    # print('adding target')
                    while self.gps.latitude == None or self.gps.longitude == None:
                        print("no gps")
                        self.gps.updategps()
                        sleep(.1)
                    target = (self.gps.latitude, self.gps.longitude)
                    logging.info(F"added Target at {target}")
                    self.targets.append(target)
                    print(f"added target, current target list is {self.targets}")
                    processed = True
                elif ary[0] != '':
                    print(f'unknown command {ary[0]}')
            if processed:
                    pass
                    #self.arduino.send("boat probably processed message")

        except Exception as e:
            logging.info(f"failed to read command {msgs}")
            print(f"message error: {e}")



    def goBetweenBuoy(self, LeftBuoyPixel, RightBuoyPixel):
        # Both in camera, assuming arguments = none if not in camera
        if LeftBuoyPixel and RightBuoyPixel:
            # Find distance of buoys to center line
            # TODO Add the total camera pixel size to constants (x,y)
            # Thought it only x distance needs to be checked
            distLeft = abs(LeftBuoyPixel[1] - c.cameraPixelSizeX / 2.0)
            distRight = abs(RightBuoyPixel[1] - c.cameraPixelSizeX / 2.0)

            # Check if one is significantly closer to center
            # TODO determine pixel wise what is significantly closer
            if distRight - distLeft > 20:  # Left buoy is closer
                # Turn right
                newCompassAngle = (self.compass.mag + 10) % 360
                self.turnToAngle(newCompassAngle)
            elif distLeft - distRight > 20:  # Right buoy closer
                # Turn left
                newCompassAngle = (self.compass.mag - 10) % 360
                self.turnToAngle(newCompassAngle)
        else:
            # Go to gps
            self.goToGps(self.currentTarget[0], self.currentTarget[1])

    def goToGPS(self, lat, long):
        print(F'going to {lat}, {long}')
        self.gps.updategps()
        while self.gps.latitude == None or self.gps.longitude == None:
            print("no gps")
            self.gps.updategps()
            sleep(.1)

        compassAngle = self.compass.angle
        deltaAngle = boatMath.angleToPoint(compassAngle, self.gps.latitude, self.gps.longitude, lat, long)
        targetAngle = (compassAngle + deltaAngle) % 360
        windAngle = self.windvane.angle
        if (deltaAngle + windAngle) % 360 < self.windvane.noGoMin and (
                deltaAngle + windAngle) % 360 > self.windvane.noGoMax:
            # turn to target
            print("case1", targetAngle, compassAngle, windAngle, deltaAngle)
            self.turnToAngle(targetAngle)
        else:
            print("case2", compassAngle, targetAngle, windAngle, deltaAngle)
            if (targetAngle - compassAngle) % 360 <= 180:
                # turn left
                self.turnToAngle(self.windvane.noGoMin)
            else:
                # turn right
                self.turnToAngle(self.windvane.noGoMax)

        if abs(boatMath.distanceInMBetweenEarthCoordinates(lat, long, self.gps.latitude, self.gps.longitude)) < 5:
            if self.cycleTargets:
                self.targets.append((lat, long))
            self.currentTarget = None
            self.adjustRudder(0)

    def turnToAngle(self, angle):
        leftPositive = -1  # change to negative one if boat is rotating the wrong way
        # if angle > 180:
        #     angle = angle - 360

        logging.info("starting turnToAngle")
        # print("turning to angle", angle)
        compassAngle = self.compass.angle
        while abs(compassAngle - angle) > int(c.config['CONSTANTS']['angle_margin_of_error']):
            # print(int(compassAngleX), int(compassAngleY), int(compassAngleZ), angle)
            compassAngle = self.compass.angle

            print(compassAngle)
            if ((angle - compassAngle) % 360 <= 180):  # turn Left
                rudderPos = leftPositive * min(45, 3 * abs(compassAngle - angle))  # /c.rotationSmoothingConst)
                # logging.info(F'turning to angle: {angle} from angle: {compassAngle} by turning rudder to {rudderPos}')
                # print("c1:",rudderPos, compassAngle, angle)
                self.adjustRudder(int(rudderPos))
            else:  # turn Other way
                rudderPos = -1 * leftPositive * min(45, 3 * abs(compassAngle - angle))  # /c.rotationSmoothingConst)
                # logging.info(F'turning to angle: {angle} from angle: {compassAngle} by turning rudder to {rudderPos}')
                # print("c2:",rudderPos, compassAngle, angle)
                self.adjustRudder(int(rudderPos))

        print(compassAngle)
        logging.info("finished turnToAngle")


if __name__ == "__main__":
    b = boat()
    try:
        b.mainLoop()
        # b.turnToAngle(90)
        # b.goToGPS(40.44368167, -79.9580000)
        print("Cleaning Up")
        b.adjustRudder(0)
        b.adjustSail(0)
    except KeyboardInterrupt as e:
        print("\n\nEXITING...\n\n")
        b.adjustRudder(0)
        b.adjustSail(0)
        print("EXITED CLEANLY")


