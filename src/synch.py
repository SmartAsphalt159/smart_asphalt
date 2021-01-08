"""
Synchronization file for smart aspahlt's platooning code
Last revision: January 8th, 2020
"""

import threading
import network
from queue import Queue
from threading import Lock

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
    
class network_producer(thread_queue):

	"""Constructor"""
	def __init__(self, out_que):
		thread_queue.__init__(self, out_que)
		self.out_que = out_que
		self.running = True

	def halt_thread(self):
		running = False

	def run(self):
		while(running):
			try:
				thread_queue.enqueue(Packet)