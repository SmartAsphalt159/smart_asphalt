"""
Synchronization file for smart aspahlt's platooning code
Last revision: January 8th, 2020
"""

import threading
import timing
from queue import Queue
from threading import Lock
from network import recv_network, send_network
from logger import Sys_logger, Data_logger
from Packet import Packet

class queue_skeleton:

    """ Constructor """
    def __init__(self, que, lock, logger, timeout):
        #initialize infinite queue
        self.que = que
        self.lock = lock
        self.logger = logger
        self.timeout = timeout

    """ Protected Enqueue """
    def enqueue(self, data):
        with self.lock:
            try:
                self.que.put(data)
            except: 
                self.logger.log_error(self, "Failed to enqueue data")
                return -1
        return 0

    """ Protected Dequeue """
    def dequeue(self,):
        with self.lock:
            try: 
                data = self.que.get(timeout=self.timeout)
            except:
                return -1
        return data

    """ Empty wrapper """
    def check_empty(self):
        return self.que.empty()

    """ Full wrapper """
    def check_full(self):
        return self.que.full()
    
class network_producer(queue_skeleton, recv_network):

    """Constructor"""
    def __init__(self, in_que, lock, port, logger, timeout):
        queue_skeleton.__init__(self, in_que, lock, logger, timeout)
        recv_network.__init__(self, port)
        self.running = True

    def halt_thread(self):
        self.running = False

    #enqueue received packets in the queue
    def run(self):
        while(self.running):
            try:
                self.enqueue(self.listen_data())
            except:
                self.logger.log_error(self, "Failed to enqueue packet data")

class network_consumer(queue_skeleton, send_network):

    """Constructor"""
    def __init__(self, out_que, lock, port, logger, timeout):
        queue_skeleton.__init__(self, out_que, lock, logger, timeout)
        send_network.__init__(self, port)
        self.running = True
        self.timeout = timeout

    def halt_thread(self):
        self.running = False

    def run(self):
        while(self.running):
            try:
                p = self.dequeue()
                #TODO: Figure out how the pipeline changes from here
            except:
                self.logger.log_error(self, "Failed to enqueue data")
