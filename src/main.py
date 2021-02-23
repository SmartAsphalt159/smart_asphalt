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
from controls import *
from lidar import Lidar

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

    #GPIO vars
    motor_ch = 32
    servo_ch = 33

    #ENCODER VARS
    #TODO: update to true value
    enc_channel = 7
    enc_timeout = 2
    sample_wait = 1
    enc_thread_timeout = 5

    #LIDAR VARS
    lid_timeout = 10
    lid_thread_timeout = 5

    #CONTROL VARS
    #Velocity constants
    vp = 1
    vi = 0
    vd = 0
    vk = 1
    #Steering constants
    sp = 1
    si = 0
    sd = 0

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

    try:
        #update local objects (done by threads)

        #Call control system
        #TODO: Update to a better design pattern, this is pretty rough
        if(c_type == "dumb"):
            #call dumb contorl system
            #TODO: Is creating a differnt lidar ok?
            new_lidar = Lidar(False)
            gpio = GPIO_Interaction(enc_channel, servo_ch, motor_ch)
            #TODO: figure out encoder within controls
            #TODO: Figure out how controls works with networking
            controller = Dumb_Networking_Controls(new_lidar,gpio)

            while True:
                controller.control_loop()
        else if(c_type == "smart"):
            #call smart control system
            #TODO: once it is written

        else if(c_type == "lidar"):
            #call lidar control system
            new_lidar = Lidar()
            gpio = GPIO_Interaction(enc_channel, servo_ch, motor_ch)
            controller = Lidar_Controls(vp, vi, vd, vk, so, si, sd, new_lidar, gpio)

            while True:
                controller.control_loop()
        else:
            log.log_error("Input was not a valid type")
    except Exception as e:
        log.log_error("Exitted loop - Exception: ", e)

    #Broadcast after control system
    sn.broadcast_data() #TODO: Cayman the local control system vars need to be parameters here

    #gracefully exit program
    graceful_shutdown(log)

def graceful_shutdown(log):
    GPIO_Interaction.shut_down()
    log.log_info("Shutting down gracefully")

if __name__ == "__main__":
    main()
