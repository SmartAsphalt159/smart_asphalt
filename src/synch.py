"""
Synchronization file for smart aspahlt's platooning code
Last revision: January 8th, 2020
"""

import logger
import threading
from queue import Queue
from threading import Lock
from network import recv_network, send_network

class thread_queue:

    """ Constructor """
    def __init__(self, queue):
        #initialize infinite queue
        self.que = Queue(maxsize=0) 
        self.lock = threading.Lock()

    """ Protected Enqueue """
	# @TODO better define what data is, should it be a list, an optional argument, etc 
    def enqueue(self, data):
        with self.lock:
            try:
                self.que.put(data)
            except: 
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
    
class network_producer(thread_queue, send_network):

    """Constructor"""
    def __init__(self, in_que, port):
        #TODO How to use the objects that I am creating in the producer
        thread_queue.__init__(self, in_que)
        send_network.__init__(self, port)
        self.out_que = in_que
        self.running = True

    def halt_thread(self):
        self.running = False

    def run(self):
        while(self.running):
            try:
                #@TODO Interface with the local data communication queue here
                braking = 0
                steering = 0
                speed = 0
            except:
                #TODO: add error messages later

                continue

            try:
                self.enqueue(self.broadcast_data(braking, steering, speed))
            except:
                continue

class network_consumer(thread_queue, recv_network):

    """Constructor"""
    def __init__(self, out_que, port):
        thread_queue.__init__(self, out_que)
        recv_network.__init__(self, port)
        self.out_que = out_que
        self.running = True

    def halt_thread(self):
        self.running = False

    #enqueue received packets in the queue
    def run(self):
        while(self.running):
            try:
                self.enqueue(self.listen_data())
            except:
                continue