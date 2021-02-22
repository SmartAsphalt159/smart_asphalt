#!/usr/bin/python3
"""
Synchronization file for smart aspahlt's platooning code
Last revision: Feb 17th, 2020
"""

import threading
import timing
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
                temp, _ = self.listen_data(1)
                if(temp == -1):
                    self.logger.log_error("Socket timeout occured")
                else:
                    self.enqueue(temp)
            except:
                if(self.outque.check_full()):
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

            if(not self.inque.check_empty()):
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

    def halt_thread(self):
        self.running = False

    #enqueue encoder values 
    def run(self):
        while(self.running):
            try:
                speed = self.get_speed()
                self.enqueue(speed)
            except:
                self.logger.log_error("Failed to read encoder value")

        #creating sampling delay
        #TODO: verify if millisecond / microsend time is necessary
        timing.sleep_for(self.sample_wait)

class encoder_consumer(queue_skeleton):

    """Constructor"""
    def __init__(self, in_que, out_que, lock, logger, thr_timeout):
        queue_skeleton.__init__(self, in_que, out_que, lock, logger, thr_timeout)
        self.running = True
        self.timeout = thr_timeout

    def halt_thread(self):
        self.running = False

    def get_speed(self):
        return self.speed

    def run(self):
        while(self.running):

            #verify that queue isn't empty
            #if(self.inque.check_empty()):
            #    timing.sleep_for(self.timeout)

            if(not self.inque.check_empty()):
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
        Lidar.__init__(self) 
        self.running = True

    def halt_thread(self):
        self.running = False

    #enqueue encoder values 
    def run(self):
        while(self.running):
            try:
                scan = self.get_scan()
                self.enqueue(scan)
            except:
                self.logger.log_error("Failed to read encoder value")

class lidar_consumer(queue_skeleton, Lidar):

    """Constructor"""
    def __init__(self, in_que, out_que, lock, logger, thr_timeout):
        queue_skeleton.__init__(self, in_que, out_que, lock, logger, thr_timeout)
        self.running = True
        self.timeout = thr_timeout

    def halt_thread(self):
        self.running = False

    #return the latest scan
    def get_scan(self):
        return self.scan

    def run(self):
        while(self.running):

            #verify that queue isn't empty
            #if(self.inque.check_empty()):
            #    timing.sleep_for(self.timeout)

            if(not self.inque.check_empty()):
                try:
                    #set scan to local variable
                    self.scan = self.dequeue()
                except:
                    self.logger.log_error("Could not deque lidar scan")
            #timeout becasue there is no data in the queue, will be respawned later
            #else:
            #    return 