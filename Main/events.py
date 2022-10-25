import constants as c
import logging
import math

try:
    from windvane import windVane
    from GPS import gps
    from compass import compass
    import GPS
    from camera import camera

    from drivers import driver
    from transceiver import arduino

    from boatMain import boat
except Exception as e:
    print("Failed to import some modules, if this is not a simulation fix this before continuing")
    print(F"Exception raised: {e}")
from datetime import date, datetime
from threading import Thread
from time import sleep



class events(boat):

    def __init__(self):
        self.MESSAGE = None
        print("init")


    def event_NL(self):
        # Nice loop to put in event functions
        #   - sends data about boat
        #   - reads messages and returns bool
        #     if need to stop doing the command (0:no, 1:YES STOP)
        ret = False

        # READ MESSAGE SECTION =========
        self.MESSAGE = self.arduino.readData() #update read
        print("events:", self.MESSAGE)
            # for msg in msgs:
        try:
            for msg in self.MESSAGE:
                ary = msg.split(" ")
                if len(ary) > 0:
                    if ary[0] == 'sail' or ary[0] == "S":
                        ret = True

                    elif ary[0] == 'rudder' or ary[0] == "R":
                        ret = True

                    elif ary[0] == 'mode' and boat.MODE_SETTING != ary[1]:
                        ret = True
        except Exception as e:
            logging.info(f"failed to read command {self.MESSAGE}")
            print(f"message error: {e}")
        
        boat.readMessages(self.MESSAGE) #override message to make faster

        # SEND MESSAGE SECTION =========
        boat.sendData()

        return ret


    def testloop(self, inp):
        if inp == "CA":
            self.Collision_Avoidance()
        elif inp == "PN":
            self.Percision_Navigation()
        elif inp == "E":
            self.Endurance()
        elif inp == "SK":
            self.Station_Keeping()
        elif inp == "S":
                # very temp inputs
            buoy_lat = input("buoy_lat: ") # Taking input from user
            buoy_long = input("buoy_long: ") # Taking input from user
            radius = input("radius: ") # Taking input from user
            self.Search(buoy_lat, buoy_long, radius)
        else:
            print("nah")


    #include in automation event code's main loop:
        #self.readmessages to see if it switches modes or RC commands, returning/break if another mode is true
        #self.sendData() to export data

    #inputs: B1,B2,B3,B4 long/lat
    #arr: [B1x,B1y, etc]
    def Collision_Avoidance(self,arr):
        print("Collision_Avoidance moment")

        if self.event_NL(): return

    #inputs: B1,B2,B3,B4 long/lat
    #arr: [B1x,B1y, etc]
    def Percision_Navigation(self,arr):
        print("Percision_Navigation moment")

        if self.event_NL(): return

    #inputs: B1,B2,B3,B4 long/lat
    #arr: [B1x,B1y, etc]
    def Endurance(self,arr):
        print("Endurance moment")

        if self.event_NL(): return

    #inputs: B1,B2 long/lat
    #arr: [B1x,B1y, etc]
    def Station_Keeping(self,arr):
        print("Station_Keeping moment")

        if self.event_NL(): return

    #inputs: B1 long/lat, Radius
    def Search(self, buoy_lat, buoy_long, radius):
        #make in boatMain along with mode switch, attach buoy coords and radius in ary
        #will need to redo GUI then ://////
        while(True):
            self.search_pattern(boat.gps.latitude, boat.gps.longitude, buoy_lat, buoy_long, radius)

            if self.event_NL(): return
        
    
    def search_pattern(self, gps_lat, gps_long, buoy_lat, buoy_long, radius):
        #find five coords via search pattern
        #in realtion to current pos and buoy rad center pos

        a = gps_lat - buoy_lat
        b = gps_long - buoy_long
        ang = math.atan(b/a)
        ang *= 180/math.pi

        if(a<0):    ang += 180

        tar_angs = [ang,ang+72,ang-72,ang-(72*3),ang-(72*2)]
        tarx = [0] * 5
        tary = [0] * 5

        for i in range(0,5):
            tarx[i] =  buoy_lat  + radius*math.cos( tar_angs[i] * (math.pi/180) )
            tary[i] =  buoy_long + radius*math.sin( tar_angs[i] * (math.pi/180) )
        
        arr = [tarx,tary]
        return arr

        

if __name__ == "__main__":
    eevee = events()
    while True:
        inp = input("Mode Test: ") # Taking input from user
        eevee.testloop(inp)

