#!/usr/bin/python3

#class for packet structure

import socket

class Packet:

    """ constructor """
    def __init__(self, throttle, steering, speed, timestamp):
        self.throttle = throttle
        self.steering = steering
        self.speed = speed
        self.timestamp = timestamp

    #Input bytes
    #Error status
    """ Decodes packet """
    def decode_pkt(self, bts): 
       dstr = bts.decode() #decoded string
       Packet.breakdown_str(self, dstr) #splits string and assigns obj

    #input: formatted string
    #output: formatted bytes
    """ Encodes packet """
    def encode_pkt(self):
        estr = Packet.build_str(self)
        ret = str.encode(estr)
        return ret

    #input: current obj
    #output: formatted bytes
    """ builds packet string """
    def build_str(self):
        delim = '-'
        ret = str(self.throttle) + delim + str(self.steering) \
            + delim + str(self.speed) + delim + str(self.timestamp)
        return ret
    
    #input: formatted string
    #ouput: error status, pkt obj is updated internally 
    """ breaksdown string and stores in string """
    def breakdown_str(self, fstr):
        lst = fstr.split("-")
        if(len(lst) != 4): #if four items weren't sent, something went wrong 
            return -1 #returns packet indicating error

        #set internal variables
        self.throttle = float(lst[0])
        self.steering = float(lst[1])
        self.speed = float(lst[2])
        self.timestamp = float(lst[3])

        #return okay
        return 0

