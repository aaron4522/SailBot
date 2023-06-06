#from curses import KEY_B2

import logging
import math
import time

try:
    from GPS import gps
    from compass import compass
    from camera import Camera, Frame
    from objectDetection import ObjectDetection, Detection
    import constants as c

except Exception as e:
    from sailbot.GPS import gps
    import sailbot.constants as c

from datetime import date, datetime
from threading import Thread
from time import sleep



#============================================================================================================================
'''
next_gps() returns next long/lat (x/y) point to go to
    return ###,###:         expected result
    return None,None:       adjust sail to 90(drop it), clear target
    raise exception eventFinished:  end the event

    check inside main for a specific exception as the end of the event
    NOTE: for some events: there is no "end" of the event, must switch to manual which will clear the class in main
Events that require manual end:
    -Station Keeping
'''

class event:
    def __init__(self, arr):
        print("init")
        self.event_arr = arr
        self.totalError = 0.0
        self.oldError = 0.0
        self.oldTime = time.time()
        self.last_pnt_x, self.last_pnt_y = None,None
        self.gps_class = gps()
    
    def SK_f(self,x,a1,b1,a2,b2): return self.SK_m(a1,b1,a2,b2)*x + self.SK_v(a1,b1,a2,b2)  #f(x)=mx+b
    def SK_m(self,a1,b1,a2,b2): return (b2-b1)/(a2-a1)                                      #m: slope between two lines
    def SK_v(self,a1,b1,a2,b2): return b1-(self.SK_m(a1,b1,a2,b2)*a1)                       #b: +y between two lines
    def SK_I(self,M1,V1,M2,V2): return (V2-V1)/(M1-M2)                                      #find x-cord intersect between two lines
    def SK_d(self,a1,b1,a2,b2): return math.sqrt((a2-a1)**2 + (b2-b1)**2)                   #find distance between two points

    #TODO: find new place to relocate
    def PID(self):  #hana
        # New PID stuff
        if (time.time() - self.oldTime < 100):  # Only runs every tenth of a second #new
            # Finds the angle the boat should take
            error = self.boat_RefObj.targetAngle - self.compass.angle  # Finds how far off the boat is from its goal
            self.totalError += error  # Gets the total error to be used for the integral gain
            derivativeError = (error - self.oldError) / (time.time() - self.oldtime)  # Gets the change in error for the derivative portion
            deltaAngle = c.config['CONSTANTS']["P"] * error + c.config['CONSTANTS']["I"] * self.totalError + c.config['CONSTANTS']["D"] * derivativeError  # Finds the angle the boat should be going

            # Translates the angle into lat and log so goToGPS won't ignore it
            self.boat_RefObj.currentAngle = getCoordinateADistanceAlongAngle(1000, deltaAngle + self.boat_RefObj.compass.angle)

            # Resets the variable
            self.oldTime = time.time()
            self.oldError = error


class Collision_Avoidance(event):
    #===================================================================================
    #inputs: B1,B2,B3 long/lat
    #arr: [B1x,B1y, etc] (self.event_arr)
    def __init__(self, arr):
        super().__init__(arr)
        print("Collision_Avoidance moment")
        '''#Challenge Goal:
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
            #going back is harder'''

    def next_gps(self):
        return 0,0


