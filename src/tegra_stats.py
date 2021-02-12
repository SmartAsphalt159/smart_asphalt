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

class tegra_stats:

	orig_stdout = sys.stdout

	@staticmethod
	def init_stdout_to_file():
		sys.stdout = open("tegra_log.csv", 'w')

	#read all tegra stats
	@staticmethod
	def get_tegra_stats():
		os.system("/usr/bin/tegrastats --logfile ~/smart_asphalt/logs/rawstats.txt")

	#writes control C to command line
	@staticmethod
	def kill_tegra_stats():
		os.system("\x03")

if __name__ == "__main__":
	collect = threading.Thread(target = tegra_stats.get_tegra_stats())
	collect.daemon = True
	collect.start()
	collect.join()
	tegra_stats.kill_tegra_stats()

	while(1):
		timing.sleep_for(1)
