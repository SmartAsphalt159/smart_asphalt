#!/usr/bin/python3

#hack for including another directory
import sys
sys.path.append('/home/andrew/school/159/code/smart_asphalt/src/')

from carphysics import CarPhysics

def main():
	x, y = CarPhysics.calc_position(90, 50, 2)
	print(x, y)

if __name__ == "__main__":
    main()