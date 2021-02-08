#/usr/bin/python3

"""
Unit test for the logging functinanlity
Last revision: January 9th, 2021 
"""

#hack for including another directory
import sys
sys.path.append('/home/andrew/school/159/code/smart_asphalt/src/')

from logger import Data_logger
from logger import Sys_logger
import timing

def dataloggertest():
    #Testing Network Logger

    #Create a logger
    log = Data_logger("network")

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

    #Testing Lidar Logger

    #Create a logger
    lidar_log = Data_logger("lidar")

    #print empty dataframe
    lidar_log.print_df()

    #formatting data
    lidar_form = lidar_log.format_data([timing.get_current_time(), 120.0, 3.0])
    print(lidar_form)

    #Upating dataframe
    lidar_log.update_df([timing.get_current_time(), 120.0, 3.0])
    lidar_log.print_df()
 
def sysloggertest():
    #Testing sys logger

    sys_log = Sys_logger("smart_asphalt")
    sys_log.log_error("error")
    sys_log.log_warning("warning")
    sys_log.log_info("info")
    sys_log.log_debug("debug")

sysloggertest()