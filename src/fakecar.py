from controls import *
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from network import recv_network, send_network
from logger import Sys_logger, Data_logger


class FakeCar:

	# fake car constructor
	def __init__(self, velocity, steering):
		self.velocity = velocity 
		self.controller = NetworkAdaptiveCruiseController(is_sim_car=True)
		self.controller.set_proportional_value(1.34)
		self.controller.set_integral_value(200)
		self.controller.set_derivative_value(0.7)
		self.desired_velocity = 0
		self.steering = steering
		self.input = []  # list of what should happen at each timestep
		self.error = 0  # starts with 0 error
		self.step = 0  # amount of runs of controller
		self.df = pd.DataFrame(columns=["step", "error", "desired", "actual"])
		self.get_inputs()
		
	# append the inputs
	def get_inputs(self):
		if len(sys.argv) < 2:
			print("Must input at least one number to test")
			exit()
		else:
			for i in range(1, len(sys.argv)):
				self.input.append(int(sys.argv[i]))

	# iterate the controller once
	def run_controller(self):
		# complete once interface is known
		self.desired_velocity = self.input[self.step]  # changing self.step
		self.controller.set_desired_velocity(self.desired_velocity)
		self.controller.set_measured_velocity(self.velocity)
		self.velocity = self.controller.control_loop()
		self.error = self.velocity - self.desired_velocity
		self.df.loc[self.step] = [self.step, self.desired_velocity - self.velocity, self.desired_velocity, self.velocity]
		self.step += 1

	def plotVel(self): 
		plt.plot(self.df["desired"], label='desired_velocity')
		plt.plot(self.df["actual"], label='controller_output')
		plt.title("Velocities per unit step")
		plt.legend(loc="best")
		plt.xlabel("Discrete Time Steps")
		plt.ylabel("Velocity (m/s)")
		plt.show()
		# plt.savefig("vel_plot.png")

	def plotError(self): 
		plt.plot(self.df["error"])
		plt.title("Error per unit step")
		plt.xlabel("Steps")		
		plt.ylabel("Error")
		plt.show()
		# plt.savefig("err_plot.png")


# running fake car
fk = FakeCar(0, 0)
while fk.step < (len(sys.argv) - 1):  # change (len(sys.argv) - 1)
	fk.run_controller()
fk.plotVel()
fk.plotError()


