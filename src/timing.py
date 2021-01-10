"""
Timing file for smart asphalt's platooning code
Timing is done in epoch time, to stay consistent with standards. 
Relative differences are calculated to be used in the measure of control delay
Last revision: December 22nd, 2020
"""

import time

""" returns the curernt time in epoch """
def get_current_time():
    return time.time()

""" sleep for a certain amount of time """
def sleep_for(secs):
    time.sleep(secs)

""" converts timestamp to local time """
def conv_timestamp(ts):
    return time.gmtime(ts)

""" Calculates difference between two timestamps """
def meas_diff(ti, tf):
    return tf - ti

