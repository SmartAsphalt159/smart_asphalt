#!/usr/bin/python3

import math
import numpy as np
import time

class CarPhysics():
    def __init__(self):
        self.delta_obj_pos = []
        self.last_time = time.time()
        self.last_steering = 0
        self.obj_max_length = 100

    """Calculations are based only on wheelbase, steering angle, current velocity, and the sample time"""

    S = 150          #distance from center of front wheels
    R0 = 15        #distance from king pin access to the center of the contact patch
    J = 120          #distance between king pins
    WHEELBASE = 165   #Wheelbase (center front to center back)

    """ Estimate relative position based on current vehicle state """
    #Input: Steering angle [-90, 90] degrees and speed
    #Output: Relative position
    @staticmethod
    def calc_position(steering, speed, sample_time):
        #print("speed",speed," sample_time ", sample_time)
        #This function calculates relative position to the current values
        #Note that this is RELATIVE and that error will occur if the sample time is too large
        #As of writing (start of W6), the sample time should be on the order of .25 seconds, or 250 millseconds
        steering = 2*steering #conversion to angle
        #handling case of going straight
        if(steering == 0):
            return [0, speed*sample_time, 0]

        
        #caclulate radius based on steering angle
        steering = math.radians(steering)
        outer_r = CarPhysics.WHEELBASE / math.sin(steering)
        inner_r = CarPhysics.WHEELBASE / math.tan(steering)
        #averaging to get center
        center_r = (outer_r + inner_r) / 2

        #print("radius: ", center_r)
        #converting alpha to radians
        #alpha_radians = math.radians(steering)
        #calculating angular velocity
        w = speed / (center_r)
        #distance traveled along circle
        #equation theta = theta0 + wt, where theta0 is 0
        theta = w*sample_time
        #print("theta: ",theta)
        #caclulate relative position
        x = center_r*math.sin(theta)
        y = center_r-center_r*math.cos(theta)
        #print("Calc x: ",x, "calc y:", y) 

        return [x, y, theta]

    def set_past_obj_pos(self,init_pos):
        self.past_obj_pos = np.array(init_pos)

    def get_past_obj_pos(self):
        return self.past_obj_pos

    def find_last_pos(self,steering,speed):
        now = time.time()
        sample_time = now-self.last_time
        steering_avg = (self.last_steering + steering)/2
        pos_calc = self.calc_position(steering_avg, speed, sample_time)
        last_pos = [pos_calc[0],pos_calc[1]]
        last_arc = pos_calc[2]
        self.last_steering = steering
        self.last_time = now
        return last_pos, last_arc

    def update_path(self, position, steering, speed):
        #move than rotate
        my_last_pos = self.find_last_pos(steering, speed)
        #print("my last pos ",my_last_pos)
        delta_my_pos = [(-1*my_last_pos[0][0]),my_last_pos[0][1]]
        angle = -my_last_pos[1]
        rotation = np.array([[np.cos(angle), np.sin(angle)],[-np.sin(angle), np.cos(angle)]])
        #print("past obj pos",self.past_obj_pos)
        #print("Delta pos",delta_my_pos)
        self.past_obj_pos = self.past_obj_pos + delta_my_pos    #transform all past points
        self.past_obj_pos = np.matmul(self.past_obj_pos,rotation)
        obj_pos_now = position

        self.past_obj_pos = np.vstack((self.past_obj_pos, obj_pos_now))
        print(self.past_obj_pos.shape[0]) 
        difference = self.past_obj_pos.shape[0] - self.obj_max_length -1
        if difference > 0:
            del self.delta_obj_pos[:difference]
        #print("past obj pos after append ",self.past_obj_pos)
        return self.past_obj_pos    
