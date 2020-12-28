#!/usr/bin/python3

"""
Logging file for smart asphalt's platooning code
Last revision: December 24th, 2020
"""

import pandas as pd
import numpy as np 


class Logger:

    """ Logger Constructor """
    def __init__(self, sensor):
        self.sensor = sensor

        #different constructor based on sensor, separated beacuse of sampling rates
        if(sensor == "network"):
            self.df =  pd.DataFrame(columns = ["Timestamp", "Braking", "Steering", "Speed"])
        elif(sensor == "lidar"):
            #TODO @Cayman: Please verify this
            self.df =  pd.DataFrame(columns = ["Timestamp", "Angle", "Value"])
        else:
            raise NameError("Invalid sensor choice for data logger")

    """ Function for writing the data frame to a csv """
    #TODO: Figure out how often this should occur, currently thinking of doing this on a scheudler
    #Incomplete
    def log_data(self):

        #get iteration
        it = open("iteration.txt")
        line = it.readline()
        iteration = line.strip()

        #open new logfile 
        sname = self.sensor+iteration+".csv"
        self.df.to_csv(sname, index = False)

    """ Format data into append ready data frame row """
    def format_data(self, rawdata):
        if(self.sensor == "network"):
            row = {
                "Timestamp": rawdata[0], 
                "Braking": rawdata[1], 
                "Steering": rawdata[2],
                "Speed": rawdata[3] }
        else:
            row = {
                "Timestamp": rawdata[0], 
                "Angle": rawdata[1], 
                "Value": rawdata[2] } 
        return row

    """ update internal dataframe with the new row """
    def update_df(self, data):
        self.df = self.df.append(self.format_data(data), ignore_index=True)

    """ print out current data frame """
    def print_df(self):
        print(self.df.to_string())
            