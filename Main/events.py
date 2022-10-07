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
            self.Search()
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


    def Search(self):
        print("Search moment")
        

if __name__ == "__main__":
    eevee = events()
    while True:
        inp = input("Mode Test: ") # Taking input from user
        eevee.testloop(inp)

