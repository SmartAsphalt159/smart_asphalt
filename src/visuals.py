#!/usr/bin/python3

"""
Visualization code for the control delay
Last revision: December 24th, 2020
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import sys

def getdf():
    #get file name
    if(len(sys.argv) != 2):                                        
        print("Incorrect number of arguments")
        sys.exit()

    filename = sys.argv[1]
    df = pd.read_csv(filename)
    return df

def plotGraph(df): #optional parameter expressed in args

    plt.title("Control Delay")
    plt.xlabel("Time")		
    plt.ylabel("Steering Angle")
    plt.legend(loc="best")
    plt.show()