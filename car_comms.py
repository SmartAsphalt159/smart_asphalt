#/usr/bin/python3

"""
Networking implementation for smart asphalt's platoon
Last revision: December 22nd, 2020
"""

import socket
import sys
from Packet import Packet

def net_inet(p1, p2):

    ls = int(p1)                                                   #for mapping sending port
    sn = int(p2)                                                   #for mapping listening port

    send_port_map = {1: 6201, 2: 6202, 3: 6303, 4: 6404}
    recv_port_map = {1: 6201, 2: 6202, 3: 6303, 4: 6404}

    ######## BEGIN SOCKET INITIALIZATION ########
    sndskt = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)      #using ipv4 address + UDP packets
    recskt = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)      #using ipv4 address + UDP packets
    sndskt.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)   #configuring for broadcasting 

    #Port definitions need to be configured per car
    listen_port = send_port_map[ls]
    send_port = recv_port_map[sn]

    recskt.bind(("100.100.5.255", listen_port))                    #bind socket to broadcast for listening
    sndskt.connect(("100.100.5.255", send_port))                   #connecting on the braodcast port

    return recskt, sndskt
    ######## END SOCKET INITIALIZATION ########

def broadcast_data(skt, braking, steering, speed):
    skt.send((Packet(braking, steering, speed).build_str()).encode())                

def listen_data(rskt):
    rpkt = Packet(0, 0, 0)                                        #initializing packet
    data = rskt.recvfrom(40)                                      #TODO decide on appropriate lenght for receiving 
    rpkt.decode_pkt(data)
    return rpkt

def printPkt(pkt, address):
    print(f"{address}, {pkt.braking}, {pkt.steering}, {pkt.speed}\n")
