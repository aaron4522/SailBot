"""
reads and sends data from the connected USB transceiver
"""
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
        # connect to device on 'port_num'
        self.ser1 = serial.Serial(port_num, c.config['MAIN']['baudrate'], timeout = .5) 
        self.I2Cbus = smbus.SMBus(1)

    def send(self, data):
        #print(data)
        self.ser1.write(str(data).encode())

    def readData(self):
        # get data from transceiver
        self.send("?") # transceiver is programmed to respond to '?' with its data
        msgs = []
        msg = self.read()
        if msg == None or msg == "'":
            time.sleep(.1)
            msg = self.read()
            if msg == None or msg == "'":
                self.send("?")
                msg = self.read()
        splits = msg.split(" ")
        return [F"{splits[0]} {splits[1]}", F"{splits[2]} {splits[3]}"] # format data
    
                
        

    def read(self):
        message = str(self.ser1.readline()).replace("\r\n'", "").replace("b'", "").replace("\\r\\n'", "")
        
        return str(message)


if __name__ == "__main__":
    print("start")
    try:
        ardu = arduino(c.config['MAIN']['ardu_port'])
        if ardu.readData() == "'":
            #print("error:", ardu.readData())
            raise Exception("could not read arduino data")
    except:
        ardu = arduino(c.config['MAIN']['ardu_port2'])
        if ardu.readData() == "'":
            #print("error:", ardu.readData())
            raise Exception("could not read arduino data")
    
    time.sleep(1)
    print("start2")
    while True:
        print(ardu.readData())

