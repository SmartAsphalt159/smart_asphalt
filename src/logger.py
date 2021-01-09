#!/usr/bin/python3

"""
Logging file for smart asphalt's platooning code
Last revision: January 9th, 2021 
"""

import pandas as pd
import numpy as np 
import logging

class Sys_logger():

    """ sys logging constructor """
    def __init__(self, name):
        #setting up logger
        self.logger = logging.getLogger(name)
        #set logger so that it will display all message types 
        self.logger.root.setLevel(logging.NOTSET)
        #file handler for debug messages
        fh = logging.FileHandler("smart_asphalt.log")
        fh.setLevel(logging.DEBUG)
        #create formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
        fh.setFormatter(formatter)
        self.logger.addHandler(fh)
        self.logger.info("Initializing smart asphalt log")

    def log_error(self, msg):
        self.logger.error(msg)
      
    def log_warning(self, msg):
        self.logger.warning(msg)

    def log_info(self, msg):
        self.logger.info(msg)

    def log_debug(self, msg):
        self.logger.debug(msg)

class Data_logger:

    """ data logger Constructor """
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
        it_r = open("iteration.txt", "r")
        line = it_r.readline()
        iteration = line.strip()
        it_r.close()

        #open new logfile 
        sname = self.sensor+iteration+".csv"
        self.df.to_csv(sname, index = False)

        #write new iteration
        it_w = open("iteration.txt", "w")
        it_w.write(str(int(iteration)+1))
        it_w.close()


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
            