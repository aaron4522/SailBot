import constants as c
import logging
import boatMath
import math

try:
    from windvane import windVane
    from GPS import gps
    from compass import compass
    import GPS
    from camera import camera

    from drivers import driver
    from transceiver import arduino
except Exception as e:
    print("Failed to import some modules, if this is not a simulation fix this before continuing")
    print(F"Exception raised: {e}")
from datetime import date, datetime
from threading import Thread
from time import sleep

import numpy



class events():

    def __init__(self):
        print("init")

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
            buoy_lat = input("buoy_lat: ") # Taking input from user
            buoy_long = input("buoy_long: ") # Taking input from user
            radius = input("radius: ") # Taking input from user
            self.Search(buoy_lat, buoy_long, radius)
        else:
            print("nah")


    #include in automation event code's main loop:
        #self.readmessages to see if it switches modes or RC commands, returning/break if another mode is true
        #self.sendData() to export data

    def Collision_Avoidance(self):
        print("Collision_Avoidance moment")


    def Percision_Navigation(self):
        print("Percision_Navigation moment")

    
    def Endurance(self):
        print("Endurance moment")


    def Station_Keeping(self):
        print("Station_Keeping moment")


    def Search(self, buoy_lat, buoy_long, radius):
        #going to have to request buoylat, buoylong somehow

        self.search_pattern(gps_lat, gps_long, buoy_lat, buoy_long, radius)
        
    
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

        

if __name__ == "__main__":
    eevee = events()
    while True:
        inp = input("Mode Test: ") # Taking input from user
        eevee.testloop(inp)

