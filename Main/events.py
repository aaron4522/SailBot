from curses import KEY_B2
import constants as c
import logging
import math
import time

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

                    elif ary[0] == 'mode' and ary[1] == 0:
                        ret = True
        except Exception as e:
            logging.info(f"failed to read command {self.MESSAGE}")
            print(f"message error: {e}")
        
        boat.readMessages(self.MESSAGE) #override message to make faster

        # SEND MESSAGE SECTION =========
        boat.sendData()

        return ret


    def testloop(self, inp):
        t_inp = input("inputs: ")
        t_arr = t_inp.split(" ")
        if inp == "CA":
            self.Collision_Avoidance(t_arr)
        elif inp == "PN":
            self.Percision_Navigation(t_arr)
        elif inp == "E":
            self.Endurance(t_arr)
        elif inp == "SK":
            self.Station_Keeping(t_arr)
        elif inp == "S":
            self.Search(t_arr)
        else:
            print("nah")


    #include in automation event code's main loop:
        #self.readmessages to see if it switches modes or RC commands, returning/break if another mode is true
        #self.sendData() to export data

    #inputs: B1,B2,B3,B4 long/lat
    #arr: [B1x,B1y, etc] (boat.event_arr)
    def Collision_Avoidance(self):
        print("Collision_Avoidance moment")

        while(True):
            #main running
                #blah blah blah


            if self.event_NL(): return  #checks if mode has switched, exits func if so



    #inputs: B1,B2,B3,B4 long/lat
    #arr: [B1x,B1y, etc] (boat.event_arr)
    def Percision_Navigation(self):
        print("Percision_Navigation moment")

        while(True):
            #main running
                #blah blah blah


            if self.event_NL(): return  #checks if mode has switched, exits func if so



    #inputs: B1,B2,B3,B4 long/lat
    #arr: [B1x,B1y, etc] (boat.event_arr)
    def Endurance(self):
        print("Endurance moment")

        while(True):
            #main running
                #blah blah blah


            if self.event_NL(): return  #checks if mode has switched, exits func if so



    #inputs: B1,B2,B3,B4 long/lat
    #TL,TR,BL,BR
    #arr: [B1x,B1y, etc] (boat.event_arr)
    def Station_Keeping(self):          #Jonah
        print("Station_Keeping moment")
        #see SK_perc_guide notes on calculating go-to points
        #running:
        #1.) wait till fall behind 80%
        #2.) sail to 90%, until 90%, set sail flat
        #3.) if behind 75%, go to step 2, repeat
        #4.) GO TO BACK POINT(or drop sails?) after time limit
        time_limit = 5*60 #in seconds

        type_arr =   [ 0, 0, 0, 1]
        wanted_arr = [80,75,90,90]
        self.SK_perc_guide(wanted_arr,type_arr,boat.event_arr)
            #(0,1)80-line,      (2,3)75-line,
            #(4,5)90-line,      (6,7)90-point,
            #(8,9)Back-line [always auto put on end]

        start = True; moving= False
        #=== main running ===
        #line check is a long process, so instead of checking both
        #uses mutual exclusion so not continiously moving to same point
            #(kinda sucks need to rework)
            #relook into if we even need mutual exclusion

        #time calc
        start_time = time.time()

        while(True):
            #return checks
            curr_time = time.time()
            if curr_time - start_time >= time_limit:
                #TODO:  either sail to back/side midpoint, or other func to find best path out
                #LEAVE QUICKLY AS POSSIBLE:
                #run down wind
                #windVane.angle()
                return
            
            if self.event_NL(): return  #checks if mode has switched, exits func if so


            #beginning set up
            if start and not(moving):
                #if not moving and behind 80%
                if self.SK_line_check(wanted_arr[0:1], wanted_arr[-3:]):
                    start = False; moving = True
                    boat.goToGPS(wanted_arr[6],wanted_arr[7])  #go to 90

            #majority sail
            elif not(start) and not(moving):
                #if not moving and behind 75% and sail back
                if self.SK_line_check(wanted_arr[2:3], wanted_arr[-3:]):
                    moving = True
                    boat.goToGPS(wanted_arr[6],wanted_arr[7])  #go to 90
            
            #if past or at 90% (redundence reduction)
            elif not(self.SK_line_check(wanted_arr[4:5], wanted_arr[-3:])):
                moving = False
                boat.adjustSail(90)  #loosen sail, do nuthin


    def SK_perc_guid(self,inp_arr,type_arr,buoy_arr):
        #calc front/back/sides mid point
        #find the parameter lat/long value per percent
        #calc line 75%/80%/90% (give long, if lat) towards front between them
            #input an array of wanted %'s, return array with matching x/y's (in own array, array of arrays)
                #saves on calc times
            #https://www.desmos.com/calculator/wud5cve4bq
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
        mid_arr=[], m_arr=[], b_arr=[]

        # midpoints ==========================
        #   (12,13,34,24);(front,left,back,right)
        #   02,04,46,26
        a = [0, 2, 0, 4, 4, 6, 2, 6]    #optimizing code with for rather then long ass list
        # 0,1, 2,3, 4,5, 6,7
        for i in range(4):  # 0,1,2,3
            #TODO: remove nice variables: just fill in and make two lines (optimization)
            j1 = a[i*2]  # 0 - 0 - 4 - 2
            k1 = j1 +1  # 1 - 1 - 5 - 3
            j2 = a[(i*2) +1]  # 2 - 4 - 6 - 6  next over in "a"
            k2 = j2 +1  # 3 - 5 - 7 - 7

            p = (buoy_arr[j1] + buoy_arr[j2])/2  # 0+1/2: j1,j2
            mid_arr.append(p)   #p
            mid_arr.append(self.SK_f(p, buoy_arr[j1], buoy_arr[k1], buoy_arr[j2], buoy_arr[k2]))    #p,j1,k1,j2,k2
                
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
        m_arr.append(self.SK_m(mid_arr[0],mid_arr[1],mid_arr[4],mid_arr[5]))
        

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
                ret_arr.append( m_arr[0] )      #m
                ret_arr.append( y-m_arr[0]*x )  #b

        ret_arr.append(m_arr[1])
        ret_arr.append(b_arr[1])
        ret_arr.append(m_arr[2])
        #ret_arr.append(b_arr[2])

        return ret_arr

    def SK_line_check(self,Tarr,Barr):
        #TRUE: BEHIND LINE
        #FALSE: AT OR PAST LINE

        #Ix/y:  current location of boat
        #       boat.gps.longitude, boat.gps.latitude
        #Tarr:  m/b compare line
        #arr:   m/b Back line,

        Fa=0;Fb=0;Fc=0  #temp sets
        #check if sideways =========================
        #input x/y as Buoy x/y's to func
        if abs(Barr[3]) < 1: #Barr is secretly the mid m line shhhhhhh
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
        

    def SK_f(self,x,a1,b1,a2,b2): return self.SK_m(a1,b1,a2,b2)*x + self.SK_v(a1,b1,a2,b2)
    def SK_m(self,a1,b1,a2,b2): return (b2-b1)/(a2-a1)
    def SK_v(self,a1,b1,a2,b2): return b1-(self.SK_m(a1,b1,a2,b2)*a1)



    #inputs: B1 long/lat, Radius (boat.event_arr)
    def Search(self):
        #make in boatMain along with mode switch, attach buoy coords and radius in ary
        #will need to redo GUI then ://////
        self.SR_pattern(boat.gps.latitude, boat.gps.longitude, boat.event_arr[0], boat.event_arr[1], boat.event_arr[2])

        while(True):
            #main running
                #blah blah blah


            if self.event_NL(): return  #checks if mode has switched, exits func if so
        
    
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

