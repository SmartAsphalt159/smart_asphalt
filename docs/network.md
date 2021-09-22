# Networking Documentation

### file: network.py

## General Functions

#### bind_port
&nbsp;&nbsp;&nbsp;&nbsp; Binds general input (1, 2, 3, 4) to the respective port (6201, 6202, 6203, 6204).

#### bind_socket
&nbsp;&nbsp;&nbsp;&nbsp; Binds port to a particular socket. Sending socket pass 0, receiving socket pass 1 to the second parameter

#### printPkt
&nbsp;&nbsp;&nbsp;&nbsp; Function for printing out a packet to the interpreter.

## Class send_network

### Functions

#### __init__
&nbsp;&nbsp;&nbsp;&nbsp; Initialize receive_network class by setting up port, socket, and packet object.

#### listen_data
&nbsp;&nbsp;&nbsp;&nbsp; Listen for data on a specicied socket for a specified timeout. Failure returns -1, Success returns received packet and timestamp.

## Class recv_network

### Functions

#### __init__
&nbsp;&nbsp;&nbsp;&nbsp; Initialize send_network class by setting up port and socket.

#### broadcast_data
&nbsp;&nbsp;&nbsp;&nbsp; Send packet data to the socket and port specified in init

