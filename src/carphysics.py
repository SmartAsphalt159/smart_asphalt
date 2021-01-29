#!/usr/bin/python3

import math

class CarPhysics:

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
        #Note that this is RELATIVE

        #caclulate radius based on steering angle 
        outer_r = CarPhysics.WHEELBASE / math.sin(steering)  
        inner_r = CarPhysics.WHEELBASE / math.tan(steering)
        #averaging to get center
        center_r = (outer_r + inner_r) / 2 

        #converting alpha to radians
        #alpha_radians = math.radians(steering)
        #calculating angular velocity
        w = speed / (center_r)
        #distance traveled along circle
        theta = w*sample_time
        #caclulate relative position
        x = center_r*math.cos(theta)
        y = center_r*math.sin(theta)

        return x, y