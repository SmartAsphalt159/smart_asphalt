#!/usr/bin/python3

"""
Main file for smart aspahlt's platooning code
Last revision: Feburary 17th, 2020
"""


import sys
import threading
import network
from sensor import GPIO_Interaction
from queue import Queue
from logger import Sys_logger
from synch import (network_producer, network_consumer, encoder_producer, encoder_consumer,
    lidar_producer, lidar_consumer)

def main():

    #Dumb, smart, and lidar
    #add arugments 
    if(len(sys.argv) != 2):
        print("Usage is: python3 main <type>")
        print("Optional types: dumb, smart, lidar")
        exit(0)
    else:
        #type of control 
        c_type = argv[1]

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
    sn = send_network(sendport)

    #ENCODER VARS
    #TODO: update to true value
    enc_channel = 7
    enc_timeout = 2
    sample_wait = 1
    enc_thread_timeout = 5

    #LIDAR VARS
    lid_timeout = 10
    lid_thread_timeout = 5

    #INIT PRODCUER CONSUMERS

    #Network
    network_producer(net_q, net_lock, recvport, log, timeout)
    network_consumer(net_q, None, net_lock, log, net_thread_timeout)
    
    #Encoder
    encoder_producer(encoder_q, enc_lock, enc_channel, log, enc_timeout, sample_wait)
    encoder_consumer(encoder_q, None, enc_lock, log, enc_thread_timeout)

    #Lidar (pull controls updates)
    lidar_producer(lidar_q, lid_lock, log, lid_timeout)
    lidar_consumer(lidar_q, None, lid_lock, log, lid_thread_timeout)

    #infinite loop
    while(1):
        #update local objects (done by threads)

        #Call control system 
        #TODO: Update to a better design pattern, this is pretty rough 
        if(c_type == "dumb"):
            #call dumb contorl system
        else if(c_type == "smart"):
            #call smart control system
        else if(c_type == "lidar"):
            #call lidar control system
        else:
            log.log_error("Input was not a valid type")

        #Broadcast after control system 
        sn.broadcast_data() #TODO: Cayman the local control system vars need to be parameters here

    #gracefully exit program
    graceful_shutdown(log)

def graceful_shutdown(log):
    GPIO_Interaction.shut_down()
    log.log_info("Shutting down gracefully")

if __name__ == "__main__":
    main()