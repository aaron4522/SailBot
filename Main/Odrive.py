import odrive
import odrive.utils as ut
import constants as c
from time import sleep
import sys


class Odrive():
    def __init__(self, calibrate = False):
        print("Start")
        self.od = odrive.find_any()
        self.setConstants()
        

        if calibrate:
            print("calibrating")
            self.reboot()
            self.axis0.requested_state = 3
            sleep(15)
            ut.dump_errors(self.od)
            #CALIBRATION = 3, can be avoided, see how to in list of axisStates
            
            # self.axis0.motor.config.pre_calibrated = False
            # sleep(.1)
            # self.axis0.requested_state = 4
            # sleep(10)
            # ut.dump_errors(self.od)
            # self.axis0.motor.config.pre_calibrated = True
            # try:
            #     self.od.save_configuration()
            # except:
            #     #an exception will be thrown, this is expected
            #     pass

            # self.od = odrive.find_any()
            # self.setConstants()
            
            # self.axis0.requested_state = 2
            # ut.dump_errors(self.od)
            # sleep(1)
            # self.axis0.requested_state = 7
            # sleep(15)

        

        #self.reboot()

        self.axis0.requested_state = 8 
        ut.dump_errors(self.od)
        sleep(.1)

    def reboot(self):
        try:
            self.od.reboot()
            pass
        except:
            #error is expected
            pass
        sleep(2)
        self.od = odrive.find_any()
        self.setConstants()

    def setConstants(self):
        self.KVRating = c.config['ODRIVE']['motorKV']
        #self.od.config.brake_resistance = c.config['CONSTANTS']['odrivebreakresistor']

        self.axis0 = self.od.axis0
        self.mo0 = self.axis0.motor
        self.enc0 = self.axis0.encoder

        self.axis0.controller.config.enable_overspeed_error = False
        self.enc0.config.cpr = c.config['ODRIVE']['odriveEncoderCPR0']
        self.od.axis0.motor.config.pole_pairs = c.config['ODRIVE']['odrivepolepairs0']
        self.od.axis0.motor.config.torque_constant = 1 # read the getting started guide on this, to be changed later
        self.od.axis0.motor.config.motor_type = 0
        
        self.axis0.controller.config.vel_limit = c.config['ODRIVE']['velLimit']
        self.axis0.controller.config.pos_gain = c.config['ODRIVE']['posGain']
        self.axis0.controller.config.vel_gain = c.config['ODRIVE']['velGain']
        self.axis0.controller.config.vel_integrator_gain = c.config['ODRIVE']['velIntegratorGain']
        self.current0 = c.config['ODRIVE']['currentLimit']

    @property
    def pos(self):
        return (self.pos0, self.pos1)

    @pos.setter
    def pos(self, axis, value):
        if axis == self.axis0:
            self.axis0.controller.input_pos = value
        elif axis == self.axis1:
            self.axis1.controller.input_pos = value

    @property
    def vel(self):
        return (self.vel0, self.vel1)

    @vel.setter
    def vel(self, axis, value):
        if axis == self.axis0:
            self.vel0 = value
        elif axis == self.axis1:
            self.vel1 = value

    @property
    def torque(self):
        #this will change current drawn
        return 8.27 * getDrawnCurrent / self.KVRating

    @torque.setter
    def torque(self, axis, value):
        if axis == self.axis0:
            self.torque0 = value
        elif axis == self.axis1:
            self.torque1 = value

    @property
    def current(self):
        return (self.current0, self.current1)

    @current.setter
    def current(self, axis, value):
        #this will change torque!!!
        #self.torque = (8.27 * value / self.KVRAting)
        #print(F"Warning: Changing the current limit will affect the torque")
        if axis == self.axis0:
            self.current0 = value
        elif axis == self.axis1:
            self.current1 = value

    def getDemandedCurrent(self):
        return (self.getDemandedCurrent0(), self.getDemandedCurrent1())
        
    @property
    def pos0(self):
        return self.axis0.encoder.pos_estimate

    @pos0.setter
    def pos0(self, value):
        self.axis0.controller.input_pos = value

    @property
    def vel0(self):
        return self.axis0.controller.config.vel_limit
        #return self.axis0.controller.input_vel

    @vel0.setter
    def vel0(self, value):
        self.axis0.controller.config.vel_limit = value

    @property
    def torque0(self):
        #this will change current drawn
        return self.axis0.controller.input_torque

    @torque0.setter
    def torque0(self, value):
        self.axis0.controller.input_torque = value

    @property
    def current0(self):
        return self.mo0.config.current_lim

    @current0.setter
    def current0(self, value):
        #this will change torque!!!
        #self.torque = (8.27 * value / self.KVRAting)
        #print(F"Warning: Changing the current limit will affect the torque")
        if int(value) > 65:
            raise Exception("Motor current limit should not be raised this high without verifying the motor can handle it")
        self.mo0.config.current_lim = value

    def getDemandedCurrent0(self):
        return self.axis0.motor.current_control.Iq_setpoint



    @property
    def pos1(self):
        return self.axis1.encoder.pos_estimate

    @pos1.setter
    def pos1(self, value):
        self.axis1.controller.input_pos = value

    @property
    def vel1(self):
        return self.axis1.controller.input_vel

    @vel1.setter
    def vel(self, value):
        self.axis1.controller.input_vel = value

    @property
    def torque1(self):
        #this will change current drawn
        return 8.27 * getDrawnCurrent / self.KVRating

    @torque1.setter
    def torque1(self, value):
        self.axis1.controller.input_torque = value

    @property
    def current1(self):
        return self.mo1.config.current_lim

    @current1.setter
    def current1(self, value):
        #this will change torque!!!
        #self.torque = (8.27 * value / self.KVRAting)
        #print(F"Warning: Changing the current limit will affect the torque")
        if int(value) > 65:
            raise Exception("Motor current limit should not be raised this high without verifying the motor can handle it")
        self.mo1.config.current_lim = value

    def getDemandedCurrent1(self):
        return self.axis1.motor.current_control.Iq_setpoint

