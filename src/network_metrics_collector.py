#/usr/bin/python3
from network import recv_network as rn, send_network as sn
from uuid import uuid4
from timing import get_current_time, sleep_for
from time import sleep
from sys import exc_info
import os
from threading import Thread

class network_metrics_collection():
    ''' Collection of methods to test the network and get data on its performance'''
    # Attempt to initialize connection with other device on the ad hoc network
    # Verify we have a connection
    
    # Begin Experiment 
    # 1. Generate a File to Store what packets we have sent into the pipeline 
    # or if receiving what packets we have received, verify we dont overwrite 
    # file when we run it again. recv#.data and send#.data maybe csv
    # 2. Data Structure: if sending store a copy of unique data we sent or we 
    # use a UUID, if receiving store data in columns.
    #------------------------------------------------------------------------
    # 3. Measure time sent and time rcved
    # 4. Threading or multiprocessing to enable listening during operation continuously
    # 5. Be able to send and recv data and have it recorded
    # 6. Configure Jetson to run on startup the script and collect the data

    def __init__(self, send_port=1, recv_port=1, file_root_name="metrics"):
        ''' Constructor that initializes a connection with another 
            device in Ad Hoc Network and needed files for metrics
            collecton.

            Key Word Args
                send_port - sender indexed port value, default set to 1
                recv_port - reciever indexed port value, default set to 2
            Returns:
                None
        '''
        try:
            self.sender_node = sn(send_port)
        except:
            print("Unable to create sender_node", exc_info()[0]) 
        try:
            self.receive_node = rn(recv_port)
        except:
            print("Unable to create receive_node", exc_info()[0])
        self.recv_file_name = file_root_name + "recv.data"
        self.send_file_name = file_root_name + "send.data"
        self.total_received = 0
        self.total_sent = 0

    def generate_test_data(self, len):
        ''' 
            Generates test data to be sent by the user

            Args:
                len - The amount of messages that are generated
            Returns:
                A list of dictionaries that contain the data for 
                the messages
        '''
        test_data = []
        for iteration in range(len):
            data = {}
            data['braking'] = uuid4()
            data['steering'] = iteration + 3
            data['speed'] = iteration + 5
            data['timestamp'] = get_current_time()
            test_data.append(data)
        return test_data

    def get_tx_power():

	    val = os.system('iwconfig wlan0 | grep -o \'Tx-Power=[0-9][0-9]\' | grep [0-9][0-9] -o')	
	    return val

    def set_tx_power(value):

	    os.system(f'sudo iwconfig wlan0 txpower {value}')
    
    def run_net_test_sender(self, size, init_delay):
        '''
            Sends a series of packets that it stores 
            in local files so that later the data can verified

            Args: 
                size - The amount of packets we want to send
                init_delay - a delay in seconds before we send 
                            out the first packet
            Returns:
                None 
        '''
        test_data = self.generate_test_data(size)
        try:
            file = open(self.send_file_name, 'a')
        except FileExistsError:
            print("Error in run_network_test: File Already Exists!")
        except TypeError:
            raise TypeError("Error in run_network_test: Typing Issue in Parameters")
        sleep(init_delay)
        for data in test_data: # Generate Test Case
            self.sender_node.broadcast_data(data['braking'], data['steering'], data['speed'], data['timestamp'])
            self.total_sent += 1
            file.write('data id: ' + str(data['braking']) + 'data msg sent: ' + str(data['braking']) + ' ' + str(data['steering']) + str(data['speed']) + str(data['timestamp']) + '\n')
        file.close()
    
    def run_net_test_recv(self, time_to_listen):
        '''
            Receives a series of packets that it stores 
            in local files so that later the data can verified

            Args: 
                time_to_listen - seconds for how long to listen for 1 msg
            Returns:
                None 
        '''
        recv_data = self.receive_node.listen_data(time_to_listen)
        if recv_data == -1:
            print("No Data Received!")
        else:
            try:
                file = open(self.recv_file_name, 'a')
            except FileExistsError:
                print("Error in run_network_test: File Already Exists!")
            except TypeError:
                raise TypeError("Error in run_network_test: Typing Issue in Parameters")
            recv_packet, elapsed_time = recv_data
            print('Recv: ' + str(type(recv_data)), str(recv_data))
            self.total_received += 1
            file.write('packet received: ' + str(elapsed_time) +' '+ str(recv_packet))
            file.close()

    def createSocketedThreads(self):
        # Create a receiving thread and a sending thread
        receiver = Thread(target=self.run_net_test_recv)
        receiver.setDaemon(True)
        receiver.start()

if __name__ == '__main__':
    network_metrics_collection.set_tx_power(22)
    power_setting = network_metrics_collection.get_tx_power()   # in dbm
    nmc = network_metrics_collection(file_root_name="metrics"+str(power_setting)+str(get_current_time()))
    
#   amount = 5000
#   i = 0    
#    while(i<amount):
#        nmc.run_net_test_recv(0.01)
#       i=i+1
#    x = "Execution Complete!, total received: " + str(nmc.total_received)
#    print(x)

#   amount = 100
#   i = 0
#   sleep_for(15)
#    while(i<amount):
#        nmc.run_net_test_sender(1, 2)
#        i = i+1
#        sleep(0.02)
#    x = "Execution Complete!, total received: " + str(nmc.total_sent)
#    print(x)
    