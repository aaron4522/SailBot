"""
calibrates and default values for Odrive and handles interfacing between Odrive and python code
"""
from time import sleep
import sys
import logging
import odrive
import odrive.utils as ut

try:
    import constants as c
except:
    import sailbot.constants as c


class Odrive:
    # TODO: (TOM) fill in documentation (I'm only including public facing vars so delete anything if the user doesn't need to know about it)
    """
    Controls the ODrive motors which move the sails and rudder
    Attributes:
        - pos (type): desc
        - vel (type): desc
        - torque (type): desc
        - current (type): desc
    Functions:
        - reboot(): desc
        - calibrate(): desc
    """
    def __init__(self, preset=None):
        """
        Args:
            preset (str): pre-defined configurations for 2023's competition
                - Supports either 'sail' or 'rudder'
        """
        logging.info(f"Initializing ODrive with preset: {preset}")
        self.od = odrive.find_any()

        self.axis = self.od.axis
        self.mo = self.axis.motor
        self.enc = self.axis.encoder

        # TODO: (TOM) if any of these constants are unique for the sail/rudder then add them inside the if/else
        self.KVRating = c.config['ODRIVE']['motorKV']
        # self.od.config.brake_resistance = c.config['CONSTANTS']['odrivebreakresistor']
        self.axis.controller.config.enable_overspeed_error = False
        self.current = c.config['ODRIVE']['currentLimit']

        # TODO: (TOM) move whichever presets are the same for sail and rudder outside of the if/else
        if preset == "sail":
            self.enc.config.cpr = c.config['ODRIVE_SAIL']['odriveEncoderCPR']
            self.od.axis.motor.config.pole_pairs = c.config['ODRIVE_SAIL']['odrivepolepairs']
            self.od.axis.motor.config.torque_constant = 1  # read the getting started guide on this, to be changed later
            self.od.axis.motor.config.motor_type = 0

            self.axis.controller.config.vel_limit = c.config['ODRIVE']['velLimit']
            self.axis.controller.config.pos_gain = c.config['ODRIVE']['posGain']
            self.axis.controller.config.vel_gain = c.config['ODRIVE']['velGain']
            self.axis.controller.config.vel_integrator_gain = c.config['ODRIVE']['velIntegratorGain']

        elif preset == "rudder":
            self.enc.config.cpr = c.config['ODRIVE_RUDDER']['odriveEncoderCPR']
            self.od.axis.motor.config.pole_pairs = c.config['ODRIVE_RUDDER']['odrivepolepairs']
            self.od.axis.motor.config.torque_constant = 1  # read the getting started guide on this, to be changed later
            self.od.axis.motor.config.motor_type = 0

            self.axis.controller.config.vel_limit = c.config['ODRIVE']['velLimit']
            self.axis.controller.config.pos_gain = c.config['ODRIVE']['posGain']
            self.axis.controller.config.vel_gain = c.config['ODRIVE']['velGain']
            self.axis.controller.config.vel_integrator_gain = c.config['ODRIVE']['velIntegratorGain']

        elif preset is not None:
            raise ValueError("Trying to load an undefined preset!")

        else:
            # Default fallback values when no preset is defined
            # TODO: (Aaron) add __init__ args to have the user define odrive values
            raise NotImplementedError("Non-preset fallback values haven't been coded yet")

        self.axis.requested_state = 8
        ut.dump_errors(self.od)
        sleep(.1)

    def reboot(self):
        # TODO: (TOM) reboot won't work with new implementation (no more setConstants())
            # is this ok?
        try:
            self.od.reboot()
        except:
            #error is expected
            pass
        sleep(2)
        self.od = odrive.find_any()
        self.setConstants()

    def calibrate(self):
        print("Calibrating")
        self.reboot()
        self.axis.requested_state = 3
        sleep(15)
        ut.dump_errors(self.od)

    @property
    def pos(self):
        return self.axis.encoder.pos_estimate

    @pos.setter
    def pos(self, value):
        # TODO: (TOM) is try except needed? why not let error get raised?
            # Do exceptions occur during normal behavior?
        try:
            self.axis.controller.input_pos = value
        except Exception as e:
            print(F"Error setting axis0 to {value}")
        self.pos = value

    @property
    def vel(self):
        return self.axis.controller.config.vel_limit
        # return self.axis0.controller.input_vel

    @vel.setter
    def vel(self, value):
        self.axis.controller.config.vel_limit = value

    @property
    def torque(self):
        #this will change current drawn
        # TODO: (TOM) which return statement?
            # getDrawnCurrent typo? or different from getDemandedCurrent()?
        return 8.27 * getDrawnCurrent / self.KVRating # Used by torque and torque0
        return self.axis.controller.input_torque # Used by torque1

    @torque.setter
    def torque(self, value):
        self.axis.controller.input_torque = value

    @property
    def current(self):
        return self.mo.config.current_lim

    @current.setter
    def current(self, value):
        # this will change torque!!!
        # self.torque = (8.27 * value / self.KVRAting)
        if value > 65:
            raise Exception("Motor current limit should not be raised this high without verifying the motor can handle it")
        else:
            self.mo.config.current_lim = value

    def getDemandedCurrent(self):
        return self.axis.motor.current_control.Iq_setpoint