class Percision_Navigation(event):  #jonah
    #===================================================================================
    #inputs: B1,B2,B3,B4 long/lat
    #TL[0,1],TR[2,3],BL[4,5],BR[6,7] (left/right top, left/right bottom)
    #arr: [B1x,B1y, etc] (self.event_arr)
    def __init__(self,arr):
        super().__init__(arr)
        print("Percision_Navigation moment")
        '''#Challenge	Goal:
            #To demonstrate the boat's ability to autonomously navigate a course within tight tolerances.
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
            #going back is harder'''
        
        self.ifsideways = None; self.ifupsidedown = None    #set up for later PN_checkwayside

        self.PN_arr = []
        self.PN_arr = self.PN_coords()

        self.rev_bool = False
        self.target_set = 1
        self.start_time = time.time()

    def next_gps(self):
            #time based check
        #curr_time = time.time()
        #if int(curr_time - self.start_time)%4 != 0: return None,None

            #set check
        if self.target_set >=int( len(self.PN_arr)/2): 
            logging.info(f"PN: REACHED FINAL POINT;\nEXITING EVENT")
            print(f"Finished Perc Nav")
            raise eventFinished

            #main running: go to points in PN_arr
        if self.PN_PassCheck():
            logging.info(f"PN: PASSED TARGET POINT: {self.target_set}")
            print(f"Passed target point: {self.target_set}")
            self.target_set += 1
        
        logging.info(f"PN: CURR TARGET POINT: {self.target_set}")
        print(f"Current target point: {self.target_set}")
        return self.PN_arr[self.target_set*2], self.PN_arr[(self.target_set*2)+1]
            
    #find coords that should go to via cart of buoy coords
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
        ret_arr.append( rad1*math.cos(  (90+m1) *t)+self.event_arr[4] )  #pt1x[0]
        ret_arr.append( rad1*math.sin(  (90+m1) *t)+self.event_arr[5] )  #pt1y[1]
        ret_arr.append( rad2*math.cos( (225+m2) *t)+self.event_arr[4] )  #pt2x[2]
        ret_arr.append( rad2*math.sin( (225+m2) *t)+self.event_arr[5] )  #pt2y[3]

        #b3/4[4-5]
        ret_arr.append( (self.event_arr[4]+self.event_arr[6])/2 )  #pt3x[4]
        ret_arr.append( (self.event_arr[5]+self.event_arr[7])/2 )  #pt3y[5]

        #b4[6-9]
        ret_arr.append( rad2*math.cos( (315-m2) *t)+self.event_arr[6] )  #pt4x[6]
        ret_arr.append( rad2*math.sin( (315-m2) *t)+self.event_arr[7] )  #pt4y[7]
        ret_arr.append( rad1*math.cos(  (90-m1) *t)+self.event_arr[6] )  #pt5x[8]
        ret_arr.append( rad1*math.sin(  (90-m1) *t)+self.event_arr[7] )  #pt5y[9]

        #b1/2[10-11]
        ret_arr.append( (self.event_arr[0]+self.event_arr[2])/2 )  #pt6x[10]
        ret_arr.append( (self.event_arr[1]+self.event_arr[3])/2 )  #pt6y[11]

        return ret_arr

    #find if passed target (ret bool)
    def PN_PassCheck(self):
        #self.target_set,self.PN_arr
        #self.event_arr

        '''
        #SK_f(x)
        #P1[0-1], self.event_arr[4-5]
        #P1[2-3], self.event_arr[4-5]
        #
        #P1[6-7], self.event_arr[6-7]
        #P1[8-9], self.event_arr[6-7]
        #self.event_arr[0-1], self.event_arr[2-3]

        #pt1: x<P1x[0],    y<L1(x)[ m(P1[0-1],[]) ]
        #pt2: x>P2x[2],    y<L2(x)
        #pt3: x>Perpendicular P2toP4    -(1/m)x+ P[5]-(1/m)*P[6]
        #pt4: x>P4x[6],    y>L4(x)
        #pt5: x<P5x[8],    y>L5(x)
        #pt6: y>L6(x)
        '''

        self.gps_class.updategps()
        #self.gps_class.longitude
        #self.gps_class.latitude

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
                x = (self.gps_class.longitude <= self.event_arr[4]
                    and self.gps_class.latitude <= self.SK_f( self.gps_class.longitude,self.PN_arr[0],self.PN_arr[1],self.event_arr[4],self.event_arr[5] ))

            #below(lat) of BL buoy[4,{5}]
            #below(lat) line between p2[2,3] and BL buoy[4,5]
            elif self.target_set == 2:
                x = (self.gps_class.latitude <= self.event_arr[5]
                    and self.gps_class.latitude <= self.SK_f( self.gps_class.longitude,self.PN_arr[2],self.PN_arr[3],self.event_arr[4],self.event_arr[5] ))

            #right(long) of line perpendicular to p2[2,3] and p4[6,7] at p3[4,5]
            elif self.target_set == 3:
                x = self.gps_class.longitude >= self.PN_Perpend(self.gps_class.longitude,self.PN_arr[4],self.PN_arr[5],self.PN_arr[2],self.PN_arr[3],self.PN_arr[4],self.PN_arr[5])
            
            #right(long) of BR buoy[{6},7]
            #above(lat) line between p4[6,7] and BR buoy[6,7]
            elif self.target_set == 4:
                x = (self.gps_class.longitude >= self.event_arr[6]
                    and self.gps_class.latitude >= self.SK_f( self.gps_class.longitude,self.PN_arr[6],self.PN_arr[7],self.event_arr[6],self.event_arr[7] ))
            
            #above(lat) of BR buoy[6,{7}]
            #above(lat) line between p5[8,9] and BR buoy[6,7]
            elif self.target_set == 5:
                x = (self.gps_class.latitude >= self.event_arr[7]
                    and self.gps_class.latitude >= self.SK_f( self.gps_class.longitude,self.PN_arr[8],self.PN_arr[9],self.event_arr[6],self.event_arr[7] ))

            #above(lat) line between TL[0,1] and TR[2,3]
            elif self.target_set == 6:
                x = self.gps_class.latitude >= self.SK_f( self.gps_class.longitude,self.event_arr[0],self.event_arr[1],self.event_arr[2],self.event_arr[3] )
            else:
                logging.info(f"PN: ERROR: 00: TARGET SET OUT OF RANGE (1to6)\nTARGET PNT = {self.target_set}")
                print(f"PN: ERROR: 00: TARGET SET OUT OF RANGE (1to6)\nTARGET PNT = {self.target_set}")

        #flip long/lat------------------------------------------------------------------
        elif not(self.ifupsidedown) and     self.ifsideways:
            #left(long) of BL buoy[{4},5]
            #below(lat) line between p1[0,1] and BL buoy[4,5]
            if self.target_set == 1:
                x = (self.gps_class.latitude <= self.event_arr[4]
                    and self.gps_class.longitude <= self.SK_f( self.gps_class.latitude,self.PN_arr[0],self.PN_arr[1],self.event_arr[4],self.event_arr[5] ))

            #below(lat) of BL buoy[4,{5}]
            #below(lat) line between p2[2,3] and BL buoy[4,5]
            elif self.target_set == 2:
                x = (self.gps_class.longitude <= self.event_arr[5]
                    and self.gps_class.longitude <= self.SK_f( self.gps_class.latitude,self.PN_arr[2],self.PN_arr[3],self.event_arr[4],self.event_arr[5] ))

            #right(long) of line perpendicular to p2[2,3] and p4[6,7] at p3[4,5]
            elif self.target_set == 3:
                x = self.gps_class.latitude >= self.PN_Perpend(self.gps_class.latitude,self.PN_arr[4],self.PN_arr[5],self.PN_arr[2],self.PN_arr[3],self.PN_arr[4],self.PN_arr[5])
            
            #right(long) of BR buoy[{6},7]
            #above(lat) line between p4[6,7] and BR buoy[6,7]
            elif self.target_set == 4:
                x = (self.gps_class.latitude >= self.event_arr[6]
                    and self.gps_class.longitude >= self.SK_f( self.gps_class.latitude,self.PN_arr[6],self.PN_arr[7],self.event_arr[6],self.event_arr[7] ))
            
            #above(lat) of BR buoy[6,{7}]
            #above(lat) line between p5[8,9] and BR buoy[6,7]
            elif self.target_set == 5:
                x = (self.gps_class.longitude >= self.event_arr[7]
                    and self.gps_class.longitude >= self.SK_f( self.gps_class.latitude,self.PN_arr[8],self.PN_arr[9],self.event_arr[6],self.event_arr[7] ))

            #above(lat) line between TL[0,1] and TR[2,3]
            elif self.target_set == 6:
                x = self.gps_class.longitude >= self.SK_f( self.gps_class.latitude,self.event_arr[0],self.event_arr[1],self.event_arr[2],self.event_arr[3] )
            else:
                logging.info(f"PN: ERROR: 00: TARGET SET OUT OF RANGE (1to6)\nTARGET PNT = {self.target_set}")
                print(f"PN: ERROR: 00: TARGET SET OUT OF RANGE (1to6)\nTARGET PNT = {self.target_set}")

        #flip >/<------------------------------------------------------------------
        elif self.ifupsidedown      and not(self.ifsideways):
            #left(long) of BL buoy[{4},5]
            #below(lat) line between p1[0,1] and BL buoy[4,5]
            if self.target_set == 1:
                x = (self.gps_class.longitude >= self.event_arr[4]
                    and self.gps_class.latitude >= self.SK_f( self.gps_class.longitude,self.PN_arr[0],self.PN_arr[1],self.event_arr[4],self.event_arr[5] ))

            #below(lat) of BL buoy[4,{5}]
            #below(lat) line between p2[2,3] and BL buoy[4,5]
            elif self.target_set == 2:
                x = (self.gps_class.latitude >= self.event_arr[5]
                    and self.gps_class.latitude >= self.SK_f( self.gps_class.longitude,self.PN_arr[2],self.PN_arr[3],self.event_arr[4],self.event_arr[5] ))

            #right(long) of line perpendicular to p2[2,3] and p4[6,7] at p3[4,5]
            elif self.target_set == 3:
                x = self.gps_class.longitude <= self.PN_Perpend(self.gps_class.longitude,self.PN_arr[4],self.PN_arr[5],self.PN_arr[2],self.PN_arr[3],self.PN_arr[4],self.PN_arr[5])
            
            #right(long) of BR buoy[{6},7]
            #above(lat) line between p4[6,7] and BR buoy[6,7]
            elif self.target_set == 4:
                x = (self.gps_class.longitude <= self.event_arr[6]
                    and self.gps_class.latitude <= self.SK_f( self.gps_class.longitude,self.PN_arr[6],self.PN_arr[7],self.event_arr[6],self.event_arr[7] ))
            
            #above(lat) of BR buoy[6,{7}]
            #above(lat) line between p5[8,9] and BR buoy[6,7]
            elif self.target_set == 5:
                x = (self.gps_class.latitude <= self.event_arr[7]
                    and self.gps_class.latitude <= self.SK_f( self.gps_class.longitude,self.PN_arr[8],self.PN_arr[9],self.event_arr[6],self.event_arr[7] ))

            #above(lat) line between TL[0,1] and TR[2,3]
            elif self.target_set == 6:
                x = self.gps_class.latitude <= self.SK_f( self.gps_class.longitude,self.event_arr[0],self.event_arr[1],self.event_arr[2],self.event_arr[3] )
            else:
                logging.info(f"PN: ERROR: 00: TARGET SET OUT OF RANGE (1to6)\nTARGET PNT = {self.target_set}")
                print(f"PN: ERROR: 00: TARGET SET OUT OF RANGE (1to6)\nTARGET PNT = {self.target_set}")

        #flip long/lat, flip >/<------------------------------------------------------------------
        elif self.ifupsidedown      and     self.ifsideways:
            #left(long) of BL buoy[{4},5]
            #below(lat) line between p1[0,1] and BL buoy[4,5]
            if self.target_set == 1:
                x = (self.gps_class.latitude >= self.event_arr[4]
                    and self.gps_class.longitude >= self.SK_f( self.gps_class.latitude,self.PN_arr[0],self.PN_arr[1],self.event_arr[4],self.event_arr[5] ))

            #below(lat) of BL buoy[4,{5}]
            #below(lat) line between p2[2,3] and BL buoy[4,5]
            elif self.target_set == 2:
                x = (self.gps_class.longitude >= self.event_arr[5]
                    and self.gps_class.longitude >= self.SK_f( self.gps_class.latitude,self.PN_arr[2],self.PN_arr[3],self.event_arr[4],self.event_arr[5] ))

            #right(long) of line perpendicular to p2[2,3] and p4[6,7] at p3[4,5]
            elif self.target_set == 3:
                x = self.gps_class.latitude <= self.PN_Perpend(self.gps_class.latitude,self.PN_arr[4],self.PN_arr[5],self.PN_arr[2],self.PN_arr[3],self.PN_arr[4],self.PN_arr[5])
            
            #right(long) of BR buoy[{6},7]
            #above(lat) line between p4[6,7] and BR buoy[6,7]
            elif self.target_set == 4:
                x = (self.gps_class.latitude <= self.event_arr[6]
                    and self.gps_class.longitude <= self.SK_f( self.gps_class.latitude,self.PN_arr[6],self.PN_arr[7],self.event_arr[6],self.event_arr[7] ))
            
            #above(lat) of BR buoy[6,{7}]
            #above(lat) line between p5[8,9] and BR buoy[6,7]
            elif self.target_set == 5:
                x = (self.gps_class.longitude <= self.event_arr[7]
                    and self.gps_class.longitude <= self.SK_f( self.gps_class.latitude,self.PN_arr[8],self.PN_arr[9],self.event_arr[6],self.event_arr[7] ))

            #above(lat) line between TL[0,1] and TR[2,3]
            elif self.target_set == 6:
                x = self.gps_class.longitude <= self.SK_f( self.gps_class.latitude,self.event_arr[0],self.event_arr[1],self.event_arr[2],self.event_arr[3] )
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
        #self.event_arr
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


