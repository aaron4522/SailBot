#sudo pip3 install adafruit-circuitpython-lis2mdl


try:
    import time
    import board
    import busio
    import adafruit_lis2mdl
    #from Thread import thread

except:
    print("Code must be run on rasp pi, requires GPIO")
    from sys import exit
    exit(0)

class:

    def __init__(self):
        i2c = busio.I2C(board.SCL, board.SDA)
        sensor = adafruit_lis2mdl.LIS2MDL(i2c)
        # pump_thread = Thread(target=self.run)
        # pump_thread.start()

    def run(self):
        pass

    @property
    def vector(self):
        return sensor.magnetic # (mag_x, mag_y, mag_z)
        

    


