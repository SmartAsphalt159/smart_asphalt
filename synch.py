"""
Synchronization file for smart aspahlt's platooning code
Last revision: December 26th, 2020
"""

import threading
from queue import Queue

class inter_thread_queue:

    """ Constructor """
    def __init__(self, queue_size, semaphore_count):
        #initialize infinite queue
        self.que = Queue(maxsize=queue_size) 
        self.sema = threading.Semaphore(semaphore_count)
     
    """ Protected Enqueue """
    def enqueue(self, data):
        with self.sema:
            try:
                self.que.put(data)
            except: 
                return -1
        return 0

    """ Protected Deque """
    def dequeue(self):
        with self.sema:
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
    