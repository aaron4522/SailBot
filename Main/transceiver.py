
#from messages_pb2 import *
import serial
import constants as c
import sys
import smbus2 as smbus#,smbus2
import time

I2C_SLAVE_ADDRESS = 11 #0x0b ou 11

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
        print(data)
        self.ser1.write(str(data).encode())

    def readSailPos(self):
        pass

    def readRudderPos(self):
        BytesToSend = ConvertStringsToBytes('R')
        print("Sent " + str(I2C_SLAVE_ADDRESS) + " the " + str(cmd) + " command.")
        print(BytesToSend )
        self.I2Cbus.write_i2c_block_data(I2C_SLAVE_ADDRESS, 0x00, BytesToSend)

        while True:
            try:
                data=self.I2Cbus.read_i2c_block_data(I2C_SLAVE_ADDRESS,0x00,16)
                print(F"recieve from slave: {data}")
                return data
            except:
                print("remote i/o error")
                time.sleep(0.5)

    def read(self):
        message = str(self.ser1.readline()).replace("\r\n'", "").replace("b'", "").replace("\\r\\n'", "")
        
        return str(message)

        pbm = BaseToBoat.parseFromString(message)

        case = pbm.WhichOneOf('command')
        if case == 'rudder' :
            result = ["rudder " + pbm.RudderCommand.position]
        elif case == 'sail' :
            result = ["sail " + pbm.SailCommand.position]
        elif case == 'skipper' :
            result = ["sail " + pbm.SkipperCommand.sailPosition, "rudder " + pbm._SkipperCommand.rudderPosition]
        elif case == 'mode' :
            result = ["mode " + pbm.Mode.mode]

        return result


if __name__ == "__main__":
    ardu = arduino(c.config['MAIN']['ardu_port'])
    while True:
        #print(ardu.read())
        print("read: ", ardu.readRudderPos())

