from RPi import GPIO
from time import sleep

class windVane():

	def __init__(self):

		self.stepsPerRev = 256

		self.clk = 17
		self.dt = 18

		GPIO.setmode(GPIO.BCM)
		GPIO.setup(self.clk, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
		GPIO.setup(self.dt, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)

		self.counter = 0
		self.clkLastState = GPIO.input(self.clk)

		pump_thread = Thread(target=self.run)
		pump_thread.start()

	def map(self, x, min1, max1, min2, max2):
		x = min(max(x, min1), max1)
		return min2 + (max2-min2)*((x-min1)/(max1-min1))

	@property
	def angle(self):
		counter = self.counter

		while (counter < 0):
			counter += self.stepsPerRev

		counter = counter % self.stepsPerRev
		return self.map(counter, 0, stepsPerRev-1, 0, 359)

	

	def run(self):
		try:
			while True:
				self.update()

		finally:
			GPIO.cleanup()

	def update(self):
		clkState = GPIO.input(clk)
		dtState = GPIO.input(dt)
		if clkState != clkLastState:

			if dtState != clkState:
				counter += 1
			else:
				counter -= 1

			clkLastState = clkState

if __name__ == '__main__':
	while True:
	wv = windVane()
	print(F"Angle {wv.angle}; Counter {wv.counter}")
