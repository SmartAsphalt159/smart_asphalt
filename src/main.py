#!/usr/bin/python3

"""
Main file for smart aspahlt's platooning code
Last revision: Feburary 17th, 2020
"""

import sys
import threading
from queue import Queue
from logger import Sys_logger
from synch import (network_producer, network_consumer, encoder_producer, encoder_consumer,
    lidar_producer, lidar_consumer)

def main():

    #INIT LOGGER
    log = Sys_logger("Application")

    #INIT QUEUES (not length cap)
    net_q = Queue(0)
    encoder_q = Queue(0)
    lidar_q = Queue(0)

    #INIT LOCKS
    net_lock = threading.Lock()
    enc_lock = threading.Lock()
    lid_lock = threading.Lock()

    #NETWORKING VARS
    recvport = 6201
    sendport = 6202
    timeout = 2 #seconds
    net_thread_timeout = 5

    #ENCODER VARS
    #TODO: update to true value
    enc_channel = 7
    enc_timeout = 2
    sample_wait = 1
    enc_thread_timeout = 5

    #LIDAR VARS
    #TODO: update to true value
    lid_channel = 6
    lid_timeout = 10
    lid_thread_timeout = 5

    #INIT PRODCUER CONSUMERS

    #Network
    network_producer(net_q, net_lock, recvport, log, timeout)
    network_consumer(net_q, None, net_lock, log, net_thread_timeout)
    
    #Encoder
    encoder_producer(encoder_q, enc_lock, enc_channel, log, enc_timeout, sample_wait)
    encoder_consumer(encoder_q, None, enc_lock, log, enc_thread_timeout)

    #Lidar
    lidar_producer(lidar_q, lid_lock, lid_channel, log, lid_timeout)
    lidar_consumer(lidar_q, None, lid_lock, log, lid_thread_timeout)

    #infinite loop
    #while(1):
        #Call control system 

if __name__ == "__main__":
    main()