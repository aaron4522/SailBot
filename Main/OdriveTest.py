import odrive
import odrive.utils as ut
import constants as c
from time import sleep


class Odrive():
    def __init__(self):
        self.od = odrive.find_any()
        self.axis = self.od.axis0
        self.mo = self.axis.motor
        self.enc = self.axis.encoder

        self.KVRating = c.config['CONSTANTS']['motorKV']
        self.enc.config.cpr = c.config['CONSTANTS']['odriveEncoderCPR']
        self.od.config.brake_resistance = c.config['CONSTANTS']['odrivebreakresistor']
        self.od.axis0.motor.config.pole_pairs = 6 #number of coils / 6
        self.od.axis0.motor.config.torque_constant = 1 # read the getting started guide on this, to be changed later
        self.od.axis0.motor.config.motor_type = 0
        self.current = 40


    @property
    def pos(self):
        return self.axis.encoder.pos_estimate

    @pos.setter
    def pos(self, value):
        self.axis.controller.input_pos = value

    @property
    def vel(self):
        return self.axis.encoder.vel_estimate

    @vel.setter
    def vel(self, value):
        self.axis.controller.input_vel = value

    @property
    def torque(self):
        #this will change current drawn
        return 8.27 * getDrawnCurrent / self.KVRating

    @torque.setter
    def torque(self, value):
        self.axis.controller.input_torque = value

    @property
    def current(self):
        return self.axis.motor.current_control.Iq_measured

    @current.setter
    def current(self, value):
        #this will change torque!!!
        #self.torque = (8.27 * value / self.KVRAting)
        print(F"Warning: Changing the current limit will affect the torque")
        self.mo.config.current_lim = value

    def getDemandedCurrent(self):
        self.axis.motor.current_control.Iq_setpoint

if __name__ == '__main__':
    drv = Odrive()
    
    drv.current = 1
    #drv.axis.requested_state = 1 #IDLE
    sleep(1)
    drv.axis.requested_state = 3 #CALIBRATION
    sleep(15)
    ut.dump_errors(drv.od)
    drv.axis.requested_state = 8 
    drv.pos = 1
    sleep(1)
    drv.pos = 2
    print('done')
       
