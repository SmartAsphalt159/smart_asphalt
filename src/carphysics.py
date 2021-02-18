#!/usr/bin/python3

import math
import numpy as np
import time

class CarPhysics():
    def __init__(self):
        self.past_obj_pos = np.array([])
        self.delta_obj_pos = []
        self.last_time = time.time()
        self.last_steering = 0

    """Calculations are based only on wheelbase, steering angle, current velocity, and the sample time"""

    S = 16          #distance from center of front wheels
    R0 = 1.5        #distance from king pin access to the center of the contact patch
    J = 12          #distance between king pins
    WHEELBASE = 8   #Wheelbase (center front to center back)

    """ Estimate relative position based on current vehicle state """
    #Input: Steering angle [-90, 90] degrees and speed
    #Output: Relative position
    @staticmethod
    def calc_position(steering, speed, sample_time):

        #This function calculates relative position to the current values
        #Note that this is RELATIVE and that error will occur if the sample time is too large
        #As of writing (start of W6), the sample time should be on the order of .25 seconds, or 250 millseconds

        #handling case of going straight
        if(steering == 0):
            return 0, speed*sample_time

        #caclulate radius based on steering angle
        steering = math.radians(steering)
        outer_r = CarPhysics.WHEELBASE / math.sin(steering)
        inner_r = CarPhysics.WHEELBASE / math.tan(steering)
        #averaging to get center
        center_r = (outer_r + inner_r) / 2

        #converting alpha to radians
        #alpha_radians = math.radians(steering)
        #calculating angular velocity
        w = speed / (center_r)
        #distance traveled along circle
        #equation theta = theta0 + wt, where theta0 is 0
        theta = w*sample_time
        #caclulate relative position
        x = center_r*math.cos(theta)
        y = center_r*math.sin(theta)

        return [x, y]


    def get_past_obj_pos(self):
        return self.past_obj_pos

    def find_last_pos(self):
        now = time.time()
        sample_time = now-self.last_time
        #TODO: Get steering
        #TODO: Get speed
        steering_avg = (self.last_steering + steering)/2
        lastself.calc_position(steering_avg, speed, sample_time)
        self.last_steering = steering
        self.last_time = now
        return last_pos

    def get_object_position(self):
        #TODO: From lidar producer consumer get lastest lidar
        #np array
        return object_position



    def update_path(self):
        my_last_pos = self.find_last_pos()
        delta_my_pos = -my_last_pos

        self.past_obj_pos = self.past_obj_pos + delta_my_pos    #transform all past points
        obj_pos_now = self.get_object_position()

        self.past_obj_pos.append(obj_pos_now)
        difference = len(self.delta_obj_pos) - self.obj_max_length -1

        if difference > 0:
            del self.delta_obj_pos[:difference]