class Endurance(event):
    #===================================================================================
    #inputs: B1,B2,B3,B4 long/lat
    #arr: [B1x,B1y, etc] (self.event_arr)
    def __init__(self,arr):
        super().__init__(arr)
        print("Endurance moment")
        '''#Challenge	Goal:
            #To demonstrate the boat's durability and capability to sail some distance
        #Description:
            #The boats will sail around 4 buoys (passing within 10 m inside of buoy is OK) for up to 7 hours
        #Scoring:
            #10 pts max
            #1 pt for each 1NM lap completed autonomously (1/2 pt/lap if RC is used at any point during the lap*)
            #An additional 1pt for each continuous (no pit-stop) hr sailed; up to 6 pts
            #At least one lap must be completed to earn points
            #All boats must start each subsequent lap at the Start line following a pit stop or support boat rescue. (*No penalty for momentary RC to avoid collisions.)
        #assumptions: (based on guidelines)
            #left of start direction is upstream'''

    def next_gps(self):
        return 0,0


class Station_Keeping(event):   #jonah
    #===================================================================================
    #inputs: B1,B2,B3,B4 long/lat
    #TL,TR,BL,BR
    #arr: [B1x,B1y, etc] (self.event_arr)
    def __init__(self,arr):
        super().__init__(arr)
        print("Station_Keeping moment")
        '''#Challenge	Goal:
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
            #front is upstream'''

        '''#see SK_perc_guide() notes on calculating go-to points
        #running:
        #1.) wait till fall behind 80%
        #2.) sail to 90%, until at 90%
        #3.) set sail flat
        #4.) if behind 75%, go to step 2, repeat
        #5.) GTFO (find&sail to best point) after time limit
            #DO NOT JUST DROP SAIL
                #how we won event first time was dropping sail
                #and floating from front to end for total of 5 minute duration travel'''
        self.time_perc = 5*60 * (70/100) #time to leave, 5 minute limit * %

        #ALGO ARRAY========================================
        #send in wanted %s in desmos calculation, and return what they are (m,b in y=mx+b; or x,y cord of center of box on %'s line)
        type_inpArr =   [ 0, 0, 0, 1]  #m,b or x,y
        perc_inpArr = [80,75,90,90]  #%'s
        self.cool_arr = self.SK_perc_guide(perc_inpArr,type_inpArr,self.event_arr)
        del type_inpArr, perc_inpArr
        #whats contained in cool_arr:
        #(0,1)80-line,      (2,3)75-line,
        #(4,5)90-line,      (6,7)90-point,

        #[always auto put on end of cool_arr thats not caluclated from input]:
        #(8,9)Front-line (here cause of cart_perimiter_scan),
        #(10,11)Left-line,  (12,13)Right-line,
        #(14,15)Back-line
        #(16) mid m line for line check

        #other Algo sets========================================
        self.start = True
        self.escape_x, self.escape_y = None,None    #determining best out to go to to leave box based on angle of run (wind)
        self.skip = False   #faster if statement for time; holdout from prev notation

        #time calc
        self.start_time = time.time()

    def next_gps(self):
        #time based checks, off-set the set GPS========================================
        curr_time = time.time()
        #gtfo, times up
        if self.skip or curr_time - self.start_time >= self.time_perc:
            #find best point to leave:
            if self.escape_x == None:
                self.skip = True #faster if statement
                self.escape_x, self.escape_y = self.cart_perimiter_scan(self.cool_arr[-7:-1])    #i thought the func name sounded cool
            self.last_pnt_x, self.last_pnt_y = self.escape_x,self.escape_y
            return self.escape_x,self.escape_y
        
        #if not in box========================================
        #ordered in certain way of most importance, handle up/down first before too left or right
        #also put before time because then it doesnt matter cause it's already out

        #past front line of box
        if not( self.SK_line_check(self.cool_arr[-9:-7], self.cool_arr[-3:-1],self.cool_arr[-1]) ):
            logging.info("too forward")
            #loosen sail, do nuthin; drift
            #.adjustSail(90)
            self.last_pnt_x, self.last_pnt_y = None,None
            return None,None
        
        #past bottom line of box
        elif not( self.SK_line_check(self.cool_arr[-3:-1], self.cool_arr[-9:-7],self.cool_arr[-1]) ):
            logging.info("too back")
            #go to 90deg line
            self.last_pnt_x, self.last_pnt_y = self.cool_arr[6],self.cool_arr[7]
            return self.cool_arr[6],self.cool_arr[7]
        
        #past left line of box
        elif not( self.SK_line_check(self.cool_arr[-7:-5], self.cool_arr[-5:-3],self.cool_arr[-1]) ):
            logging.info("too left")
            #find/go-to intersect of line (+)35degrees of wind direction to left line
            #mini cart scan
            t_x, t_y = self.mini_cart_perimiter_scan(self.cool_arr[-7:-5],"L")
            self.last_pnt_x, self.last_pnt_y = t_x, t_y
            return t_x, t_y

        #past right line of box
        elif not( self.SK_line_check(self.cool_arr[-5:-3], self.cool_arr[-7:-5],self.cool_arr[-1]) ):
            logging.info("too right")
            #find/go-to intersect of line (-)35degrees of wind direction to left line
            #mini cart scan
            t_x, t_y = self.mini_cart_perimiter_scan(self.cool_arr[-5:-3],"R")
            self.last_pnt_x, self.last_pnt_y = t_x, t_y
            return t_x, t_y


        #passed checks: SAILING; DOING THE EVENT========================================
        #beginning set up
        if self.start:
            logging.info("start if")
            #if not moving and behind 80%
            if self.SK_line_check(self.cool_arr[0:2], self.cool_arr[-3:-1],self.cool_arr[-1]):
                logging.info("start: behind 80%; ending start")
                self.start = False
                self.last_pnt_x, self.last_pnt_y = self.cool_arr[6],self.cool_arr[7]
                return self.cool_arr[6],self.cool_arr[7]    #go to 90deg line
            #if this doesnt pass, its WITHIN BOX but is ahead of 80; so it returns init'd last_pnt which is to loosen sail and drift (WHAT WE WANT)
            else:   logging.info("start: ahead 80%")

        #majority of the sail
        else:
            #if behind 75%:sail back
            if self.SK_line_check(self.cool_arr[2:4], self.cool_arr[-3:-1],self.cool_arr[-1]):
                self.last_pnt_x, self.last_pnt_y = self.cool_arr[6],self.cool_arr[7]
                return self.cool_arr[6],self.cool_arr[7]    #go to 90deg line
        
            #if past or at 90% (redundence reduction)
            elif not(self.SK_line_check(self.cool_arr[4:6], self.cool_arr[-3:-1],self.cool_arr[-1])):
                self.last_pnt_x, self.last_pnt_y = None,None
                return None,None  #loosen sail, do nuthin
        
        return self.last_pnt_x, self.last_pnt_y #fall back return if nested if's dont pass

    #give %-line of box and other lines(details in SK) used in algo
    def SK_perc_guide(self,inp_arr,type_arr,buoy_arr):
        '''#calc front/back/sides mid point
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
        #then add other details need to the very end'''

        ret_arr = []
        mid_arr=[]#, m_arr=[], b_arr=[]

        # midpoints ==========================
        #annoying optimization work; done with skips in 'i' indexing
        '''
        - i=x cord of buoy, even index in array
        - need to find with different combos of all the buoy coords to find the point in the middle of them
        - organize those combos with a FAST FOR STATEMENT using index skipping
        - can see depreciated "straightforward" way of doing it below, this looks nicer (and takes less memory?)
        - need to find these midpoints to calcualte the perc lines/points given in input of function
        '''
        #   (12,13,34,24);(front,left,back,right)
        #   02,04,46,26
        a = [0, 2, 0, 4, 4, 6, 2, 6]    #optimizing code with for rather then long ass list
        # 0,1, 2,3, 4,5, 6,7
        for i in range(4):  # 0,1,2,3
            #TODO: remove nice variables: just fill in and make two lines (optimization)
            #NOTE: nah, fuck that^^^
            j1 = a[i*2]  # 0 - 0 - 4 - 2
            k1 = j1 +1  # 1 - 1 - 5 - 3
            j2 = a[(i*2) +1]  # 2 - 4 - 6 - 6  next over in "a"
            k2 = j2 +1  # 3 - 5 - 7 - 7

            p = (buoy_arr[j1] + buoy_arr[j2])/2  # 0+1/2: j1,j2
            mid_arr.append(p)   #p
            mid_arr.append(self.SK_f(p, buoy_arr[j1], buoy_arr[k1], buoy_arr[j2], buoy_arr[k2]))    #p,j1,k1,j2,k2
        
        
        '''
        #DEPRECIATED
        #DO NOT DELETE, USE FOR EXPLANATION FOR OPTIMIZATION
        # m's and b's ==========================
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
        m2 = self.SK_m(mid_arr[2], mid_arr[3], mid_arr[6], mid_arr[7])  #slope between side line's midpoints
        
        #newline: s-scale
        #adding all perc line/point into return array (from input in function)
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

        #sides-line for cart_perimiter_scan; additional additions to return
        #front
        ret_arr.append( self.SK_m(buoy_arr[0], buoy_arr[1], buoy_arr[2], buoy_arr[3]) ) #m buoy1,buoy2
        ret_arr.append( self.SK_v(buoy_arr[0], buoy_arr[1], buoy_arr[2], buoy_arr[3]) ) #b buoy1,buoy2
        #left
        ret_arr.append( self.SK_m(buoy_arr[0], buoy_arr[1], buoy_arr[4], buoy_arr[5]) ) #m buoy1,buoy3
        ret_arr.append( self.SK_v(buoy_arr[0], buoy_arr[1], buoy_arr[4], buoy_arr[5]) ) #b buoy1,buoy3
        #right
        ret_arr.append( self.SK_v(buoy_arr[2], buoy_arr[3], buoy_arr[6], buoy_arr[7]) ) #m buoy2,buoy4
        ret_arr.append( self.SK_v(buoy_arr[2], buoy_arr[3], buoy_arr[6], buoy_arr[7]) ) #b buoy2,buoy4
        '''#back-line, m of middle-line(linecheck); additional additions to return
        ret_arr.append(m_arr[1])
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
        #       self.gps_class.longitude, self.gps_class.latitude
        #Tarr:  m/b compare line
        #arr:   m/b Back line,
        
        #Fa:front
        #Fb:mid
        #Fc:back

        Fa=0;Fb=0;Fc=0  #temp sets
        #check if sideways =========================
        #input x/y as Buoy x/y's to func
        self.gps_class.updategps()
        if abs(mid_m) < 1: #Barr is secretly the mid m line shhhhhhh (LOOK AT ME)
            #sideways  -------------------
            #x=(y-b)/m
            Fa= (self.gps_class.latitude-Tarr[1])/Tarr[0]
            Fb= self.gps_class.longitude
            Fc= (self.gps_class.latitude-Barr[1])/Barr[0]
        else:
            #rightways  -------------------
            #y=mx+b
            Fa= Tarr[0]*self.gps_class.longitude +Tarr[1]
            Fb= self.gps_class.latitude
            Fc= Barr[0]*self.gps_class.longitude +Barr[1]

        if Fa > Fc: #upright
            if Fa >= Fb: return False   #past or equal
            else: return True           #behind
        else: #upside down
            if Fa <= Fb: return False   #past or equal
            else: return True           #behind
    
    #find best point of run to leave box
    def cart_perimiter_scan(self,arr):
        #DETAILS
        '''#https://www.desmos.com/calculator/rz8tfc8fwn
        #see what mid point closest (Left,Back,Right)
            #cartesian with rand radius
                #find point at perimeter at -45 or 125 (left,right) degrees (LDeg,RDeg line)
                #find m/b of both
                #x = r * cos( θ )
                #y = r * sin( θ );  r=5(doesnt matter)
            #take I() of LDeg,LSide; LDeg,BSide; RDeg,RSide; RDeg,BSide
                #find closest, sail to

        #arr: back-line,left-line,right-line (m,b's) 01,23,45
            #find x,y's of degrees at best run points left and right'''

        #STRAIGHTFORWARD EXPLANATION:
        #make a point in the 2 best directions of run using cart math
        #make a line between the boat and both points
        #find intersection of those two lines and the boat
        #determine with intersection is closest
            
        self.gps_class.updategps()
        lat = self.gps_class.latitude; long = self.gps_class.longitude
        t = math.pi/180
        o = windVane.position
        lx = 5*math.cos( 135*t+o*t)+lat     #left side run point
        ly = 5*math.sin( 135*t+o*t)+long
        rx = 5*math.cos(-135*t+o*t)+lat     #right side run point
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

    #same concept as cart_perm_scan
    #used when OUTSIDE BOX to find best line to attack INTO BOX
    #just for when left/right of box
    def mini_cart_perimiter_scan(self,arr,case):
        self.gps_class.updategps()
        lat = self.gps_class.latitude; long = self.gps_class.longitude
        t = math.pi/180
        o = windVane.position

        if case == "L":
            x = 5*math.cos( 55*t+o*t)+lat   #+35 from windvane
            y = 5*math.sin( 55*t+o*t)+long
        elif case == "R":
            x = 5*math.cos(125*t+o*t)+lat   #-35
            y = 5*math.sin(125*t+o*t)+long
        else:
            raise TypeError("mini_cart_perimiter_scan ERROR")

        m = self.SK_m(x,y,lat,long)
        b = self.SK_v(x,y,lat,long)

        ret1= self.SK_I(arr[0],arr[1],m,b)
        return ret1, m*ret1 + b


