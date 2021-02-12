#!/user/bin/python3 

""" 
Script for monitoring the values of a script and logging them for viewing later 
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import sys

class tegra_stats:

	orig_stdout = sys.stdout

	@staticmethod
	def init_stdout_to_file():
		sys.stdout = open("tegra_log.csv", 'w')

	#read all tegra stats
	@staticmethod
	def get_tegra_stats():
		os.system("/usr/bin/tegrastats --logfile ~/smart_asphalt/logs/rawstats.txt")

tegra_stats.get_tegra_stats()