#!/usr/bin/python3
"""
Synchronization file for smart aspahlt's platooning code
Last revision: Feb 17th, 2020
"""

import threading
import timing
import time
import serial
import json
import network as net
from queue import Queue
from threading import Lock
from network import recv_network, send_network
from logger import Sys_logger, Data_logger
from Packet import Packet
from sensor import Encoder, GPIO_Interaction
from lidar import Lidar

class queue_skeleton(threading.Thread):

    """ Constructor """
    def __init__(self, inque, outque, lock, logger, timeout):
        threading.Thread.__init__(self)
        self.inque = inque
        self.outque = outque
        self.lock = lock
        self.logger = logger
        self.timeout = timeout

    """ Protected Enqueue """
    def enqueue(self, data):
        self.lock.acquire()

        try:
            self.outque.put(data)
        except:
            self.logger.log_error("Failed to enqueue data")
            self.lock.release()
            return -1

        self.lock.release()
        return 0

    """ Protected Dequeue """
    def dequeue(self):
        self.lock.acquire()
        try:
            data = self.inque.get(timeout=self.timeout)
            self.inque.task_done()
        except:
            self.logger.log_error("Failed to dequeue data")
            self.lock.release()
            return -1

        self.lock.release()
        return data

    """ Empty wrapper """
    def check_empty(self):
        return self.inque.empty()

    """ Full wrapper """
    def check_full(self):
        return self.outque.full()

class network_producer(queue_skeleton, recv_network):

    """Constructor"""
    def __init__(self, out_que, lock, port, logger, timeout):
        queue_skeleton.__init__(self, None, out_que, lock, logger, timeout)
        recv_network.__init__(self, port)
        self.running = True

    def halt_thread(self):
        self.running = False

    #enqueue received packets in the queue
    def run(self):
        while(self.running):
            try:
                #Setting timeout of 1 second
                temp, _ = self.listen_data(0.1)
                if(temp == -1):
                    self.logger.log_error("Socket timeout occured")
                else:
                    self.enqueue(temp)
            except:
                if(self.check_full()):
                    self.logger.log_error("Network Producer output queue is full")

class network_consumer(queue_skeleton):

    """Constructor"""
    def __init__(self, in_que, out_que, lock, logger, thr_timeout):
        queue_skeleton.__init__(self, in_que, out_que, lock, logger, thr_timeout)
        self.running = True
        self.timeout = thr_timeout

    def halt_thread(self):
        self.running = False

    def get_packet(self):
        return self.packet

    def run(self):
        while(self.running):

            #verify that queue isn't empty
            #if(self.inque.check_empty()):
            #    timing.sleep_for(self.timeout)

            if(not self.check_empty()):
                try:
                    self.packet = self.dequeue()
                except:
                    self.logger.log_error("Could not deque packet")
            #timeout becasue there is no data in the queue, will be respawned later
#            else:
#                return

class encoder_producer(queue_skeleton, Encoder):

    """Constructor"""
    def __init__(self, out_que, lock, channel, logger, timeout, sample_wait):
        queue_skeleton.__init__(self, None, out_que, lock, logger, timeout)
        Encoder.__init__(self, channel)
        self.running = True
        self.sample_wait = sample_wait
        self.ser = serial.Serial('/dev/ttyTHS1', 19200, timeout=0.8)
        self.ser.flush()
        print("encoder initialized")

    def halt_thread(self):
        self.running = False

    #enqueue encoder values
    def run(self):
        while(self.running):
            try:
                try:
                    start = time.time()
                    data = self.ser.readline().decode()
                    next_t = time.time()
                    #print(data)
                except serial.SerialTimeoutException:
                    print("Serial Timeout")
                    self.logger.log_error("Serial Timeout error")
                except serial.SerialException as e:
                    print(e)
                    self.logger.log_error(e)
                except Exception as e:
                    print(e)
                    raise e
                try:
                    j_data = json.loads(data)
                    tally = j_data["tally"]
                    delta_ms = j_data["delta_time"]
                    self.sample_speed(tally, delta_ms)
                    speed = self.get_speed()
                    #print(speed)
                    self.enqueue(speed)
                    now = time.time()
                    print(f"Time taken to get data: {next_t - start}")
                    print(f"TIme taken after: {now - next_t}")
                except Exception as e:

                    print(e)

            except Exception as e:
                print(e)
                self.logger.log_error("Failed to read encoder value")

        #creating sampling delay
        #TODO: verify if millisecond / microsend time is necessary
            #timing.sleep_for(self.sample_wait)

class encoder_consumer(queue_skeleton):

    """Constructor"""
    def __init__(self, in_que, out_que, lock, logger, thr_timeout):
        queue_skeleton.__init__(self, in_que, out_que, lock, logger, thr_timeout)
        self.running = True
        self.timeout = thr_timeout
        self.speed = 0

    def halt_thread(self):
        self.running = False

    def get_speed(self):
        print("In consumer get speed")
        return self.speed

    def run(self):
        while(self.running):

            #verify that queue isn't empty
            #if(self.inque.check_empty()):
            #    timing.sleep_for(self.timeout)

            if(not self.check_empty()):
                try:
                    self.speed = self.dequeue()
                except:
                    self.logger.log_error("Could not deque encoder data")
            #timeout becasue there is no data in the queue, will be respawned later
            #else:
            #    return


class lidar_producer(queue_skeleton, Lidar):

    """Constructor"""
    def __init__(self, out_que, lock, channel, logger, timeout):
        queue_skeleton.__init__(self, None, out_que, lock, logger, timeout)
        Lidar.__init__(self, True)
        self.running = True
        self.time_last_gotten = time.time()
        

    def halt_thread(self):
        self.running = False

    #enqueue encoder values
    def run(self):
        #initiate the scan
        print("starting scan, hi andrew!")
        self.start_scan()
        print("scan started, yahoo")
        while(self.running):
            print("loop cycle:")
            try:

                scan = self.get_scan()
                now = time.time()
                print("Last scan gotten",now-self.time_last_gotten)
                self.time_last_gotten = now
                self.enqueue(scan)
            except:
                print("failed to read lidar value")
                self.logger.log_error("Failed to read lidar value")

class lidar_consumer(queue_skeleton, Lidar):

    """Constructor"""
    def __init__(self, in_que, out_que, lock, logger, thr_timeout):
        queue_skeleton.__init__(self, in_que, out_que, lock, logger, thr_timeout)
        self.running = True
        self.timeout = thr_timeout
        self.scan = None


    def halt_thread(self):
        self.running = False

    #return the latest scan

    def run(self):
        while(self.running):

            #verify that queue isn't empty
            #if(self.inque.check_empty()):
            #    timing.sleep_for(self.timeout)

            if(not self.check_empty()):
                try:
                    #set scan to local variable
                    self.scan = self.dequeue()
                except:
                    self.logger.log_error("Could not deque lidar scan")
            #timeout becasue there is no data in the queue, will be respawned later
            #else:
            #    return
