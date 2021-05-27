#!/usr/bin/python3

"""
Follower Vehicle Script to enable follower specific behavior and fit the sensor characteristics of the follower,
Last revision: May 9th, 2021
"""

import sys
import network
from sensor import GPIO_Interaction
from queue import Queue
from logger import Sys_logger
from synch import (network_producer, encoder_producer, encoder_consumer, lidar_producer, lidar_consumer)
from controls import *
from lidar import Lidar
from carphysics import CarPhysics
from timing import get_current_time, sleep_for

def main():
    # Dumb, smart, and lidar
    # add arugments
    if (len(sys.argv) != 2):
        print("Command is \"python3 platoon_follower.py <type>\"")
        print("Optional types: dumb, smart-follower, lidar")
        exit(0)
    else:
        # type of control
        c_type = sys.argv[1]  # TODO Verify its a valid command

    # INIT LOGGER
    # log = Sys_logger("Application")

    # INIT QUEUES (not length cap)
    network_q = Queue(0)
    encoder_q = Queue(0)
    lidar_q = Queue(0)

    # NETWORKING VARS
    recvport = 2 # TODO: Are these correct
    sendport = 1
    timeout = 2  # seconds TODO maybe change to be smaller
    net_thread_timeout = 5

    # Initializing the send_network
    sn = network.send_network(sendport)  # TODO: why is sn not being used

    # GPIO vars
    motor_ch = 32
    servo_ch = 33

    # ENCODER VARS
    enc_channel = 19
    enc_timeout = 2
    sample_wait = 0.1  # TODO utilize interrupts not polling
    enc_thread_timeout = 5

    # LIDAR VARS
    lidar_channel = "/dev/ttyUSB0"
    lid_timeout = 10  # TODO: Confirm Units
    lid_thread_timeout = 5

    # CONTROL VARS
    # Velocity constants PI controllers are often used rather than PD controllers for this
    vp = 0.7
    vi = 0
    vd = 2
    vk = 1
    # Steering constants
    sp = 0.5
    si = 0
    sd = 0.3

    gpio = GPIO_Interaction(enc_channel, servo_ch, motor_ch)

    # INIT PRODUCER and CONSUMERS

    # Network
    net_producer = network_producer(network_q, recvport, log, timeout)

    # Encoder
    ep = encoder_producer(encoder_q, enc_channel, log, enc_timeout, sample_wait)
    encoder_consumer_data = encoder_consumer(encoder_q, None, log, enc_thread_timeout)

    # Lidar (pull controls updates)
    lp = lidar_producer(lidar_q, lidar_channel, log, lid_timeout)
    lc = lidar_consumer(lidar_q, None, log, lid_thread_timeout)

    # start the producer consumer threads
    net_producer.start()
    ep.start()
    encoder_consumer_data.start()
    lp.start()
    lc.start()

    try:
        # update local objects (done by threads)

        # Call control system
        # TODO: Update to a better design pattern, this is pretty rough
        if (c_type == "dumb"):
            # call dumb contorl system
            new_lidar = Lidar(False)

            carphys = CarPhysics()

            controller = Dumb_Networking_Controls(new_lidar, gpio, carphys, net_producer, ep, lp, mode=1)

            controller = Dumb_Networking_Controls(new_lidar, gpio, carphys, net_producer, encoder_consumer_data, lp, mode=1)

            while True:
                # TODO: double check
                encoder_speed = controller.get_encoder_velocity()
                print(f"encoder_speed: {encoder_speed}")
                packet = net_producer.get_packet()
                if not packet:
                    sleep_for(0.01)
                    continue
                # print(f"str: {packet.steering}  thtl: {packet.throttle}")
                controller.get_newest_steering_cmd(packet.steering)
                controller.get_newest_accel_cmd(packet.throttle)
                strg, accl = controller.control_loop(encoder_speed)

                # Broadcast after control system
                # sn.broadcast_data(accl, strg, encoder_speed, time.time())

        # Uncomment when written
        # TODO: when smart networking is implemented
        # elif(c_type == "smart"):
        # call smart control system
        # TODO: once it is written

        elif (c_type == "lidar"):
            # call lidar control system
            new_lidar = Lidar(False)  # TODO: Why do we still do this?
            sleep_for(0.1)  # TODO: Is this necessary and why?
            carphys = CarPhysics()
            try:
                controller = LidarControls(vp, vi, vd, vk, sp, si, sd, new_lidar, gpio, carphys, ep, lp)
                # TODO: Don't pass pid constants in, assign them from outside
            except KeyboardInterrupt as e:
                raise e

            while True:
                controller.get_lidar_data()
                print("got lidar")
                encoder_speed = controller.get_encoder_velocity()
                # print(f"encoder_speed: {encoder_speed}")
                then = time.time()
                strg, accl = controller.control_loop(encoder_speed)
                print("time to run control loop: ", time.time() - then)
                # Broadcast after control system
                print("Steering ", strg, "Accl ", accl)
                # sn.broadcast_data(accl, strg, encoder_speed, time.time) #TODO: idk if we need this here
        elif (c_type == "encoder_test"):
            new_lidar = Lidar(False)
            carphys = CarPhysics()
            controller = Dumb_Networking_Controls(new_lidar, gpio, carphys, net_producer, ep, lp, mode=1)
            while True:
                encoder_speed = controller.get_encoder_velocity()
                # print(f"Speed = {encoder_speed}")
                time.sleep_for(0.01)
        elif c_type == "smart-follower":
            msg = "Smart network selected (smart-follower), beginning control loop"
            print(msg)
            # log.log_info("Smart network selected (smart-follower), beginning control loop")

            new_lidar = Lidar(False)
            sleep_for(0.1)
            carphys = CarPhysics()

            try:
                controller = LidarNetworkControls(vp, vi, vd, vk, sp, si, sd, new_lidar, gpio, carphys, ep, lp, net_producer)
            except KeyboardInterrupt as e:
                print("Keyboard Interrupt Detected, Quitting!")
                raise e

            # Initialize network variables
            desired_velocity = 0  # millimeters per second
            speed = 0  # millimeters per second
            throttle = 0  # between 0 - 10
            steering = 0  # Currently is servo position not heading
            timestamp = get_current_time()  # the time when message is sent
            msg = "Smart-Network Initialization Complete, Beginning Control Loop"
            # log.log_info("Smart-Network Initialization Complete, Beginning Control Loop")
            print(msg)
            while True:
                # Acquiring sensor data
                controller.get_lidar_data()
                vehicle_velocity = controller.get_encoder_velocity()  # (m/s)
                strg, accl = controller.control_loop(vehicle_velocity)
                log_data = f"strg: {strg} accel: {accl} velocity: {vehicle_velocity}mps"
                # log.log_info(log_data)
                print(log_data)
                # speed = encoder_consumer_data.get_speed()
                # timestamp = get_current_time()
                # sn.broadcast_data(throttle, steering, speed, timestamp)
        else:
            err_msg = "Input was not a valid type"
            # log.log_error("Input was not a valid type")
            print(err_msg)
    except Exception as e:
        print("im here!")
        print(e)

        err = "Exitted loop - Exception: " + str(e)
        raise ValueError(err)
        # log.log_error(err)
    # exited from loop

    # lp.end_scan = True
    sleep_for(0.2)
    # halt other threads, they should exit naturally
    net_producer.halt_thread()
    # nc.halt_thread()
    ep.halt_thread()
    # ec.halt_thread()
    # lp.halt_thread()
    # lc.halt_thread()

    # gracefully exit program and reset vars
    graceful_shutdown(log, gpio)


def graceful_shutdown(log, gpio):
    gpio.shut_down()
    log.log_info("Shutting down gracefully")


if __name__ == "__main__":
    main()
