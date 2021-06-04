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
from config import config


def main():

    # Input Handling Begin
    if(len(sys.argv) != 2):
        print("Usage is: python3 main <type>")
        print("Optional types: dumb, smart, lidar")
        exit(0)
    else:
        # type of control
        c_type = sys.argv[1]
    # Input Handling Done

    # One Time Initializations Begin
    #INIT LOGGER
    log = Sys_logger("Application")

    #INIT QUEUES (not length cap)
    net_q = Queue(0)
    encoder_q = Queue(0)
    lidar_q = Queue(0)

    #INIT CONFIG
    conf = config()
    conf.read_config()

    #NETWORKING VARS
    recvport = conf.get_param("int", "network", "recvport")
    sendport = conf.get_param("int", "network", "sendport")
    timeout =  conf.get_param("int", "network", "timeout")
    sn = network.send_network(sendport)

    #net_thread_timeout = 5

    # GPIO vars
    motor_ch = conf.get_param("int", "gpio", "motor")
    servo_ch = conf.get_param("int", "gpio", "servo")

    # ENCODER VARS
    enc_channel = conf.get_param("int", "encoder", "channel")
    enc_timeout = conf.get_param("int", "encoder", "timeout")
    sample_wait = conf.get_param("float", "encoder", "sample_wait")
    #enc_thread_timeout = 5

    # LIDAR VARS
    lidar_channel = conf.get_param("str", "lidar", "channel")
    lidar_timeout = conf.get_param("int", "lidar", "timeout")
    #lid_thread_timeout = 5

    #CONTROL VARS
    
    #Velocity constants
    vp = conf.get_param("float", "velocity", "p-term")
    vi = conf.get_param("float", "velocity", "i-term")
    vd = conf.get_param("float", "velocity", "d-term")
    vk = conf.get_param("float", "velocity", "k-term")
    
    #Steering constants
    sp = conf.get_param("float", "steering", "p-term")
    si = conf.get_param("float", "steering", "i-term")
    sd = conf.get_param("float", "steering", "d-term")

    gpio = GPIO_Interaction(enc_channel, servo_ch, motor_ch)

    #INIT PRODCUER CONSUMERS

    #Network
    np = network_producer(net_q, recvport, log, timeout)

    #nc = network_consumer(net_q, None, log, net_thread_timeout)

    #Encoder
    ep = encoder_producer(encoder_q, enc_channel, log, enc_timeout, sample_wait)
    #ec = encoder_consumer(encoder_q, None, log, enc_thread_timeout)

    #Lidar (pull controls updates)
    lp = lidar_producer(lidar_q, lidar_channel, log, lidar_timeout)
    #lc = lidar_consumer(lidar_q, None, log, lid_thread_timeout)


    #start the producer consumer threads
    np.start()
    #nc.start()
    ep.start()
    #ec.start()
    lp.start()
    #lc.start()
    # One time initializations end

    # Control Scheme Selection and Execution Begins
    try:
        #update local objects (done by threads)

        #Call control system
        #TODO: Update to a better design pattern, this is pretty rough
        if(c_type == "dumb"):
            #call dumb contorl system
            new_lidar = Lidar(False)

            carphys = CarPhysics()

            controller = Dumb_Networking_Controls(new_lidar, gpio, carphys, np, ep, lp, mode = 1)

            controller = Dumb_Networking_Controls(new_lidar, gpio, carphys, nc, ec, lp, mode = 1)


            while True:
                #TODO: double check
                encoder_speed = controller.get_encoder_velocity()
                print(f"encoder_speed: {encoder_speed}")
                packet = np.get_packet()
                if not packet:
                    time.sleep(0.01)
                    continue
                # print(f"str: {packet.steering}  thtl: {packet.throttle}")
                controller.get_newest_steering_cmd(packet.steering)
                controller.get_newest_accel_cmd(packet.throttle)
                strg, accl = controller.control_loop(encoder_speed)
                
                #Broadcast after control system
                #sn.broadcast_data(accl, strg, encoder_speed, time.time())

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
            try:
                controller = LidarControls(vp, vi, vd, vk, sp, si, sd, new_lidar, gpio, carphys, ep, lp)
            except KeyboardInterrupt as e:
                raise e

            while True:
                controller.get_lidar_data()
                print("got lidar")
                encoder_speed = controller.get_encoder_velocity()
                #print(f"encoder_speed: {encoder_speed}")
                then = time.time()
                strg, accl = controller.control_loop(encoder_speed)
                print("time to run control loop: ", time.time()-then)
                # Broadcast after control system
                print("Steering ", strg, "Accl ", accl)
                #sn.broadcast_data(accl, strg, encoder_speed, time.time) #TODO: idk if we need this here
        elif(c_type == "encoder_test"):
            new_lidar = Lidar(False)
            carphys = CarPhysics()
            nc = None
            controller = Dumb_Networking_Controls(new_lidar, gpio, carphys, np, ep, lp, mode=1)
            while True:
                encoder_speed = controller.get_encoder_velocity()
                print(f"Speed = {encoder_speed}")
                time.sleep(0.5)
        elif(c_type == "record"):
            cont = True
            try:
                while cont:
                    time.sleep(0.1)
                    continue
            except KeyboardInterrupt:
                print("ending")

        else:
            log.log_error("Input was not a valid type")
    except Exception as e:
        print("im here!")
        print(e)

        err = "Exitted loop - Exception: " + str(e)
        raise ValueError(err)
        log.log_error(err)
    # Control Scheme Selection and Execution Ends
    # exited from loop
    # Killing and stopping unnecessary activities Begins
    lp.end_scan = True
    time.sleep(0.2)
    # halt other threads, they should exit naturally
    np.halt_thread()
    # nc.halt_thread()
    ep.halt_thread()
    # ec.halt_thread()
    lp.halt_thread()
    # lc.halt_thread()

    # gracefully exit program and reset vars
    graceful_shutdown(log, gpio)
    # Killing and stopping unnecessary activities Ends


def graceful_shutdown(log, gpio):
    gpio.shut_down()
    log.log_info("Shutting down gracefully")


if __name__ == "__main__":
    main()
