#!/usr/bin/python3

"""
Networking implementation for smart asphalt's platoon
Last revision: Friday, Jan 8th 
"""

import os
import socket
import sys
import timing
from Packet import Packet

def bind_port(str_port, port_type):
    int_port = int(str_port)                                      #for mapping listening port

    #sending
    if(port_type == 0): 
            port_map = {1: 6201, 2: 6202, 3: 6303, 4: 6404}
    #receiving
    else: 
            port_map = {1: 6201, 2: 6202, 3: 6303, 4: 6404}

    #Port definitions need to be configured per car
    port = port_map[int_port]
    return port

def bind_skt(port, skt_type):

    ######## BEGIN SOCKET INITIALIZATION ########
    skt = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)     #using ipv4 address + UDP packets
    ip = str(os.system('hostname -I | awk \'{print $1}\''))
    if(skt_type == 0):
            skt.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)  #configuring for broadcasting 
            skt.connect((ip, port))                  #connecting on the braodcast port
    else:
            skt.bind((ip, port))                     #bind socket to broadcast for listening

    return skt

def printPkt(pkt, address):
    print(str(address) + ': '+ str(pkt) + '\n')

class send_network():

    """ Constructor """
    def __init__(self, port):
            self.send_port = bind_port(port, 0)
            self.sndskt = bind_skt(self.send_port, 0)

    def broadcast_data(self, braking, steering, speed, timestamp):
            self.sndskt.send((Packet(braking, steering, speed, 
                    timestamp).build_str()).encode())                

class recv_network():

    """ Constructor """
    def __init__(self, port):
            self.recv_port = bind_port(port, 1)
            self.recvskt = bind_skt(self.recv_port, 1)
            self.recvpkt = Packet(0, 0, 0, 0)

    """ listens for data """
    def listen_data(self, timeout):
            self.recvskt.settimeout(timeout)
            try:
                data, _ = self.recvskt.recvfrom(40)                               #TODO decide on appropriate length for receiving 
                recv_time = timing.get_current_time()
            except:
                return -1

            self.recvpkt.decode_pkt(data)
            elapsed_time = timing.meas_diff(self.recvpkt.timestamp, recv_time)

            return self.recvpkt, elapsed_time
