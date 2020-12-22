#/usr/bin/python3

#class for packet structure

import socket

class Packet:

    #constructor
    def __init__(self, braking, steering, speed):
        self.braking = braking
        self.steering = steering
        self.speed = speed

    #Input bytes
    #Error status
    def decode_pkt(self, bts): 
       dstr = bts.decode() #decoded string
       Packet.breakdown_str(self, dstr) #splits string and assigns obj

    #input: formatted string
    #output: formatted bytes
    def encode_pkt(self):
        estr = Packet.build_str(self)
        ret = str.encode(estr)
        return ret

    #input: current obj
    #output: formatted bytes
    def build_str(self):
        delim = '-'
        ret = str(self.braking) + delim + str(self.steering) \
            + delim + str(self.speed)
        return ret
    
    #input: formatted string
    #ouput: error status, pkt obj is updated internally 
    def breakdown_str(self, fstr):
        lst = fstr.split("-")
        if(len(lst) != 3): #if three items weren't sent, something went wrong 
            return -1 #returns packet indicating error

        #set internal variables
        self.braking = float(lst[0])
        self.steering = float(lst[1])
        self.speed = float(lst[2])

        #return okay
        return 0

