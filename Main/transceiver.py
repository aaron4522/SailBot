
#from messages_pb2 import *
import serial
import constants as c
import sys
import smbus2 as smbus#,smbus2
import time

I2C_SLAVE_ADDRESS = 0x10

def ConvertStringsToBytes(src):
  converted = []
  for b in src:
    converted.append(ord(b))
  return converted

class arduino:

    def __init__(self, port_num):
        self.ser1 = serial.Serial(port_num, c.config['MAIN']['baudrate'], timeout = .5) 
        self.I2Cbus = smbus.SMBus(1)

    def send(self, data):
        #print(data)
        self.ser1.write(str(data).encode())

    def readData(self):
        self.send("?")
        msgs = []
        msg = self.read()
        while msg != None and msg != "'":
            msgs.append(msg)
            msg = self.read()
        return msgs
    
                
        

    def read(self):
        message = str(self.ser1.readline()).replace("\r\n'", "").replace("b'", "").replace("\\r\\n'", "")
        
        return str(message)


if __name__ == "__main__":
    print("start")
    try:
        ardu = arduino(c.config['MAIN']['ardu_port'])
    except:
        ardu = arduino(c.config['MAIN']['ardu_port2'])
    time.sleep(1)
    print("start2")
    while True:
        print(ardu.readRudderPos())
        time.sleep(1)

