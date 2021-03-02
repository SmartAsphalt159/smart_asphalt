#!/usr/bin/python3

"""
Main file for smart aspahlt's platooning code
Last revision: Feburary 17th, 2020
"""


import sys
import threading
import network
import time
from sensor import GPIO_Interaction
from queue import Queue
from logger import Sys_logger
from synch import (network_producer, network_consumer, encoder_producer, encoder_consumer,
    lidar_producer, lidar_consumer)
from controls import *
from lidar import Lidar
from carphysics import CarPhysics

def main():

    #Dumb, smart, and lidar
    #add arugments
    if(len(sys.argv) != 2):
        print("Usage is: python3 main <type>")
        print("Optional types: dumb, smart, lidar")
        exit(0)
    else:
        #type of control
        c_type = sys.argv[1]

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
    recvport = 1
    sendport = 2
    timeout = 2  # seconds
    net_thread_timeout = 5
    sn = network.send_network(sendport)

    # GPIO vars
    motor_ch = 32
    servo_ch = 33

    # ENCODER VARS
    # TODO: update to true value
    enc_channel = 19
    enc_timeout = 2
    sample_wait = 0.1
    enc_thread_timeout = 5

    # LIDAR VARS
    lidar_channel = "/dev/ttyUSB0"
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

    gpio = GPIO_Interaction(enc_channel, servo_ch, motor_ch)

    #INIT PRODCUER CONSUMERS

    #Network
    np = network_producer(net_q, net_lock, recvport, log, timeout)
    nc = network_consumer(net_q, None, net_lock, log, net_thread_timeout)

    #Encoder
    ep = encoder_producer(encoder_q, enc_lock, enc_channel, log, enc_timeout, sample_wait)
    ec = encoder_consumer(encoder_q, None, enc_lock, log, enc_thread_timeout)

    #Lidar (pull controls updates)
    lp = lidar_producer(lidar_q, lid_lock, lidar_channel, log, lid_timeout)
    lc = lidar_consumer(lidar_q, None, lid_lock, log, lid_thread_timeout)

    #start the producer consumer threads
    np.start()
    nc.start()
    ep.start()
    ec.start()
    lp.start()
    lc.start()

    try:
        #update local objects (done by threads)

        #Call control system
        #TODO: Update to a better design pattern, this is pretty rough
        if(c_type == "dumb"):
            #call dumb contorl system
            new_lidar = Lidar(False)

            carphys = CarPhysics()
            controller = Dumb_Networking_Controls(new_lidar, gpio, carphys, nc, ec, lp, mode = 1)

            while True:
                #TODO: double check
                encoder_speed = controller.get_encoder_velocity()
                packet = nc.get_packet()
                controller.get_newest_steering_cmd(packet.steering)
                controller.get_newest_accel_cmd(packet.throttle)
                strg, accl = controller.control_loop(encoder_speed)
                #Broadcast after control system
                sn.broadcast_data(accl, strg, encoder_speed, time.time())
        #Uncomment when written
        #TODO: when smart networking is implemented
        #elif(c_type == "smart"):
            #call smart control system
            #TODO: once it is written

        elif(c_type == "lidar"):
            #call lidar control system
            new_lidar = Lidar(False)
            time.sleep(0.1)
            carphys = CarPhysics()
            controller = Lidar_Controls(vp, vi, vd, vk, sp, si, sd, new_lidar, gpio, carphys, ec, lp)
            while True:
                controller.get_lidar_data()

                encoder_speed = controller.get_encoder_velocity()
                then = time.time()
                strg, accl = controller.control_loop(encoder_speed)
                print("time to run control loop: ",time.time()-then)
                #Broadcast after control system
                print("Steering ",strg,"Accl ",accl)
                #sn.broadcast_data(accl, strg, encoder_speed, time.time) #TODO: idk if we need this here
        elif(c_type == "encoder_test"):
            new_lidar = Lidar(False)
            carphys = CarPhysics()
            controller = Dumb_Networking_Controls(new_lidar, gpio, carphys, nc, ec, lc, mode = 1)
            while True:
                encoder_speed = controller.get_encoder_velocity()
                print(f"Speed = {encoder_speed}")
                time.sleep(0.01)

        else:
            log.log_error("Input was not a valid type")
    except Exception as e:
        err = "Exitted loop - Exception: " + str(e)
        raise ValueError(err)
        log.log_error(err)


    #exited from loop

    #halt other threads, they should exit naturally
    np.halt_thread()
    nc.halt_thread()
    ep.halt_thread()
    ec.halt_thread()
    lp.halt_thread()
    lc.halt_thread()

    #gracefully exit program and reset vars
    graceful_shutdown(log,gpio)

def graceful_shutdown(log,gpio):
    #TODO: Cayman, how do I use this function, is it initalized somewhere
    gpio.shut_down()
    log.log_info("Shutting down gracefully")

if __name__ == "__main__":
    main()