class Search(event):
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
    # Strategy:
        # Define search path as series of GPS lines to cover the most ground in shortest time
        # If x% match verify:
            # Check if estimated position is outside of given bounds + buffer
        # Then deviate from course and go to position
            # If target confidence increases -> target lock & goto
            # if target confidence decreases -> 
        # On
            
    #inputs: B1 long/lat, Radius (self.event_arr)
    def __init__(self,arr):
        super().__init__(arr)
        print("Search moment")
        self.object_detection = ObjectDetection()
        self.camera = Camera()


        #make in boatMain along with mode switch, attach buoy coords and radius in ary
        #will need to redo GUI then ://////
        self.arr = self.SR_pattern()
    
    def next_gps(self):
        return 0,0
    
    def loop(self):
        """Event body"""
        imgs: list[Frame] = self.camera.survey(3) # (3, analyze=True?)
        for i, img in enumerate(i, imgs):
            self.object_detection.analyze(img)
        imgs.sort() # sort by confidence
        # Datapoints:
            # GPS pos of boat
            # GPS pos of detections
            # Confidence of detections
        # Abstract:
            # Create a heatmap of buoys which persists across surveys
                # (lat, long, confidence) 
        
        
    
    def SR_pattern(self):
        #find five coords via search pattern
        #in realtion to current pos and buoy rad center pos

        self.gps_class.updategps()
        gps_lat = self.gps_class.latitude
        gps_long = self.gps_class.longitude

        a = gps_lat - self.event_arr[0]
        b = gps_long - self.event_arr[1]
        ang = math.atan(b/a)
        ang *= 180/math.pi

        if(a<0): ang += 180

        tar_angs = [ang,ang+72,ang-72,ang-(72*3),ang-(72*2)]
        tarx = [0]*5
        tary = [0]*5

        for i in range(0,5):
            tarx[i] =  self.event_arr[0]  + self.event_arr[2]*math.cos( tar_angs[i] * (math.pi/180) )
            tary[i] =  self.event_arr[1] + self.event_arr[2]*math.sin( tar_angs[i] * (math.pi/180) )
        
        return tarx,tary


