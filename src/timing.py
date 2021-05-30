#!/usr/bin/python3
"""
Timing file for smart asphalt's platooning code
Timing is done in epoch time, to stay consistent with standards. 
Relative differences are calculated to be used in the measure of control delay
Last revision: December 22nd, 2020
"""

import time


def get_current_time():
    """ returns the curernt time in epoch """
    return time.time()


def sleep_for(secs):
    """ sleep for a certain amount of time """
    time.sleep(secs)


def conv_timestamp(ts):
    """ converts timestamp to local time """
    return time.gmtime(ts)


def meas_diff(ti, tf):
    """ Calculates difference between two timestamps """
    return tf - ti

