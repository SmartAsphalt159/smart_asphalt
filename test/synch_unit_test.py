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
from synch import (queue_skeleton, network_producer, network_consumer, encoder_producer, encoder_consumer,
    lidar_producer, lidar_consumer)
 
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

def overall_synch_comm_test():

	#INIT LOGGER
	log = Sys_logger("Application")

	net_q = Queue(0)
	encoder_q = Queue(0)
	lidar_q = Queue(0)

	#INIT LOCKS
	net_lock = threading.Lock()
	enc_lock = threading.Lock()
	lid_lock = threading.Lock()

	#Random variables for parameters so that queue exchanges can be confirmed
	recvport = 1
	timeout = 2  # seconds
	net_thread_timeout = 5
	enc_thread_timeout = 5
	lid_thread_timeout = 5
	lid_timeout = 5
	enc_timeout = 5
	sample_wait = 5
	enc_channel = 5
	lidar_channel = 5

	np = network_producer(net_q, net_lock, recvport, log, timeout)
	nc = network_consumer(net_q, None, net_lock, log, net_thread_timeout)

	#Encoder
	ep = encoder_producer(encoder_q, enc_lock, enc_channel, log, enc_timeout, sample_wait)
	ec = encoder_consumer(encoder_q, None, enc_lock, log, enc_thread_timeout)

	#Lidar (pull controls updates)
	lp = lidar_producer(lidar_q, lid_lock, lidar_channel, log, lid_timeout)
	lc = lidar_consumer(lidar_q, None, lid_lock, log, lid_thread_timeout)

	#start the producer consumer threads
	np.start()
	nc.start()
	ep.start()
	ec.start()
	lp.start()
	lc.start()

	for i in range(100):
		print(f"Network Queue size: {net_q.qsize()}")
		print(f"Network Queue {list(net_q.queue)}")
		print(f"Last Net Var {nc.packet}\n")
		print(f"Encoder Queue size: {encoder_q.qsize()}")
		print(f"Encoder Queue {list(encoder_q.queue)}")
		print(f"Last Enc Var {ec.speed}\n")
		print(f"Lidar Queue size: {lidar_q.qsize()}")
		print(f"Lidar Queue {list(lidar_q.queue)}")
		print(f"Last Lidar Var {lc.scan}\n")
		i+=1
		
	np.halt_thread()
	nc.halt_thread()
	ep.halt_thread()
	ec.halt_thread()
	lp.halt_thread()
	lc.halt_thread()

	print("concluding")

overall_synch_comm_test()