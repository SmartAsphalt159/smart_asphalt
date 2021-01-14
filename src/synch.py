"""
Synchronization file for smart aspahlt's platooning code
Last revision: January 8th, 2020
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
        self.lock.aquire()
        with self.lock:
            try:
                self.outque.put(data)
            except: 
                self.logger.log_error("Failed to enqueue data")
                self.lock.release()
                return -1
        self.lock.release()
        return 0

    """ Protected Dequeue """
    def dequeue(self,):
        self.lock.aquire()
        with self.lock:
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
    def __init__(self, in_que, lock, port, logger, timeout):
        queue_skeleton.__init__(self, in_que, None, lock, logger, timeout)
        recv_network.__init__(self, port)
        print("Spawned recv network")
        self.running = True
        print("Spawned network producer")
        print(self.running)

    def halt_thread(self):
        self.running = False

    #enqueue received packets in the queue
    def run(self):
        while(self.running):
            try:
                print("began listening")
                #Setting timeout of 3 seconds 
                temp, _ = self.listen_data(3)
                if(temp == -1):
                    self.logger.log_error("Socket timeout occured")
                print("stopped listening")
                self.enqueue(temp)
                #TESTING ON PC
                #self.enqueue(Packet(0, 0, 0, 0))
                #print(self.que.qsize())
                #timing.sleep_for(3)
            except:
                continue

class network_consumer(queue_skeleton, send_network):

    """Constructor"""
    def __init__(self, in_que, out_que, lock, port, logger, timeout):
        queue_skeleton.__init__(self, in_que, out_que, lock, logger, timeout)
        send_network.__init__(self, port)
        self.running = True
        self.timeout = timeout
        print("Spawned network consumer")

    def halt_thread(self):
        self.running = False

    def run(self):
        while(self.running):
            try:
                p = self.dequeue()
                #testing on pc
                net.printPkt(p, 0)
                #print(net.printPkt(p, 3))
                self.enqueue(p)
            except:
                continue
