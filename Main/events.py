from curses import KEY_B2
import constants as c
import logging
import math
import time

try:
    from windvane import windVane
    from GPS import gps
    from compass import compass
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
        self.totalError = 0.0
        self.oldError = 0.0
        self.oldTime = time.time()


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

                    elif ary[0] == 'mode' and ary[1] == 0:
                        ret = True
        except Exception as e:
            logging.info(f"failed to read command {self.MESSAGE}")
            print(f"message error: {e}")
        
        boat.readMessages(self.MESSAGE) #override message to make faster

        # SEND MESSAGE SECTION =========
        boat.sendData()

        # New PID stuff
        if (time.time() - self.oldTime < 100):  # Only runs every tenth of a second #new
            # Finds the angle the boat should take
            error = boat.targetAngle - boat.compass.angle  # Finds how far off the boat is from its goal
            self.totalError += error  # Gets the total error to be used for the integral gain
            derivativeError = (error - self.oldError) / (
                        time.time() - self.oldtime)  # Gets the change in error for the derivative portion
            deltaAngle = c.config['CONSTANTS']["P"] * error + c.config['CONSTANTS']["I"] * self.totalError + c.config['CONSTANTS']["D"] * derivativeError  # Finds the angle the boat should be going

            # Translates the angle into lat and log so goToGPS won't ignore it
            boat.currentAngle = getCoordinateADistanceAlongAngle(1000, deltaAngle + boat.compass.angle)

            # Resets the variable
            self.oldTime = time.time()
            self.oldError = error


        return ret


    def testloop(self, inp):
        t_inp = input("inputs: ")
        t_arr = t_inp.split(" ")
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


    #===================================================================================
    #inputs: B1,B2,B3,B4 long/lat
    #arr: [B1x,B1y, etc] (boat.event_arr)
    def Collision_Avoidance(self):
        print("Collision_Avoidance moment")
        #Challenge	Goal:
            #Demonstrate a successful autonomous collision avoidance system.
        #Description:
            #The boat will start between two buoys
            #will sail autonomously on a reach to another buoy and return
            #Sometime during the trip, a manned boat will approach on a collision course
            #RC is not permitted after the start.
        #Scoring:
            #10 pts max
            #7 pts if the boat responds but a collision still occurs
            #2 pt deduction if the respective buoy(s) are not reached following the avoidance maneuver
            #3 pts max by alternative dry-land demo of appropriate sensor/rudder interaction.
        #assumptions: (based on guidelines)
            #left of start direction is upstream
            #going back is harder

        while(True):
            #main running
                #blah blah blah


            if self.event_NL(): return  #checks if mode has switched, exits func if so


    #===================================================================================
    #inputs: B1,B2,B3,B4 long/lat
    #TL[0,1],TR[2,3],BL[4,5],BR[6,7] (left/right top, left/right bottom)
    #arr: [B1x,B1y, etc] (boat.event_arr)
    def Percision_Navigation(self):     #Jonah
        print("Percision_Navigation moment")
        #Challenge	Goal:
            #To demonstrate the boat’s ability to autonomously navigate a course within tight tolerances.
        #Description:
            #The boat will start between two buoys
            #then will autonomously sail a course around two buoys
            #then return between the two start buoys
        #Scoring:
            #10 pts max
            #2 pts/each for rounding the first two buoys
            #6 pts more for finishing between the start buoys
            #or 4 pts more for crossing the line outside of the start buoys.
        #assumptions: (based on guidelines)
            #behind start is upstream
            #going back is harder
        
        self.ifsideways = None; self.ifupsidedown = None    #set up for later PN_checkwayside

        self.PN_arr = []
        self.PN_arr = self.PN_coords()

        self.rev_bool = False
        self.target_set = 1
        start_time = time.time()
        while(True):
            #return checks
                ##changed modes
            if self.event_NL(): return  #checks if mode has switched, exits func if so
                #time based check
            curr_time = time.time()
            if int(curr_time - start_time)%4 != 0: continue #off-set the set GPS 
                #set check
            if self.target_set >=int( len(self.PN_arr)/2): 
                logging.info(f"PN: REACHED FINAL POINT;\nEXITING EVENT")
                print(f"Finished Perc Nav")
                return

            #main running: go to points in PN_arr
            #TODO:
                #[x]track which coord set in PN_arr needs to go to
                #[x]find if it passes, go to next set
                #[x]wait small period between keep setting it
                #[x]2i,2i+1
            logging.info(f"PN: CURR TARGET POINT: {self.target_set}")
            print(f"Current target point: {self.target_set}")

            if self.PN_PassCheck():
                logging.info(f"PN: PASSED TARGET POINT: {self.target_set}")
                print(f"Passed target point: {self.target_set}")
                self.target_set += 1
            boat.goToGPS(self.target_set*2,self.target_set*2 +1)
            
    
    #find coords that shoudl go to via cart of buoy coords
    def PN_coords(self):

        #adjustable values
        rad1 = 4    #inner rad
        rad2 = 8    #outer rad
        m1= 45; m2= -15 #rad offset from 90 and 225/-45 points
                        #see desmos: https://www.desmos.com/calculator/2fjqthukuf

        ret_arr = []
        #pt1= b3 rad1: 90+m1
        #pt2= b3 rad2: 225+m2
        #pt3= between b2 and b4
        #pt4= b4 rad2:315+m2
        #pt5= b4 rad1:90+m1
        #pt6= between b1 and b2

        #calcing x/y points
        t = math.pi/180 #conv deg to rad
        #b3[0-3]
        ret_arr.append( rad1*math.cos(  (90+m1) *t)+boat.event_arr[4] )  #pt1x[0]
        ret_arr.append( rad1*math.sin(  (90+m1) *t)+boat.event_arr[5] )  #pt1y[1]
        ret_arr.append( rad2*math.cos( (225+m2) *t)+boat.event_arr[4] )  #pt2x[2]
        ret_arr.append( rad2*math.sin( (225+m2) *t)+boat.event_arr[5] )  #pt2y[3]

        #b3/4[4-5]
        ret_arr.append( (boat.event_arr[4]+boat.event_arr[6])/2 )  #pt3x[4]
        ret_arr.append( (boat.event_arr[5]+boat.event_arr[7])/2 )  #pt3y[5]

        #b4[6-9]
        ret_arr.append( rad2*math.cos( (315-m2) *t)+boat.event_arr[6] )  #pt4x[6]
        ret_arr.append( rad2*math.sin( (315-m2) *t)+boat.event_arr[7] )  #pt4y[7]
        ret_arr.append( rad1*math.cos(  (90-m1) *t)+boat.event_arr[6] )  #pt5x[8]
        ret_arr.append( rad1*math.sin(  (90-m1) *t)+boat.event_arr[7] )  #pt5y[9]

        #b1/2[10-11]
        ret_arr.append( (boat.event_arr[0]+boat.event_arr[2])/2 )  #pt6x[10]
        ret_arr.append( (boat.event_arr[1]+boat.event_arr[3])/2 )  #pt6y[11]

        return ret_arr

    #find if passed target (ret bool)
    def PN_PassCheck(self):
        #self.target_set,self.PN_arr
        #boat.event_arr

        '''
        #SK_f(x)
        #P1[0-1], boat.event_arr[4-5]
        #P1[2-3], boat.event_arr[4-5]
        #
        #P1[6-7], boat.event_arr[6-7]
        #P1[8-9], boat.event_arr[6-7]
        #boat.event_arr[0-1], boat.event_arr[2-3]

        #pt1: x<P1x[0],    y<L1(x)[ m(P1[0-1],[]) ]
        #pt2: x>P2x[2],    y<L2(x)
        #pt3: x>Perpendicular P2toP4    -(1/m)x+ P[5]-(1/m)*P[6]
        #pt4: x>P4x[6],    y>L4(x)
        #pt5: x<P5x[8],    y>L5(x)
        #pt6: y>L6(x)
        '''

        gps.updategps()
        #boat.gps.longitude
        #boat.gps.latitude

        #TODO:
        #either figure out better system, or put in a 'reverse if' of the next case in each statement to know whether the coords are right
        #Ie: if x<whatever before it starts the next set, check for x>=whatever in the next case
        #mult by a 'rev_bool' decided
        #that really sucks to map out though

        if self.ifupsidedown == None: self.ifupsidedown, self.ifsideways = self.PN_checkwayside() #True=sideways/upsidedown
        #[x_]upsidedown: flip >/<
        #[_x]sideways: flip long/lat
        #00,01,10,11: standard;turn 90deg left for order
        x=False

        #standard------------------------------------------------------------------
        if   not(self.ifupsidedown) and not(self.ifsideways):
            #left(long) of BL buoy[{4},5]
            #below(lat) line between p1[0,1] and BL buoy[4,5]
            if self.target_set == 1:
                x = (boat.gps.longitude <= boat.event_arr[4]
                    and boat.gps.latitude <= self.SK_f( boat.gps.longitude,self.PN_arr[0],self.PN_arr[1],boat.event_arr[4],boat.event_arr[5] ))

            #below(lat) of BL buoy[4,{5}]
            #below(lat) line between p2[2,3] and BL buoy[4,5]
            elif self.target_set == 2:
                x = (boat.gps.latitude <= boat.event_arr[5]
                    and boat.gps.latitude <= self.SK_f( boat.gps.longitude,self.PN_arr[2],self.PN_arr[3],boat.event_arr[4],boat.event_arr[5] ))

            #right(long) of line perpendicular to p2[2,3] and p4[6,7] at p3[4,5]
            elif self.target_set == 3:
                x = boat.gps.longitude >= self.PN_Perpend(boat.gps.longitude,self.PN_arr[4],self.PN_arr[5],self.PN_arr[2],self.PN_arr[3],self.PN_arr[4],self.PN_arr[5])
            
            #right(long) of BR buoy[{6},7]
            #above(lat) line between p4[6,7] and BR buoy[6,7]
            elif self.target_set == 4:
                x = (boat.gps.longitude >= boat.event_arr[6]
                    and boat.gps.latitude >= self.SK_f( boat.gps.longitude,self.PN_arr[6],self.PN_arr[7],boat.event_arr[6],boat.event_arr[7] ))
            
            #above(lat) of BR buoy[6,{7}]
            #above(lat) line between p5[8,9] and BR buoy[6,7]
            elif self.target_set == 5:
                x = (boat.gps.latitude >= boat.event_arr[7]
                    and boat.gps.latitude >= self.SK_f( boat.gps.longitude,self.PN_arr[8],self.PN_arr[9],boat.event_arr[6],boat.event_arr[7] ))

            #above(lat) line between TL[0,1] and TR[2,3]
            elif self.target_set == 6:
                x = boat.gps.latitude >= self.SK_f( boat.gps.longitude,boat.event_arr[0],boat.event_arr[1],boat.event_arr[2],boat.event_arr[3] )
            else:
                logging.info(f"PN: ERROR: 00: TARGET SET OUT OF RANGE (1to6)\nTARGET PNT = {self.target_set}")
                print(f"PN: ERROR: 00: TARGET SET OUT OF RANGE (1to6)\nTARGET PNT = {self.target_set}")

        #flip long/lat------------------------------------------------------------------
        elif not(self.ifupsidedown) and     self.ifsideways:
            #left(long) of BL buoy[{4},5]
            #below(lat) line between p1[0,1] and BL buoy[4,5]
            if self.target_set == 1:
                x = (boat.gps.latitude <= boat.event_arr[4]
                    and boat.gps.longitude <= self.SK_f( boat.gps.latitude,self.PN_arr[0],self.PN_arr[1],boat.event_arr[4],boat.event_arr[5] ))

            #below(lat) of BL buoy[4,{5}]
            #below(lat) line between p2[2,3] and BL buoy[4,5]
            elif self.target_set == 2:
                x = (boat.gps.longitude <= boat.event_arr[5]
                    and boat.gps.longitude <= self.SK_f( boat.gps.latitude,self.PN_arr[2],self.PN_arr[3],boat.event_arr[4],boat.event_arr[5] ))

            #right(long) of line perpendicular to p2[2,3] and p4[6,7] at p3[4,5]
            elif self.target_set == 3:
                x = boat.gps.latitude >= self.PN_Perpend(boat.gps.latitude,self.PN_arr[4],self.PN_arr[5],self.PN_arr[2],self.PN_arr[3],self.PN_arr[4],self.PN_arr[5])
            
            #right(long) of BR buoy[{6},7]
            #above(lat) line between p4[6,7] and BR buoy[6,7]
            elif self.target_set == 4:
                x = (boat.gps.latitude >= boat.event_arr[6]
                    and boat.gps.longitude >= self.SK_f( boat.gps.latitude,self.PN_arr[6],self.PN_arr[7],boat.event_arr[6],boat.event_arr[7] ))
            
            #above(lat) of BR buoy[6,{7}]
            #above(lat) line between p5[8,9] and BR buoy[6,7]
            elif self.target_set == 5:
                x = (boat.gps.longitude >= boat.event_arr[7]
                    and boat.gps.longitude >= self.SK_f( boat.gps.latitude,self.PN_arr[8],self.PN_arr[9],boat.event_arr[6],boat.event_arr[7] ))

            #above(lat) line between TL[0,1] and TR[2,3]
            elif self.target_set == 6:
                x = boat.gps.longitude >= self.SK_f( boat.gps.latitude,boat.event_arr[0],boat.event_arr[1],boat.event_arr[2],boat.event_arr[3] )
            else:
                logging.info(f"PN: ERROR: 00: TARGET SET OUT OF RANGE (1to6)\nTARGET PNT = {self.target_set}")
                print(f"PN: ERROR: 00: TARGET SET OUT OF RANGE (1to6)\nTARGET PNT = {self.target_set}")

        #flip >/<------------------------------------------------------------------
        elif self.ifupsidedown      and not(self.ifsideways):
            #left(long) of BL buoy[{4},5]
            #below(lat) line between p1[0,1] and BL buoy[4,5]
            if self.target_set == 1:
                x = (boat.gps.longitude >= boat.event_arr[4]
                    and boat.gps.latitude >= self.SK_f( boat.gps.longitude,self.PN_arr[0],self.PN_arr[1],boat.event_arr[4],boat.event_arr[5] ))

            #below(lat) of BL buoy[4,{5}]
            #below(lat) line between p2[2,3] and BL buoy[4,5]
            elif self.target_set == 2:
                x = (boat.gps.latitude >= boat.event_arr[5]
                    and boat.gps.latitude >= self.SK_f( boat.gps.longitude,self.PN_arr[2],self.PN_arr[3],boat.event_arr[4],boat.event_arr[5] ))

            #right(long) of line perpendicular to p2[2,3] and p4[6,7] at p3[4,5]
            elif self.target_set == 3:
                x = boat.gps.longitude <= self.PN_Perpend(boat.gps.longitude,self.PN_arr[4],self.PN_arr[5],self.PN_arr[2],self.PN_arr[3],self.PN_arr[4],self.PN_arr[5])
            
            #right(long) of BR buoy[{6},7]
            #above(lat) line between p4[6,7] and BR buoy[6,7]
            elif self.target_set == 4:
                x = (boat.gps.longitude <= boat.event_arr[6]
                    and boat.gps.latitude <= self.SK_f( boat.gps.longitude,self.PN_arr[6],self.PN_arr[7],boat.event_arr[6],boat.event_arr[7] ))
            
            #above(lat) of BR buoy[6,{7}]
            #above(lat) line between p5[8,9] and BR buoy[6,7]
            elif self.target_set == 5:
                x = (boat.gps.latitude <= boat.event_arr[7]
                    and boat.gps.latitude <= self.SK_f( boat.gps.longitude,self.PN_arr[8],self.PN_arr[9],boat.event_arr[6],boat.event_arr[7] ))

            #above(lat) line between TL[0,1] and TR[2,3]
            elif self.target_set == 6:
                x = boat.gps.latitude <= self.SK_f( boat.gps.longitude,boat.event_arr[0],boat.event_arr[1],boat.event_arr[2],boat.event_arr[3] )
            else:
                logging.info(f"PN: ERROR: 00: TARGET SET OUT OF RANGE (1to6)\nTARGET PNT = {self.target_set}")
                print(f"PN: ERROR: 00: TARGET SET OUT OF RANGE (1to6)\nTARGET PNT = {self.target_set}")

        #flip long/lat, flip >/<------------------------------------------------------------------
        elif self.ifupsidedown      and     self.ifsideways:
            #left(long) of BL buoy[{4},5]
            #below(lat) line between p1[0,1] and BL buoy[4,5]
            if self.target_set == 1:
                x = (boat.gps.latitude >= boat.event_arr[4]
                    and boat.gps.longitude >= self.SK_f( boat.gps.latitude,self.PN_arr[0],self.PN_arr[1],boat.event_arr[4],boat.event_arr[5] ))

            #below(lat) of BL buoy[4,{5}]
            #below(lat) line between p2[2,3] and BL buoy[4,5]
            elif self.target_set == 2:
                x = (boat.gps.longitude >= boat.event_arr[5]
                    and boat.gps.longitude >= self.SK_f( boat.gps.latitude,self.PN_arr[2],self.PN_arr[3],boat.event_arr[4],boat.event_arr[5] ))

            #right(long) of line perpendicular to p2[2,3] and p4[6,7] at p3[4,5]
            elif self.target_set == 3:
                x = boat.gps.latitude <= self.PN_Perpend(boat.gps.latitude,self.PN_arr[4],self.PN_arr[5],self.PN_arr[2],self.PN_arr[3],self.PN_arr[4],self.PN_arr[5])
            
            #right(long) of BR buoy[{6},7]
            #above(lat) line between p4[6,7] and BR buoy[6,7]
            elif self.target_set == 4:
                x = (boat.gps.latitude <= boat.event_arr[6]
                    and boat.gps.longitude <= self.SK_f( boat.gps.latitude,self.PN_arr[6],self.PN_arr[7],boat.event_arr[6],boat.event_arr[7] ))
            
            #above(lat) of BR buoy[6,{7}]
            #above(lat) line between p5[8,9] and BR buoy[6,7]
            elif self.target_set == 5:
                x = (boat.gps.longitude <= boat.event_arr[7]
                    and boat.gps.longitude <= self.SK_f( boat.gps.latitude,self.PN_arr[8],self.PN_arr[9],boat.event_arr[6],boat.event_arr[7] ))

            #above(lat) line between TL[0,1] and TR[2,3]
            elif self.target_set == 6:
                x = boat.gps.longitude <= self.SK_f( boat.gps.latitude,boat.event_arr[0],boat.event_arr[1],boat.event_arr[2],boat.event_arr[3] )
            else:
                logging.info(f"PN: ERROR: 00: TARGET SET OUT OF RANGE (1to6)\nTARGET PNT = {self.target_set}")
                print(f"PN: ERROR: 00: TARGET SET OUT OF RANGE (1to6)\nTARGET PNT = {self.target_set}")
        

        return x

    def PN_Perpend(self,x,c1,c2,a1,b1,a2,b2):
        #f(x) = y of line perpendicular to SK_f(a1,b1,a2,b2)

        #x:input
        #c1/c2:mid x/y
        #a1/b1:point1
        #a2/b2:point2

        #m= -m0^-1
        #v= c2-m0*c1
        m = -1/self.SK_m(a1,b1,a2,b2)
        v = c2 - m*c1
        return m*x+v

    def PN_checkwayside(self):
        #check if sideways or upsidedown
        #[!!!!!]return self.ifupsidedown,self.ifsideways
        #boat.event_arr
        #PN_arr
        '''
        1:rightways [standard]
        2:90deg  right
        3:180deg upsidedown
        4:90deg  left

        [4,5][10,11]
        not sideways(1/3): 3>&6< 45deg line(p3/p6)  [same, keep]
        sideways(2/4     : 3>&6< 45deg line(p3/p6)  [change long/lat asks]

        rightside up(1/2)   [same, keep]
        1:p3y<p6y
        2:p3x<p6x
        upside down(3/4)    [change >&<]
        1:p3y>p6y
        2:p3x>p6x
        '''

        if abs( self.SK_m(self.PN_arr[4],self.PN_arr[5],self.PN_arr[10],self.PN_arr[11]) ) <1:  a=True  #sideways
        else: a=False

        if a:   #sideways
            if self.PN_arr[4] > self.PN_arr[10]: b=True    #upsidedown
            else: b=False   #rightside up
        else:   #rightways
            if self.PN_arr[5] > self.PN_arr[11]: b=True    #upsidedown
            else: b=False   #rightside up

        return b,a  #changed for bool table reasons to b,a


    #===================================================================================
    #inputs: B1,B2,B3,B4 long/lat
    #arr: [B1x,B1y, etc] (boat.event_arr)
    def Endurance(self):
        print("Endurance moment")
        #Challenge	Goal:
            #To demonstrate the boat’s durability and capability to sail some distance
        #Description:
            #The boats will sail around 4 buoys (passing within 10 m inside of buoy is OK) for up to 7 hours
        #Scoring:
            #10 pts max
            #1 pt for each 1NM lap completed autonomously (1/2 pt/lap if RC is used at any point during the lap*)
            #An additional 1pt for each continuous (no pit-stop) hr sailed; up to 6 pts
            #At least one lap must be completed to earn points
            #All boats must start each subsequent lap at the Start line following a pit stop or support boat rescue. (*No penalty for momentary RC to avoid collisions.)
        #assumptions: (based on guidelines)
            #left of start direction is upstream


        gps.updategps()
        print(gps.latitude)

        while(True):
            #main running
                #blah blah blah


            if self.event_NL(): return  #checks if mode has switched, exits func if so


    #===================================================================================
    #inputs: B1,B2,B3,B4 long/lat
    #TL,TR,BL,BR
    #arr: [B1x,B1y, etc] (boat.event_arr)
    def Station_Keeping(self):          #Jonah
        print("Station_Keeping moment")
        #Challenge	Goal:
            #To	demonstrate	the	ability	of the boat to remain close to one position and respond to time-based commands.	
        #Description:
            #The boat will enter a 40 x 40m box and attempt to stay inside the box for 5 minutes.
            #It must then exit within 30 seconds to avoid a penalty.
        #Scoring:
            #10	pts	max.
            #2 pts per minute within the box during the 5 minute test (the boat may exit and reenter multiple times).
            #2 pts per minute will be deducted for time within the box after 5½ minutes.	
            #The final score will be reduced by 50% if any RC is preformed from the start of the 5 minute event	until the boat’s final exit.
            #The final score will be to X.X precision
        #assumptions: (based on guidelines)
            #front is upstream


        #see SK_perc_guide() notes on calculating go-to points
        #running:
        #1.) wait till fall behind 80%
        #2.) sail to 90%, until at 90%
        #3.) set sail flat
        #4.) if behind 75%, go to step 2, repeat
        #5.) GTFO (find&sail to best point) after time limit
            #DO NOT JUST DROP SAIL
                #how we won event first time was dropping sail
                #and floating from front to end for total of 5 minute duration travel
        time_perc = 5*60 * (70/100) #time to leave, 5 minute limit * %


        type_arr =   [ 0, 0, 0, 1]
        wanted_arr = [80,75,90,90]
        cool_arr = self.SK_perc_guide(wanted_arr,type_arr,boat.event_arr)
        del type_arr, wanted_arr
            #(0,1)80-line,      (2,3)75-line,
            #(4,5)90-line,      (6,7)90-point,

            #[always auto put on end]:
            #(8,9)Front-line            (here cause of cart_perimiter_scan)
            #(10,11)Left-line,  (12,13)Right-line
            #(14,15)Back-line
            #(16) mid m line for line check

        start = True#; moving = False
        targ_x = None#; targ_y = None
        skip = False
            #gotoGPS just sets it on course, not till it goes there
        #=== main running ===
        #line check is a long process, so instead of checking both
        #DEPRICATED:uses mutual exclusion so not continiously moving to same point (moving bool)
            #gotoGPS just sets it on course, not till it goes there

        #time calc
        start_time = time.time()

        while(True):
            #return checks
                #changed modes
            if self.event_NL(): return  #checks if mode has switched, exits func if so

                #time based checks
            curr_time = time.time()
            if int(curr_time - start_time)%4 != 0: continue #off-set the set GPS 

                #gtfo
            if skip or curr_time - start_time >= time_perc:
                #find best point to leave:
                if targ_x == None:
                    skip = True #faster if statement
                    targ_x, targ_y = self.cart_perimiter_scan(cool_arr[-7:-1])    #i thought the name sounded cool

                #TODO: when to stop????
                    #using past line depending
                    #using side/back-line that the shortest on intersected at and using SK_line_check with front instead of back
                        #return another var in cart_perimiter_scan, str, ("B","L","R")
                        #or si (var from cart_perimiter_scan)
                    #maybe break to go to another loop after this one, checking it doesnt crash?
                    #[!!!!!]might also just not have too as: as soon as you leave after the timelimit, the event is over and we can switch to manual
                boat.goToGPS(targ_x,targ_y)
                '''
                stall = False
                while(not self.SK_line_check(uhh_idk_something)): stall=True
                '''
                continue
            
                #if not in box
                #ordered in certain way of most importance, handle up/down first before too left or right
                #also put before time because then it doesnt matter cause it's already out
            #past front
            if not( self.SK_line_check(cool_arr[-9:-7], cool_arr[-3:-1],cool_arr[-1]) ):
                logging.info("too forward")
                #loosen sail, do nuthin; drift
                boat.adjustSail(90)
                continue
            
            #past bot
            elif not( self.SK_line_check(cool_arr[-3:-1], cool_arr[-9:-7],cool_arr[-1]) ):
                logging.info("too back")
                #go to 90
                boat.goToGPS(cool_arr[6],cool_arr[7])
                continue
            
            #past left
            elif not( self.SK_line_check(cool_arr[-7:-5], cool_arr[-5:-3],cool_arr[-1]) ):
                logging.info("too left")
                #find/go-to intersect of line (+)35degrees of wind direction to left line
                #mini cart scan
                t_x, t_y = self.mini_cart_permititer_scan(cool_arr[-7:-5],"L")
                boat.goToGPS(t_x, t_y)
                continue

            #past right
            elif not( self.SK_line_check(cool_arr[-5:-3], cool_arr[-7:-5],cool_arr[-1]) ):
                logging.info("too right")
                #find/go-to intersect of line (-)35degrees of wind direction to left line
                #mini cart scan
                t_x, t_y = self.mini_cart_permititer_scan(cool_arr[-5:-3],"R")
                boat.goToGPS(t_x, t_y)
                continue


            #passed checks: SAILING; DOING THE EVENT====================

            #beginning set up
            if start: #and not(moving):
                #if not moving and behind 80%
                if self.SK_line_check(cool_arr[0:2], cool_arr[-3:-1],cool_arr[-1]):
                    start = False; #moving = True
                    boat.goToGPS(cool_arr[6],cool_arr[7])  #go to 90

            #majority sail
            elif not(start): #and not(moving):
                #if not moving and behind 75% and sail back
                if self.SK_line_check(cool_arr[2:4], cool_arr[-3:-1],cool_arr[-1]):
                    #moving = True
                    boat.goToGPS(cool_arr[6],cool_arr[7])  #go to 90
            
                #if past or at 90% (redundence reduction)
                elif not(self.SK_line_check(cool_arr[4:6], cool_arr[-3:-1],cool_arr[-1])):
                    #moving = False
                    boat.adjustSail(90)  #loosen sail, do nuthin

    #give %-line of box and other lines(details in SK)
    def SK_perc_guide(self,inp_arr,type_arr,buoy_arr):
        #calc front/back/sides mid point
        #find the parameter lat/long value per percent
        #calc line 75%/80%/90% (give long, if lat) towards front between them
            #input an array of wanted %'s, return array with matching x/y's (in own array, array of arrays)
                #saves on calc times
            #https://www.desmos.com/calculator/yjeqtqunbh
                #go with s scaling
                    #1.)find midpoints
                    #2.)between mid1, mid3: perc scale x/y's
                    #works no matter rotation of boat
                #last in inp_arr returns x/y point that is % way of the box
                    #rest is m/b's
                #add m/b of back line, at end of ret_arr
                #add m of front/back midpoint line, at end of ret_arr
                #0: m/b, 1: x/y

        ret_arr = []
        mid_arr=[]#, m_arr=[], b_arr=[]

        # midpoints ==========================
        #   (12,13,34,24);(front,left,back,right)
        #   02,04,46,26
        a = [0, 2, 0, 4, 4, 6, 2, 6]    #optimizing code with for rather then long ass list
        # 0,1, 2,3, 4,5, 6,7
        for i in range(4):  # 0,1,2,3
            #TODO: remove nice variables: just fill in and make two lines (optimization)
            #nah
            j1 = a[i*2]  # 0 - 0 - 4 - 2
            k1 = j1 +1  # 1 - 1 - 5 - 3
            j2 = a[(i*2) +1]  # 2 - 4 - 6 - 6  next over in "a"
            k2 = j2 +1  # 3 - 5 - 7 - 7

            p = (buoy_arr[j1] + buoy_arr[j2])/2  # 0+1/2: j1,j2
            mid_arr.append(p)   #p
            mid_arr.append(self.SK_f(p, buoy_arr[j1], buoy_arr[k1], buoy_arr[j2], buoy_arr[k2]))    #p,j1,k1,j2,k2
        
        
        '''# m's and b's ==========================
        #   dont wanna just delete cause dont wanna rewrite if somehow need them
        #   (mid13,mid24; 1,2; 3,4; mid12,mid34)
        m_arr.append(self.SK_m(mid_arr[2], mid_arr[3], mid_arr[6], mid_arr[7]))  # mid13 - mid24 (2,4)  m2
        #m_arr.append(self.SK_m(buoy_arr[0], buoy_arr[1], buoy_arr[2], buoy_arr[3]))  # 1 - 2            front
        m_arr.append(self.SK_m(buoy_arr[4], buoy_arr[5], buoy_arr[6], buoy_arr[7]))  # 3 - 4            back
        #m_arr.append(self.SK_m(mid_arr[0], mid_arr[1], mid_arr[4], mid_arr[5]))  # mid12 - mid34 (1,3)  down center

        b_arr.append(self.SK_v(mid_arr[2], mid_arr[3], mid_arr[6], mid_arr[7]))  # mid13 - mid24 (2,4)
        #b_arr.append(self.SK_v(buoy_arr[0], buoy_arr[1], buoy_arr[2], buoy_arr[3]))  # 1 - 2
        b_arr.append(self.SK_v(buoy_arr[4], buoy_arr[5], buoy_arr[6], buoy_arr[7]))  # 3 - 4
        #b_arr.append(self.SK_v(mid_arr[0], mid_arr[1], mid_arr[4], mid_arr[5]))  # mid12 - mid34 (1,3)


        #front/back mid line for facing use
        m_arr.append(self.SK_m(mid_arr[0],mid_arr[1],mid_arr[4],mid_arr[5]))'''
        m2 = self.SK_m(mid_arr[2], mid_arr[3], mid_arr[6], mid_arr[7])
        
        #newline: s-scale
        for i in range(len(inp_arr)):
            perc = inp_arr[i]/100
            x = perc*mid_arr[0] + (1-perc)*mid_arr[4]
            y = perc*mid_arr[1] + (1-perc)*mid_arr[5]

            if type_arr[i] == 1: #x/y
                ret_arr.append(x)
                ret_arr.append(y)
                continue
            else:
                ret_arr.append( m2[0] )      #m
                ret_arr.append( y-m2[0]*x )  #b

        #sides-line for cart_perimiter_scan
            #front
        ret_arr.append( self.SK_m(buoy_arr[0], buoy_arr[1], buoy_arr[2], buoy_arr[3]) ) #m buoy1,buoy2
        ret_arr.append( self.SK_v(buoy_arr[0], buoy_arr[1], buoy_arr[2], buoy_arr[3]) ) #b buoy1,buoy2
            #left
        ret_arr.append( self.SK_m(buoy_arr[0], buoy_arr[1], buoy_arr[4], buoy_arr[5]) ) #m buoy1,buoy3
        ret_arr.append( self.SK_v(buoy_arr[0], buoy_arr[1], buoy_arr[4], buoy_arr[5]) ) #b buoy1,buoy3
            #right
        ret_arr.append( self.SK_v(buoy_arr[2], buoy_arr[3], buoy_arr[6], buoy_arr[7]) ) #m buoy2,buoy4
        ret_arr.append( self.SK_v(buoy_arr[2], buoy_arr[3], buoy_arr[6], buoy_arr[7]) ) #b buoy2,buoy4

        #back-line, m of middle-line(linecheck)
        '''ret_arr.append(m_arr[1])
        ret_arr.append(b_arr[1])
        ret_arr.append(m_arr[2])
        #ret_arr.append(b_arr[2])'''
            #back
        ret_arr.append( self.SK_m(buoy_arr[4], buoy_arr[5], buoy_arr[6], buoy_arr[7]) ) #m buoy3,buoy4
        ret_arr.append( self.SK_v(buoy_arr[4], buoy_arr[5], buoy_arr[6], buoy_arr[7]) ) #b buoy3,buoy4
        ret_arr.append( self.SK_m(mid_arr[0],mid_arr[1],mid_arr[4],mid_arr[5]) )

        return ret_arr

    #if past line
    def SK_line_check(self,Tarr,Barr,mid_m):
        #TRUE: BEHIND LINE
        #FALSE: AT OR PAST LINE

        #Ix/y:  current location of boat
        #       boat.gps.longitude, boat.gps.latitude
        #Tarr:  m/b compare line
        #arr:   m/b Back line,
        
        #Fa:front
        #Fb:mid
        #Fc:back

        Fa=0;Fb=0;Fc=0  #temp sets
        #check if sideways =========================
        #input x/y as Buoy x/y's to func
        gps.updategps()
        if abs(mid_m) < 1: #Barr is secretly the mid m line shhhhhhh (LOOK AT ME)
            #sideways  -------------------
            #x=(y-b)/m
            Fa= (boat.gps.latitude-Tarr[1])/Tarr[0]
            Fb= boat.gps.longitude
            Fc= (boat.gps.latitude-Barr[1])/Barr[0]
        else:
            #rightways  -------------------
            #y=mx+b
            Fa= Tarr[0]*boat.gps.longitude +Tarr[1]
            Fb= boat.gps.latitude
            Fc= Barr[0]*boat.gps.longitude +Barr[1]

        if Fa > Fc: #upright
            if Fa >= Fb: return False   #past or equal
            else: return True           #behind
        else: #upside down
            if Fa <= Fb: return False   #past or equal
            else: return True           #behind
    
    #find best point of run to leave box
    def cart_perimiter_scan(self,arr):
        #https://www.desmos.com/calculator/rz8tfc8fwn
        #see what mid point closest (Left,Back,Right)
            #cartesian with rand radius
                #find point at perimeter at -45 or 125 (left,right) degrees (LDeg,RDeg line)
                #find m/b of both
                #x = r × cos( θ )
                #y = r × sin( θ );  r=5(doesnt matter)
            #take I() of LDeg,LSide; LDeg,BSide; RDeg,RSide; RDeg,BSide
                #find closest, sail to

        #arr: back-line,left-line,right-line (m,b's) 01,23,45
            #find x,y's of degrees at best run points left and right
            
        gps.updategps()
        lat = boat.gps.latitude, long=boat.gps.longitude
        t = math.pi/180
        o = windVane.position
        lx = 5*math.cos(135 *t+o*t)+lat
        ly = 5*math.sin(135 *t+o*t)+long
        rx = 5*math.cos(-135*t+o*t)+lat
        ry = 5*math.sin(-135*t+o*t)+long
            #into m,b's
        lm = self.SK_m(lx,ly,lat,long)
        lb = self.SK_v(lx,ly,lat,long)
        rm = self.SK_m(rx,ry,lat,long)
        rb = self.SK_v(rx,ry,lat,long)
        #del t,o,lx,ly,rx,ry

            #find intersects of LDeg,LSide; LDeg,BSide; RDeg,RSide; RDeg,BSide
        t_arr=[]
        t_arr.append( self.SK_I(lm,lb,arr[2],arr[3]) )  #x1(0)
        t_arr.append( lm*t_arr[0]+lb )  #y1(1)
        t_arr.append( self.SK_I(lm,lb,arr[0],arr[1]) )  #x2(2)
        t_arr.append( lm*t_arr[2]+lb )  #y2(3)
        t_arr.append( self.SK_I(rm,rb,arr[4],arr[5]) )  #x3(4)
        t_arr.append( rm*t_arr[4]+rb )  #y3(5)
        t_arr.append( self.SK_I(rm,rb,arr[0],arr[1]) )  #x4(6)
        t_arr.append( rm*t_arr[6]+rb )  #y4(7)

            #use distance equation and find closest
        sd = self.SK_d(t_arr[0],t_arr[1],lat,long)
        si = -1
        for i in range(3):
            a = self.SK_d(t_arr[2*(i+1)],t_arr[(2*i)+3],lat,long) #skip 0,1
            if a<sd:    sd=a;si=i
        return t_arr[si+1],t_arr[si+2]

    def mini_cart_permititer_scan(self,arr,case):
        gps.updategps()
        lat = boat.gps.latitude, long=boat.gps.longitude
        t = math.pi/180
        o = windVane.position

        if case == "L":
            x = 5*math.cos(55 *t+o*t)+lat   #+35 from windvane
            y = 5*math.sin(55 *t+o*t)+long
        elif case == "R":
            x = 5*math.cos(125 *t+o*t)+lat  #-35
            y = 5*math.sin(125 *t+o*t)+long
        else:
            raise TypeError("mini_cart_permititer_scan ERROR")

        m = self.SK_m(x,y,lat,long)
        b = self.SK_v(x,y,lat,long)

        ret1= self.SK_I(arr[0],arr[1],m,b)
        return ret1, m*ret1 + b


    def SK_f(self,x,a1,b1,a2,b2): return self.SK_m(a1,b1,a2,b2)*x + self.SK_v(a1,b1,a2,b2)  #f(x)=mx+b
    def SK_m(self,a1,b1,a2,b2): return (b2-b1)/(a2-a1)                                      #m: slope between two lines
    def SK_v(self,a1,b1,a2,b2): return b1-(self.SK_m(a1,b1,a2,b2)*a1)                       #b: +y between two lines
    def SK_I(self,M1,V1,M2,V2): return (V2-V1)/(M1-M2)                                      #find x-cord intersect between two lines
    def SK_d(self,a1,b1,a2,b2): return math.sqrt((a2-a1)**2 + (b2-b1)**2)                   #find distance between two points


    #===================================================================================
    #inputs: B1 long/lat, Radius (boat.event_arr)
    def Search(self):
        #Challenge	Goal:
            #To demonstrate the boat’s ability to autonomously locate an object
        #Description:
            #An orange buoy will be placed somewhere within 100 m of a reference position
            #The boat must locate, touch, and signal* such within 10 minutes of entering the search area
            #RC is not allowed after entering the search area
            #'Signal' means white strobe on boat and/or signal to a shore station and either turn into wind or assume station-keeping mode
        #Scoring:
            #15 pts max
            #12 pts for touching (w/o signal)
            #9 pts for passing within 1m
            #6 pts for performing a search pattern (creeping line, expanding square, direct tracking to buoy, etc)
        #assumptions: (based on guidelines)
            #left of start direction is upstream


        #make in boatMain along with mode switch, attach buoy coords and radius in ary
        #will need to redo GUI then ://////
        arr = self.SR_pattern(boat.gps.latitude, boat.gps.longitude, boat.event_arr[0], boat.event_arr[1], boat.event_arr[2])

        while(True):
            #main running
                #blah blah blah


            if self.event_NL(): return  #checks if mode has switched, exits func if so
        
    #5 point cart search pattern
    def SR_pattern(self, gps_lat, gps_long, buoy_lat, buoy_long, radius):
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

