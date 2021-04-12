<<<<<<< HEAD
#from messages_pb2 import *
import serial
import constants as c

class arduino:

    def __init__(self, port_num):
        self.ser1 = serial.Serial(port_num, c.config['MAIN']['baudrate']) 


    def send(self, data):
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

=======
#from messages_pb2 import *
import constants as C

class arduino:

	def __init__(self, port_num):
		self.ser1 = serial.Serial('COM'+port_num, c.config['MAIN']['baudrate']) 


	def send(self, data):
		self.ser1.write(str(data).encode())

	def read(self):
		message = self.ser1.readline()

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

>>>>>>> 3db36562af7c80ae34beffeaa526e522005367b5
