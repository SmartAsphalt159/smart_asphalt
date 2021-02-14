#!/user/bin/python3 

""" 
Script for monitoring the values of tegra_stats and logging them for viewing later 
The output from tegrastats is synchronous (~ every 1s), so the absolute timestamps are not taken. 
Instead, any plots assume contingous samples, meaning the index can be used for graphing"
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
import time
import re
import sys
import subprocess

class tegra_stats:

	reg = re.compile("POM_5V_IN \d+\/\d+")
	orig_stdout = sys.stdout

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
		line = str(f.readline())
		count = 0
		#create dataframe
		df = pd.DataFrame(columns = ["inst_mw", "avg_mw"])
		while line:
			#match regex 
			mtc = tegra_stats.reg.search(line)
			if(mtc):
				raw_match = mtc.group(0)
				nums = raw_match.split()[1]
				power = nums.split('/')
				df.loc[count] = [float(power[0]), float(power[1])]
			
			line = str(f.readline())
			count += 1

		#return dataframe
		return df

	@staticmethod
	def plotGraph(df): 
		plt.plot(df["inst_mw"])
		plt.title("Power Consumption Over Time")
		plt.xlabel("Time (Seconds relative to start of script)")		
		plt.ylabel("Power (mw)")
		plt.savefig("mw_plot.png")

def main():
	#get command line args
	if(len(sys.argv) != 2):
		print("Input format was not correct")
		print("The correct input is python3 tegra_stas.py <timeout>")
		exit()

	acq_time = int(sys.argv[1])
	#start collection process
	proc = tegra_stats.get_tegra_stats()
	time.sleep(acq_time)
	tegra_stats.kill_tegra_stats(proc)
	#extract data and plot
	df = tegra_stats.read_file()
	tegra_stats.plotGraph(df)

if __name__ == "__main__":
	main()
