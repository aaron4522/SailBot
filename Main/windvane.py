
from time import sleep
from threading import Thread, Lock
from queue import Queue
import board
from RPi import GPIO
from adafruit_seesaw import seesaw, rotaryio, digitalio
import constants as c


class windVane():

    def __init__(self):

        self.stepsPerRev = 256

        self.clk = 17
        self.dt = 18
        self.hef = 23
        
        

    
        #self.q = Queue(0)
        
        self.saw = seesaw.Seesaw (board.I2C(), 0x36)
        self.encoder = rotaryio.IncrementalEncoder(self.saw)
        self.lock = Lock()
        GPIO.setmode(GPIO.BCM)
        #GPIO.setup(self.clk, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
        #GPIO.setup(self.dt, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
        GPIO.setup(self.hef, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        self.offset = 0
        self.counter = 0
        #self.clkLastState = GPIO.input(self.clk)
        #pump_thread = Thread(target=self.run)
        #pump_thread.start()
        
        #pump_thread2 = Thread(target=self.flush_queue)
        #pump_thread2.start()
        

    def map(self, x, min1, max1, min2, max2):
        x = min(max(x, min1), max1)
        return min2 + (max2-min2)*((x-min1)/(max1-min1))

    @property
    def angle(self):
        counter = self.position
        while (counter < 0):
            counter += self.stepsPerRev

        counter = counter % self.stepsPerRev
        return self.map(counter, 0, self.stepsPerRev-1, 0, 359)
  
    @property
    def position(self):
        self.lock.acquire()
        self.checkHef()
        val =  int( ((self.encoder.position * (360/self.stepsPerRev)) - self.offset)%360 )
        self.lock.release()
        return val

    @property
    def noGoMin(self):
        return 360 - int(c.config['CONSTANTS']['noGoAngle'])/2

    @property
    def noGoMax(self):
        return int(c.config['CONSTANTS']['noGoAngle'])/2
    """    
    def flush_queue(self):
        while True:
            self.counter += self.q.get()
    """
    def run(self):
        while True:
            self.lock.acquire()
            val = self.checkHef()
            self.lock.release()
            if not val:
                sleep(.1)

    def checkHef(self):
        hefState = GPIO.input(self.hef)
        if hefState == False:             
            self.offset = int( (self.encoder.position * 1.8)%360)
            return False
        return True

    """
    def update(self):
        
        clkState = GPIO.input(self.clk)
        dtState = GPIO.input(self.dt)
        hefState = GPIO.input(self.hef)
        if clkState != self.clkLastState:

            if dtState != clkState:

                self.q.put_nowait(1)
                
            else:
                self.q.put_nowait(-1)

            self.clkLastState = clkState
        if hefState == False:
            self.counter = 0
       """     
        
if __name__ == '__main__':
    wv = windVane()
    while True:
        sleep(.1)
        print(F"Angle {wv.position}")
    