def printCurrent(drv):
    while True:
        print(abs(drv.getDemandedCurrent0()))
        sleep(.5)

if __name__ == '__main__':
    #print(c.config.keys())
    #print(sys.argv)
    print("Run as sudo if on rasp pi, will othewise get error")
    if len(sys.argv) < 2 or sys.argv[1] != '0':
        try:
            #odrive.find_any().reboot()
            #sleep(2)
            pass
        except:
            pass
        
        
        drv = Odrive(calibrate=True)
    
        

    else:
        drv = Odrive()

    
    for i in range(1):
        drv.pos0 = 5
        sleep(3)
        drv.pos0 = 0
        sleep(3)
    ut.dump_errors(drv.od)






    # from threading import Thread
    # from time import sleep
    # pump_thread = Thread(target=printCurrent, args=[drv])
    # pump_thread.start()
    try:
        while True:
            string = input("  > Enter Input:")

            if string.startswith("pi") or string.startswith("PI"):
                if len(string) == 2:
                    print(drv.axis0.controller.config.pos_gain)
                else:
                    val = float(string[2:])
                    print(drv.axis0.controller.config.pos_gain, "->", val)
                    drv.axis0.controller.config.pos_gain = val
            
            elif string[0] == "p" or string[0] == 'P':
                if len(string) == 1:
                    print(drv.pos0)
                else:
                    val = float(string[1:])
                    print(drv.pos0, "->", val)
                    drv.pos0 = val

            elif string[0] == "v" or string[0] == 'V':
                if len(string) == 1:
                    print(drv.vel0)
                else:
                    val = float(string[1:])
                    print(drv.vel0, "->", val)
                    drv.vel0 = val

            elif string[0] == "c" or string[0] == 'C':
                if len(string) == 1:
                    print(F"{drv.getDemandedCurrent0()} ({drv.current0})")
                else:
                    val = float(string[1:])
                    print(drv.current0, "->", val)
                    drv.current0 = val

            elif string[0] == "d" or string[0] == 'D':
                if len(string) == 1:
                    print(drv.axis0.controller.config.vel_integrator_gain)
                else:
                    val = float(string[1:])
                    print(drv.axis0.controller.config.vel_integrator_gain, "->", val)
                    drv.axis0.controller.config.vel_integrator_gain = val

            elif string[0] == "i" or string[0] == 'I':
                if len(string) == 1:
                    print(drv.axis0.controller.config.vel_gain)
                else:
                    val = float(string[1:])
                    print(drv.axis0.controller.config.vel_gain, "->", val)
                    drv.axis0.controller.config.vel_gain = val

            elif string[0] == "r" or string[0] == 'R':
                print("rebooting")
                drv.reboot()
                drv = Odrive(calibrate=True)

            elif string[0] == "e" or string[0] == 'E':
                ut.dump_errors(drv.od)


            


            else:
                val = float(string)
                drv.pos0 = val
    except KeyboardInterrupt as e:
        ut.dump_errors(drv.od)

    print('done')
       
