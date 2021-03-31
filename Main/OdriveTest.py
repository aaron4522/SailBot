import odrive
import odrive.utils as ut
import constants as c
from time import sleep


class Odrive():
    def __init__(self):
        self.od = odrive.find_any()
        self.KVRating = c.config['CONSTANTS']['motorKV']
        self.od.config.brake_resistance = c.config['CONSTANTS']['odrivebreakresistor']

        self.axis0 = self.od.axis0
        self.mo0 = self.axis0.motor
        self.enc0 = self.axis0.encoder

        self.enc0.config.cpr = c.config['CONSTANTS']['odriveEncoderCPR0']
        self.od.axis0.motor.config.pole_pairs = c.config['CONSTANTS']['odrivepolepairs0']
        self.od.axis0.motor.config.torque_constant = 1 # read the getting started guide on this, to be changed later
        self.od.axis0.motor.config.motor_type = 0

        # Axis 1

        self.axis1 = self.od.axis1
        self.mo1 = self.axis1.motor
        self.enc1 = self.axis1.encoder

        self.enc1.config.cpr = c.config['CONSTANTS']['odriveEncoderCPR1']
        self.od.axis1.motor.config.pole_pairs = c.config['CONSTANTS']['odrivepolepairs1']
        self.od.axis1.motor.config.torque_constant = 1 # read the getting started guide on this, to be changed later
        self.od.axis1.motor.config.motor_type = 0

        self.axis1.controller.config.vel_limit = self.axis0.controller.config.vel_limit

        # self.axis1.controller.config.pos_gain = c.config['CONSTANTS']['posGain']
        # self.axis1.controller.config.vel_gain = c.config['CONSTANTS']['velGain']
        # self.axis1.controller.config.vel_integrator_gain = c.config['CONSTANTS']['velIntegratorGain']

        self.current = 20
        #self.enc0.config.calib_scan_distance *= 4

        #print(F"!!!! {self.enc0.config.calib_scan_distance}")
        
    @property
    def pos0(self):
        return self.axis0.encoder.pos_estimate

    @pos0.setter
    def pos0(self, value):
        self.axis0.controller.input_pos = value

    @property
    def vel0(self):
        return self.axis0.encoder.vel_estimate

    @vel0.setter
    def vel0(self, value):
        self.axis0.controller.input_vel = value

    @property
    def torque0(self):
        #this will change current drawn
        return 8.27 * getDrawnCurrent / self.KVRating

    @torque0.setter
    def torque0(self, value):
        self.axis0.controller.input_torque = value

    @property
    def current0(self):
        return self.axis0.motor.current_control.Iq_measured

    @current0.setter
    def current0(self, value):
        #this will change torque!!!
        #self.torque = (8.27 * value / self.KVRAting)
        #print(F"Warning: Changing the current limit will affect the torque")
        self.mo0.config.current_lim = value

    def getDemandedCurrent0(self):
        self.axis0.motor.current_control.Iq_setpoint



    @property
    def pos1(self):
        return self.axis1.encoder.pos_estimate

    @pos1.setter
    def pos1(self, value):
        self.axis1.controller.input_pos = value

    @property
    def vel1(self):
        return self.axis1.encoder.vel_estimate

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
        return self.axis1.motor.current_control.Iq_measured

    @current1.setter
    def current1(self, value):
        #this will change torque!!!
        #self.torque = (8.27 * value / self.KVRAting)
        #print(F"Warning: Changing the current limit will affect the torque")
        self.mo1.config.current_lim = value

    def getDemandedCurrent1(self):
        self.axis1.motor.current_control.Iq_setpoint

if __name__ == '__main__':
    drv = Odrive()

    drv.current = 20
    #drv.axis.requested_state = 1 #IDLE
    #sleep(1)
    drv.axis0.requested_state = 3 #CALIBRATION
    sleep(15)
    
    ut.dump_errors(drv.od)
    drv.axis0.requested_state = 8 
    sleep(1)
    for i in range(5):
        drv.pos0 = 0
        sleep(3)
        drv.pos0 = 5
        sleep(3)
        ut.dump_errors(drv.od)

    # drv.axis1.requested_state = 3 #CALIBRATION
    # sleep(15)
    
    # ut.dump_errors(drv.od)
    # drv.axis1.requested_state = 8 
    # sleep(1)
    # for i in range(5):
    #     drv.pos1 = 0
    #     sleep(3)
    #     drv.pos1 = 5
    #     sleep(3)
    #     ut.dump_errors(drv.od)
    

    # print('done')
       
