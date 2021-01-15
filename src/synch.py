"""
Synchronization file for smart aspahlt's platooning code
Last revision: January 15th, 2020
"""

import threading
import timing
import network as net
from queue import Queue
from threading import Lock
from network import recv_network, send_network
from logger import Sys_logger, Data_logger
from Packet import Packet

class queue_skeleton(threading.Thread):

    """ Constructor """
    def __init__(self, inque, outque, lock, logger, timeout):
        threading.Thread.__init__(self)
        #initialize infinite queue
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
        print(self.running)

    def halt_thread(self):
        self.running = False

    #enqueue received packets in the queue
    def run(self):
        while(self.running):
            try:
                #Setting timeout of 3 seconds 
                temp, _ = self.listen_data(3)
                if(temp == -1):
                    self.logger.log_error("Socket timeout occured")
                self.enqueue(temp)
                #print("Producer outque size: ", self.outque.qsize())
            except:
                if(self.outque.check_full()):
                    self.logger.log_error("Network Producer output queue is full")
                continue

class network_consumer(queue_skeleton, send_network):

    """Constructor"""
    def __init__(self, in_que, out_que, lock, logger, thr_timeout):
        queue_skeleton.__init__(self, in_que, out_que, lock, logger, thr_timeout)
        self.running = True
        self.timeout = thr_timeout

    def halt_thread(self):
        self.running = False

    def run(self):
        while(self.running):

            #verify that queue isn't empty
            if(self.inque.check_empty()):
                timing.sleep_for(self.timeout)

            try:
                if(not self.inque.check_empty()):
                    p = self.dequeue()
                    #net.printPkt(p, 7)
                    self.enqueue(p)
                #timeout becasue there is no data in the queue, will be respawned later
                else:
                    return 
            except:
                self.logger.log_error("Could not deque packet")
