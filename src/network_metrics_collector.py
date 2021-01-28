#/usr/bin/python3
from network import recv_network as rn, send_network as sn
from uuid import uuid4
from timing import get_current_time
from time import sleep
from sys import exc_info

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
    # 3. 

    def __init__(self, send_port=1, recv_port=2, file_root_name="metrics"):
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

    def run_network_test(self, size, init_delay, mode='s'):
        '''
            Sends or Receives a series of packets that it stores 
            in local files so that later the data can verified

            Args: 
                size - The amount of packets we want to send
                init_delay - a delay in seconds before we send 
                            out the first packet
                mode - whether we are sending 's' or receiving 'r'
            Returns:
                None 
        '''      
        if (mode == 's'):
            test_data = self.generate_test_data(size)
            #file = open(self.send_file_name, 'w')
            try:
                file = open(self.send_file_name, 'w')
            except FileExistsError:
                print("Error in run_network_test: File Already Exists!")
            except TypeError:
                raise TypeError("Error in run_network_test: Typing Issue in Parameters")
            sleep(init_delay)
            for data in test_data: 
                self.sender_node.broadcast_data(data['braking'], data['steering'], data['speed'], data['timestamp'])
                file.write('data' + str(data) + ' ' + str(data['braking']) + str(data['steering']) + str(data['speed']) + str(data['timestamp']) + '\n')
                sleep(1)
            file.close()
        elif(mode == 'r'):
            recv_data = self.receive_node.listen_data(120)
            if recv_data == -1:
                print("No Data Received!")
            else:
                try:
                    file = open(self.recv_file_name, 'w')
                except FileExistsError:
                    print("Error in run_network_test: File Already Exists!")
                except TypeError:
                    raise TypeError("Error in run_network_test: Typing Issue in Parameters")
                print(type(recv_data), recv_data)
                #file.write('packet recvd: ' + str(elapsed_time) +' '+ str(recv_packet))
                file.close()
        else:
            print("Arguement for 'mode' is Invalid: please use 's' or 'r'!")

if __name__ == '__main__':
    nmc = network_metrics_collection()
    nmc.run_network_test(1, 5, 'r')
