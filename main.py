#/usr/bin/python3

"""
Main file for smart aspahlt's platooning code
Last revision: December 22nd, 2020
"""

import socket
import sys
import time
import threading
import car_comms
from logger import Logger

def main():
    
    ### INIT NETWORKING ###

    #get port numbers 
    if(len(sys.argv) != 3):                                        #checking argument validity 
        print("Incorrect number of arguments")
        print("Must specify index for sending and receiving port")
        sys.exit()

    #init sockets
    recskt, sndskt = car_comms.net_inet(sys.argv[1], sys.argv[2])

    #create threads for broadcasting and listening 
    list_thread = threading.Thread(target=car_comms.listen_data, args=([recskt]))
    send_thread = threading.Thread(target=car_comms.broadcast_data, args=([sndskt]))

    #start threads
    send_thread.start()
    list_thread.start()

    ### NETWORK INIT COMPLETE ### 

    ### DATA LOGGING INIT ### 

    net = Logger("network")
    lidar = Logger("lidar")
    net_data = None
    lidar_data = None
    
    ### DATA LOGGING INIT COMPLETE ###

    ### INIT CONTROLS ### @TODO Cayman / Adrian 
    ### INIT CONTROLS COMPLETE ###

    ### INIT LIDAR ### @TODO Cayman
    ### INIT LIDAR COMPLETE ###

    ### INIT LOCAL COMMUNICATION ### @TODO Anyone
    ### INIT LOCAL COMMUNICATION COMPLETE ###

    #while 1 used for the event driven system
    while(1):
        #synchronize threads (oh boi)

        #update dataframes with data
        net.update_df(net_data)
        lidar.update_df(lidar_data)


if __name__ == "__main__":
    main()