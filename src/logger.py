#!/usr/bin/python3

"""
Logging file for smart asphalt's platooning code
Last revision: April 15th, 2021 
"""

import pandas as pd
import numpy as np 
import logging


class Sys_logger():

    """ sys logging constructor """
    def __init__(self, name):
        # setting up logger
        self.logger = logging.getLogger(name)
        # set logger so that it will display all message types
        self.logger.root.setLevel(logging.NOTSET)
        # file handler for debug messages
        fh = logging.FileHandler("smart_asphalt.log")
        fh.setLevel(logging.DEBUG)
        # create formatter
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

    def __init__(self, sensor):
        """ data logger Constructor """
        self.sensor = sensor
        self.iteration = 0
        self.file_state = 0  # variable for keeping track of file naming, 0: need to get name, 1: named
        self.sname = ""  # file name

        # different constructor based on sensor, separated because of sampling rates
        if(sensor == "network"):
            self.df =  pd.DataFrame(columns = ["Timestamp", "Braking", "Steering", "Speed"])
        elif(sensor == "lidar"):
            self.df =  pd.DataFrame(columns = ["Timestamp", "Angle", "Distance", "Intensity"])
        else:
            raise NameError("Invalid sensor choice for data logger")

    def get_log_name(self):
        """ Function to get updated log name based on prior logs """
        # get iteration
        it_r = open("iteration.txt", "r")
        line = it_r.readline()
        self.iteration = int(line.strip())
        print(self.iteration)
        it_r.close()

        # write new iteration for next power on
        it_w = open("iteration.txt", "w")
        it_w.write(str(int(self.iteration)+1))
        it_w.close()

        self.sname = str(str(self.sensor) + str(self.iteration) + ".csv")

    def log_data(self):
        """ Function for writing the data frame to a csv """
        if self.file_state == 0: # get new file name if it needs to be named
            self.get_log_name()
            # open new logfile
            self.df.to_csv(path_or_buf=self.sname, mode='w', index=False)
            self.file_state = 1
        else: # append to file
            self.df.to_csv(path_or_buf=self.sname, mode='a', index=False, header=False)
               
        self.df = self.df.iloc[0:0] # clear existing data from the dataframe


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
                "Distance": rawdata[2],
                "Intensity": rawdata[3] } 
        return row

    """ update internal dataframe with the new row """
    def update_df(self, data):
        self.df = self.df.append(self.format_data(data), ignore_index=True)

    """ print out current data frame """
    def print_df(self):
        print(self.df.to_string())
            