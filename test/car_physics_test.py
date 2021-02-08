#!/usr/bin/python3

#hack for including another directory
import sys
sys.path.append('/home/andrew/school/159/code/smart_asphalt/src/')

from carphysics import CarPhysics

def main():
	#sampling time will be chosen based on runtime and experiment
	x, y = CarPhysics.calc_position(0, 8, .25)
	print(x, y)

if __name__ == "__main__":
    main()