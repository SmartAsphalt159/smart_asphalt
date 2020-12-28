#/usr/bin/python3

"""
Unit test for the logging functinanlity
Last revision: December 27th, 2020
"""

#hack for including another directory
import sys
sys.path.append('/home/andrew/school/159/code/smart_asphalt/src/')

from logger import Logger
import timing

#Create a logger
log = Logger("network")

#print empty dataframe
log.print_df()

#formatting data
form = log.format_data([timing.get_current_time(), 0.0, 0.0, 0.0])
print(form)

#Upating dataframe
log.update_df([timing.get_current_time(), 0.0, 0.0, 0.0])
log.print_df()

#logging of data
#a priori, iteration.txt must already exist
    #and be populated solely as an int as the first character
log.log_data()