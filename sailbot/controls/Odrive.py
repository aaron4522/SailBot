"""
calibrates and default values for Odrive and handles interfacing between Odrive and python code
"""
# TODO: Finish merging
from time import sleep
import sys
import logging
import odrive
import odrive.utils as ut

from sailbot import constants as c


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

        self.enc.config.cpr = c.config['ODRIVE_SAIL']['odriveEncoderCPR']
        self.od.axis.motor.config.pole_pairs = c.config['ODRIVE_SAIL']['odrivepolepairs']

        self.od.axis.motor.config.torque_constant = 1  # read the getting started guide on this, to be changed later
        self.od.axis.motor.config.motor_type = 0

        self.KVRating = int(c.config['ODRIVE']['motorKV'])
        self.current_limit = int(c.config['ODRIVE']['currentLimit'])

        self.axis.controller.config.enable_overspeed_error = False
        self.od.config.brake_resistance = float(c.config['CONSTANTS']['odrivebreakresistor'])

        if preset == "sail":
            self.axis.controller.config.pos_gain = int(c.config['ODRIVE_SAIL']['posGain'])

            self.axis.controller.config.vel_gain = float(c.config['ODRIVE_SAIL']['velGain'])
            self.axis.controller.config.vel_limit = float(c.config['ODRIVE_SAIL']['velLimit'])
            self.axis.controller.config.vel_integrator_gain = int(c.config['ODRIVE_SAIL']['velIntegratorGain'])

            # TODO: Add odrive rotations float(c.config['ODRIVE_SAIL']['odriveRotations'])

        elif preset == "rudder":
            self.axis.controller.config.pos_gain = int(c.config['ODRIVE_SAIL']['posGain'])

            self.axis.controller.config.vel_gain = float(c.config['ODRIVE_RUDDER']['velGain'])
            self.axis.controller.config.vel_limit = float(c.config['ODRIVE_RUDDER']['velLimit'])
            self.axis.controller.config.vel_integrator_gain = int(c.config['ODRIVE_RUDDER']['velIntegratorGain'])

        elif preset is not None:
            raise ValueError("Trying to load an undefined preset!")

        else:
            # Default fallback values when no preset is defined
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
    def current_limit(self):
        return self.mo.config.current_lim

    @current_limit.setter
    def current_limit(self, value):
        # this will change torque!!!
        # self.torque = (8.27 * value / self.KVRAting)
        if value > 65:
            raise ValueError("Motor current limit should not be raised this high without verifying the motor can handle it")
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
    print("Run as sudo if on rasp pi, will otherwise not work")
    if len(sys.argv) < 2 or sys.argv[1] != '0':
        drv = Odrive(calibrate=True)
    else:
        drv = Odrive()

    p0_offset = 0
    p1_offset = 0
    while True:
        try:
            while True:
                string = input("  > Enter Input:")

                if string == "calibrate":
                    # print("rebooting")
                    # drv.reboot()
                    drv = Odrive(calibrate=True)

                elif string.startswith("pi0") or string.startswith("PI0"):
                    if len(string.split(' ')) == 1:
                        print(drv.axis0.controller.config.pos_gain)
                    else:
                        val = float(string.split(' ')[1])
                        print(drv.axis0.controller.config.pos_gain, "->", val)
                        drv.axis0.controller.config.pos_gain = val

                elif string.startswith("pi1") or string.startswith("PI1"):
                    if len(string.split(' ')) == 1:
                        print(drv.axis1.controller.config.pos_gain)
                    else:
                        val = float(string.split(' ')[1])
                        print(drv.axis1.controller.config.pos_gain, "->", val)
                        drv.axis1.controller.config.pos_gain = val

                elif string.lower().startswith("p0"):
                    if len(string.split(' ')) == 1:
                        print(drv.pos0 + p0_offset)
                    else:
                        val = float(string.split(' ')[1])
                        print(drv.pos0 + p0_offset, "->", val)
                        drv.pos0 = val + p0_offset

                elif string.lower().startswith("pr"):
                    if len(string.split(' ')) == 1:
                        print(drv.pos0 + p0_offset)
                    else:
                        val = float(string.split(' ')[1])
                        print(drv.pos0 + p0_offset, "->", val, "(resetting to 0 in 1 sec)")
                        drv.pos0 = val + p0_offset
                        lastRudderMoveVal = val

                        def rudderReset(*args):
                            sleep(1)
                            drv.pos0 = p0_offset

                        threading.Thread(target=rudderReset).start()

                elif string.lower().startswith("z"):
                    print(drv.pos0 + p0_offset, "->", lastRudderMoveVal, "(resetting to 0 in 1 sec)")
                    drv.pos0 = lastRudderMoveVal + p0_offset

                    def rudderReset(*args):
                            sleep(1)
                            drv.pos0 = p0_offset

                    threading.Thread(target=rudderReset).start()

                elif string.lower().startswith("ps"):
                    if len(string.split(' ')) == 1:
                        print(drv.pos1 + p1_offset)
                    else:
                        val = float(string.split(' ')[1])
                        print(drv.pos1 + p1_offset, "->", val)
                        drv.pos1 = val + p1_offset

                elif string.lower().startswith("or"):
                    # val = float(string.split(' ')[1])
                    p0_offset = drv.pos0 + p0_offset
                    print("offset is", p0_offset)

                elif string.lower().startswith("os"):
                    # val = float(string.split(' ')[1])
                    p1_offset = drv.pos0 + p0_offset
                    print("offset is", p0_offset)

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

                elif string.lower().startswith("d0"):
                    if len(string.split(' ')) == 1:
                        print(drv.axis0.controller.config.vel_integrator_gain)
                    else:
                        val = float(string.split(' ')[1])
                        print(drv.axis0.controller.config.vel_integrator_gain, "->", val)
                        drv.axis0.controller.config.vel_integrator_gain = val

                elif string.lower().startswith("d1"):
                    if len(string.split(' ')) == 1:
                        print(drv.axis1.controller.config.vel_integrator_gain)
                    else:
                        val = float(string.split(' ')[1])
                        print(drv.axis1.controller.config.vel_integrator_gain, "->", val)
                        drv.axis1.controller.config.vel_integrator_gain = val

                elif string.lower().startswith("i0"):
                    if len(string.split(' ')) == 1:
                        print(drv.axis0.controller.config.vel_gain)
                    else:
                        val = float(string.split(' ')[1])
                        print(drv.axis0.controller.config.vel_gain, "->", val)
                        drv.axis0.controller.config.vel_gain = val

                elif string.lower().startswith("i1"):
                    if len(string.split(' ')) == 1:
                        print(drv.axis1.controller.config.vel_gain)
                    else:
                        val = float(string.split(' ')[1])
                        print(drv.axis1.controller.config.vel_gain, "->", val)
                        drv.axis1.controller.config.vel_gain = val

                elif string == "reset":
                    print("rebooting")
                    drv.reboot()
                    drv = Odrive(calibrate=False)



                elif string[0] == "e" or string[0] == 'E':
                    ut.dump_errors(drv.od)





                else:
                    val = float(string)
                    drv.pos0 = val
                    drv.pos1 = val
        except KeyboardInterrupt as e:
            ut.dump_errors(drv.od)
            break
        except Exception as e:
            print(F"Error: {e}")
            print(traceback.format_exc())

    print('done')
       
