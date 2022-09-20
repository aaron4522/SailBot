
#from messages_pb2 import *
import serial
import constants as c

class arduino:

    def __init__(self, port_num):
        self.ser1 = serial.Serial(port_num, c.config['MAIN']['baudrate'], timeout = .5) 


    def send(self, data):
        print(data)
        self.ser1.write(str(data).encode())

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
    ardu = arduino("/dev/ttyACM0")
    while True:
        print(ardu.read())

