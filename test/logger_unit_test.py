#/usr/bin/python3

"""
Unit test for the logging functinanlity
Last revision: January 9th, 2021 
"""

#hack for including another directory
import sys
sys.path.append('/home/andrew/smart_asphalt/src')

from logger import Data_logger
from logger import Sys_logger
from synch import lidar_producer
from queue import Queue
import timing

def data_logger_test_network():
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

def data_logger_functionality_test_lidar():
    #Create a logger
    lidar_log = Data_logger("lidar")

    #print empty dataframe
    lidar_log.print_df()

    #formatting data
    lidar_form = lidar_log.format_data([timing.get_current_time(), 120.0, 3.0, 7])
    print(lidar_form)

    #Upating dataframe
    lidar_log.update_df([timing.get_current_time(), 120.0, 3.0, 3])
    lidar_log.print_df()

    #log data + creating file
    lidar_log.log_data()

    #populate with random data
    for i in range(0, 10):
        lidar_log.update_df([timing.get_current_time(), i * 10, i, i*2])

    #ensure that the lidar logs to the same file instead of creating a new one
    lidar_log.log_data()

def data_logger_real_time_test_lidar():
    
    # LIDAR VARS
    lidar_channel = "/dev/ttyUSB0"
    lid_timeout = 10
    lid_thread_timeout = 5
    log = Sys_logger("Application")
    lidar_q = Queue(0)

    lp = lidar_producer(lidar_q, lidar_channel, log, lid_timeout)
    lp.start()

def sys_logger_test():
    #Testing sys logger

    sys_log = Sys_logger("smart_asphalt")
    sys_log.log_error("error")
    sys_log.log_warning("warning")
    sys_log.log_info("info")
    sys_log.log_debug("debug")

data_logger_real_time_test_lidar()