def printCurrent(drv):
    while True:
        print(abs(drv.getDemandedCurrent()))
        sleep(.5)


# TODO: (Aaron) Update
if __name__ == '__main__':
    #print(c.config.keys())
    #print(sys.argv)
    print("Run as sudo if on rasp pi, will otherwise not work")
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
        drv.pos1 = 5
        sleep(3)
        drv.pos0 = 0
        drv.pos1 = 0
        sleep(3)
    ut.dump_errors(drv.od)


    try:
        while True:
            string = input("  > Enter Input:")

            if string.startswith("pi") or string.startswith("PI"):
                if len(string) == 2:
                    print(drv.axis.controller.config.pos_gain)
                else:
                    val = float(string[2:])
                    print(drv.axis.controller.config.pos_gain, "->", val)
                    drv.axis.controller.config.pos_gain = val
            
            elif string[0] == "p" or string[0] == 'P':
                if len(string) == 1:
                    print(drv.pos)
                else:
                    val = float(string[1:])
                    print(drv.pos, "->", val)
                    drv.pos = val

            elif string[0] == "v" or string[0] == 'V':
                if len(string) == 1:
                    print(drv.vel)
                else:
                    val = float(string[1:])
                    print(drv.vel, "->", val)
                    drv.vel = val

            elif string[0] == "c" or string[0] == 'C':
                if len(string) == 1:
                    print(F"{drv.getDemandedCurrent()} [{drv.current}]")
                else:
                    val = float(string[1:])
                    print(drv.current, "->", val)
                    drv.current = val

            elif string[0] == "d" or string[0] == 'D':
                if len(string) == 1:
                    print(drv.axis.controller.config.vel_integrator_gain)
                else:
                    val = float(string[1:])
                    print(drv.axis.controller.config.vel_integrator_gain, "->", val)
                    drv.axis.controller.config.vel_integrator_gain = val
                    drv.axis1.controller.config.vel_integrator_gain = val

            elif string[0] == "i" or string[0] == 'I':
                if len(string) == 1:
                    print(drv.axis1.controller.config.vel_gain)
                else:
                    val = float(string[1:])
                    print(drv.axis.controller.config.vel_gain, "->", val)
                    drv.axis.controller.config.vel_gain = val
                    drv.axis1.controller.config.vel_gain = val

            elif string[0] == "r" or string[0] == 'R':
                print("rebooting")
                drv.reboot()
                drv = Odrive(calibrate=True)

            elif string[0] == "e" or string[0] == 'E':
                ut.dump_errors(drv.od)


            


            else:
                val = float(string)
                drv.pos0 = val
                drv.pos1 = val
    except KeyboardInterrupt as e:
        ut.dump_errors(drv.od)

    print('done')
       