#=================
class eventFinished(Exception):
    pass

#============================================================================================================================
def testloop():
    print("----Accepted events: CA,PN,E,SK,S----")
    inp = input("Mode Test: ")
    print('''
=============================
Accepted event info:
CA: B1,B2,B3 long/lat
PN: B1,B2,B3,B4 long/lat
E:  B1,B2,B3,B4 long/lat
SK: B1,B2,B3,B4 long/lat
S:  B1 long/lat, radius
-----------------------------
''')
    inp1 = input("Event info(space with ','): ")
    inp1 = inp1.split(',')
    for i in range(len(inp1)): inp1[i] = float(inp1[i])
    print(inp1)
    if inp == "CA":
        if len(inp1) != 6: raise Exception("invalid event info len")
        obj = Collision_Avoidance(inp1)
    elif inp == "PN":
        if len(inp1) != 8: raise Exception("invalid event info len")
        obj = Percision_Navigation(inp1)
    elif inp == "E":
        if len(inp1) != 8: raise Exception("invalid event info len")
        obj = Endurance(inp1)
    elif inp == "SK":
        if len(inp1) != 8: raise Exception("invalid event info len")
        obj = Station_Keeping(inp1)
    elif inp == "S":
        if len(inp1) != 3: raise Exception("invalid event info len")
        obj = Search(inp1)
    else:
        print("nah...")
        raise Exception("invalid event name")
    return obj


if __name__ == "__main__":
    eevee = testloop()
    while True:
        try:
            print( str(eevee.next_gps()) )
        except eventFinished:
            break
    print("cya")