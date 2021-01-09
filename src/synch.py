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

class thread_queue:

    """ Constructor """
    def __init__(self, queue, logger):
        #initialize infinite queue
        self.que = Queue(maxsize=0) 
        self.lock = threading.Lock()
        self.logger = logger

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
    def dequeue(self):
        with self.lock:
            try: 
                data = self.que.get()
            except:
                return -1
        return data

    """ Empty wrapper """
    def check_empty(self):
        return self.que.empty()

    """ Full wrapper """
    def check_full(self):
        return self.que.full()
    
class network_producer(thread_queue, recv_network):

    """Constructor"""
    def __init__(self, in_que, port):
        thread_queue.__init__(self, in_que, self.logger)
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

class network_consumer(thread_queue, send_network):

    """Constructor"""
    def __init__(self, out_que, port):
        #TODO How to use the objects that I am creating in the producer
        thread_queue.__init__(self, out_que, self.logger)
        send_network.__init__(self, port)
        self.running = True

    def halt_thread(self):
        self.running = False

    def run(self):
        while(self.running):
            try:
                p = self.dequeue()
                #TODO: Figure out how the pipeline changes from here
            except:
                self.logger.log_error(self, "Failed to enqueue data")
