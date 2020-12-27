#/usr/bin/python3

"""
Main file for smart aspahlt's platooning code
Last revision: December 26th, 2020
"""

import socket
import sys
import time
import threading
import network
from logger import Logger
from synch import inter_thread_queue

def main():
    
    ### INIT NETWORK ###

    #get port numbers 
    if(len(sys.argv) != 3):                                        #checking argument validity 
        print("Incorrect number of arguments")
        print("Must specify index for sending and receiving port")
        sys.exit()

    #init sockets
    recskt, sndskt = network.net_init(sys.argv[1], sys.argv[2])

    #create threads for broadcasting and listening 
    list_thread = threading.Thread(target=network.listen_data, args=([recskt]))
    send_thread = threading.Thread(target=network.broadcast_data, args=([sndskt]))

    #start threads
    send_thread.start()
    list_thread.start()

    ### NETWORK INIT COMPLETE ### 

    ### THREAD COMMUNICATIONS INIT  ### 
    """initailize thread communication queue with infinite queue length and binary semaphore """
    #TODO: Decide whether lidar needs a separate queue due to bandwidth + speed 
    #network and controls queue
    net_cont_synch = inter_thread_queue(0, 1) 

    #local sensors and control queue
    sensor_cont_synch = inter_thread_queue(0, 1) 

    ### THREAD COMMUNUCATIONS INIT COMPLETE ### 

    ### DATA LOGGING INIT ### 

    net = Logger("network")
    lidar = Logger("lidar")
    net_data = None
    lidar_data = None
    
    ### DATA LOGGING INIT COMPLETE ###

    ### INIT CONTROLS ### TODO Cayman / Adrian 
    ### INIT CONTROLS COMPLETE ###

    ### INIT SENSORS ### TODO Cayman / Andrew 
    ### INIT SENSORS COMPLETE ###

    ### RUNTIME COMPONENT ###
    while(1):


        #update dataframes with data
        net.update_df(net_data)
        lidar.update_df(lidar_data)


if __name__ == "__main__":
    main()