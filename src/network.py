#/usr/bin/python3

"""
Networking implementation for smart asphalt's platoon
Last revision: December 22nd, 2020
"""

import socket
import sys
import timing
from Packet import Packet
from synch import thread_queue

class network_send:

	""" Constructor """
	def __init__(self, p1, p2):

		self.listen_port, self.send_port = self.bind_port(p1, p2)
		self.recskt, self.sndskt = self.bind_skt(self.listen_port, self.send_port)

	def bind_port(self, p1, p2):
		ls = int(p1)                                                  #for mapping sending port
		sn = int(p2)                                                  #for mapping listening port

		send_port_map = {1: 6201, 2: 6202, 3: 6303, 4: 6404}
		recv_port_map = {1: 6201, 2: 6202, 3: 6303, 4: 6404}

		#Port definitions need to be configured per car
		listen_port = send_port_map[ls]
		send_port = recv_port_map[sn]
		
		return listen_port, send_port

	def bind_skt(self, listen_port, send_port):

		######## BEGIN SOCKET INITIALIZATION ########
		sndskt = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)     #using ipv4 address + UDP packets
		recskt = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)     #using ipv4 address + UDP packets
		sndskt.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)  #configuring for broadcasting 

		recskt.bind(("100.100.5.255", listen_port))                   #bind socket to broadcast for listening
		sndskt.connect(("100.100.5.255", send_port))                  #connecting on the braodcast port

		return recskt, sndskt
		######## END SOCKET INITIALIZATION ########

	def broadcast_data(self, braking, steering, speed):
		self.sndskt.send((Packet(braking, steering, speed, 
			timing.get_current_time()).build_str()).encode())                

	def listen_data(self, rskt):
		rpkt = Packet(0, 0, 0, 0)                                     #initializing filler packet to be overwritten

		data = self.recskt.recvfrom(40)                               #TODO decide on appropriate length for receiving 
		recv_time = timing.get_current_time()

		rpkt.decode_pkt(data)
		elapsed_time = timing.meas_diff(rpkt.timestamp, recv_time)

		return rpkt, elapsed_time

	def printPkt(self, pkt, address):
		print(f"{address}, {pkt.braking}, {pkt.steering}, {pkt.speed}\n")
