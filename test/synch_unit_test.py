#/usr/bin/python3

"""
Unit test for synchronization functionality
Last revision: January 9th, 2021
"""

#hack for including another directory
import sys
sys.path.append('/home/andrew/school/159/code/smart_asphalt/src/')

import threading
from Packet import Packet
from logger import Sys_logger, Data_logger
from queue import Queue
from synch import queue_skeleton, network_producer, network_consumer
 
def test_thread_queue_pc():
	#Unit test for thread queue

	#create a logger
	temp_lock = threading.Lock()
	logger = Sys_logger("synch_test")
	tq = queue_skeleton(Queue(0), temp_lock, logger, 3)

	#testing normal functinonality
	#testing enque
	tq.enqueue(7)
	#testing deque
	sev = tq.dequeue()
	#print out variable
	print(sev)
	#print queue size
	print(tq.que.qsize())

	#test errant dequeue
	fail = tq.dequeue()

	#test empty queue
	print(tq.check_empty())

	#test full queue
	print(tq.check_full())

def test_network_producer_pc():
	#unit test for network producer

	#create network producer
	temp_lock = threading.Lock()
	logger = Sys_logger("synch_test")
	np = network_producer(Queue(0), temp_lock, 6202, logger, 3) 
	np.run()

def test_network_consumer_pc():
	#unit test for network consumer 

	#create network consumer
	temp_lock = threading.Lock()
	logger = Sys_logger("synch_test")
	np = network_consumer(Queue(0), temp_lock, 6202, logger, 3) 

	np.enqueue(Packet(0, 0, 0, 0))
	np.enqueue(Packet(1, 1, 1, 1))
	np.enqueue(Packet(2, 2, 2, 2))
	np.enqueue(Packet(3, 3, 3, 3))

	np.run()
