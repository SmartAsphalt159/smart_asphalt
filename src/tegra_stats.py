#!/user/bin/python3 

""" 
Script for monitoring the values of a script and logging them for viewing later 
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import sys
import timing
import threading
import subprocess

class tegra_stats:

	orig_stdout = sys.stdout
	timeout 

	@staticmethod
	def init_stdout_to_file():
		sys.stdout = open("tegra_log.csv", 'w')

	#read all tegra stats
	@staticmethod
	def get_tegra_stats():
		t_stats = subprocess.Popen(["exec " + "/usr/bin/tegrastats --logfile ~/smart_asphalt/logs/rawstats.txt"], shell=True)
		return t_stats

	#kill process
	@staticmethod
	def kill_tegra_stats(t_stats):
		t_stats.kill()

	@staticmethod
	def read_file():
		#open text file
		f = open("../logs/rawstats.txt", 'r')
		lines = f.readlines()
		#create dataframe
		for l in lines:
			#regex command 

		#return dataframe

def main():
	proc = tegra_stats.get_tegra_stats()
	timing.sleep_for(5)
	tegra_stats.kill_tegra_stats(proc)

if __name__ == "__main__":
	main()
