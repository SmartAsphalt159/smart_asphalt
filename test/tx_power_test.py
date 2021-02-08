#!/usr/bin/python3

""" 
Test script for checking received packets vs TX power characteristics 
"""

#hack for including another directory
import sys
sys.path.append('/home/pi/smart_asphalt/src/')

from network import recv_network as rn, send_network as sn
from uuid import uuid4
from timing import get_current_time
from time import sleep
from sys import exc_info
import socket
import threading
import os

class tx_power:
	def __init__(self, send_port=1, recv_port=2):
		''' Constructor that initializes a connection with another 
            device in Ad Hoc Network and needed files for metrics
            collecton.
            Key Word Args
                send_port - sender indexed port value, default set to 1
                recv_port - reciever indexed port value, default set to 2
            Returns:
                None
        '''

		#TODO find starting power
		self.tx_power = 0
		self.recv_count = 0
		self.send_count = 0

		try:
			self.sender_node = sn(send_port)
		except:
			print("Unable to create sender_node", exc_info()[0]) 
		try:
			self.receive_node = rn(recv_port)
		except:
			print("Unable to create receiver_node", exc_info()[0]) 

	def get_tx_power(self):
		val = os.system('iwconfig wlp5s0 | grep -o \'Tx-Power=[0-9][0-9]\' | grep [0-9][0-9] -o')	
		return val

	def set_tx_power(self, value):
		os.system('iwconfig txpower {}'.format(value))

	def recv(self, timeout):
		if rn.listen_data(timeout) != -1:
			self.recv_count+=1

	def snd(self):
		sn.braodcast_data(0,0,0, get_current_time())
		self.send_count+=1

