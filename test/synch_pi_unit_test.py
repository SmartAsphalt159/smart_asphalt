"""
Unit test for synchronization functionality on the raspberry pi with threading and networking enabled
Last revision: January 15th, 2021
"""

#hack for including another directory
import sys
sys.path.append('/home/pi/smart_asphalt/src/')

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

#Driver for testing network producer and consumer
def driver():

	#setup one pi as broadcasting continously
	logger = Sys_logger("synch_test")
	temp_lock = threading.Lock()
	merge_q = Queue(0)
	oupt_q = Queue(0)

	pd = network_producer(oupt_q, temp_lock, 2, logger, 3) 
	cs = network_consumer(oupt_q, merge_q, temp_lock, logger, 5) 

	cs.start()
	pd.start()

	while(1):
		continue

driver()
