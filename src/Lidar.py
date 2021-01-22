#/usr/bin/python3
from time import time
from math import sqrt, abs, cos, sin, pi, floor, tan, atan
from rplidar import RPLidar

class Object:
    def __init__(self, pixels, ts, threshold_size, rel_velocity, last_center, box_len, sample, err_fac=1):
        self.pixels = pixels
        self.time_sampled = ts
        self.threshold_size = threshold_size
        self.velocity = rel_velocity
        self.last_center = last_center
        self.box_len = box_len
        self.err_fac = err_fac

        self.size = None
        self.midpoint = None
        self.center = None
        self.angle = None
        self.correct_object_score = None
        self.last_pixels = None

        self.find_size()

        if not self.size_filter():
            return None

        if not self.location_filter():
            return None

    """pass this object through filter. Objects too large/small are cut"""
    def size_filter(self):
        if self.size[0] > threshold_size and self.size[1] > threshold_size:
            return False
        else:
            return True

    def location_filter(self):
        now = time.time()
        d_t = self.time_sampled - now
        d_pos = rel_velocity*d_t
        d_pos_mag = sqrt(d_pos[0]**2 + d_pos[1]**2)
        err = self.err_fac*(2*1.41*(self.box_len/2) + 2*d_pos_mag)
        est_pos = (last_center[0] + d_pos[0],last_center[1] + d_pos[1])
        if abs(est_pos[0]-self.midpoint[0]) < err and abs(est_pos[1]-self.midpoint[1]) < err:
            return True
        else:
            return False

    """find a size of box that all samples fit into"""
    def find_size(self):
        minx = maxx = self.pixels[0][0]
        maxy = miny = self.pixels[0][1]

        for x,y in self.pixels:
            if x > maxx:
                maxx = x
            if y > maxy:
                maxy = y
            if x < minx:
                minx = x
            if y < miny:
                miny = y

        self.size = (maxx-minx, maxy-miny)
        self.midpoint = (minx + self.size[0]/2,miny+ self.size[1]/2)

    def find_center(self):
        #possibly use hough transform
        #center is the actual center not the midpoint of the box after chosen
        x_sum = y_sum = 0
        for x,y in self.pixels:
            x_sum += x
            y_sum += y

        a = len(self.pixels)
        self.center = (x_sum/a,ysum/a)

    """compare last object to this object and return likely hood of being the same"""
    def find_likeness(self, sample):
        return likeness


class Lidar():
    def __init__(self, USB_port='/dev/ttyUSB0'):
        self.lidar = RPLidar(USB_port)
        self.lidar.connect()
        self.time_last = 0
        self.last_measurement = None
        self.iterator = self.lidar.iter_measurments(540)

    def print_health(self):
        print(self.lidar.health())

    def print_info(self):
        print(self.lidar.info())

    def restart(self):
        self.lidar.reset()
        self.lidar.connect()

    def do_scan(self):
        """
        This depends on the buffer overflowing and starting at a random Angle
        in the buffer. It iterates until it passes its starting point and returns
        the data that it measured during its full 360 deg scan
        !!!Needs testing!!!
        """
        start = 360
        last = -1
        for new_scan, quality, angle, distance in self.iterator:
            if last == -1:
                start = angle
                last = angle+0.5
                if quality > 1 and distance > 1:
                    scan.append((angle,distance))
                continue

            if last < start and angle > start:
                break

            if quality > 1 and distance > 1:
                scan.append((angle,distance))

            last = angle

    def polar_to_cartesian(self,polar):
        for index, (angle, distance) in polar:
            #may need to change due to reflection issues
            x = cos(angle*(180/pi))*distance
            y = -sin(angle*(180/pi))*distance
            polar[index] = (x,y)
        cartesian = polar
        return cartesian

    def break_DCs(self, polar, threshold, length):      #tries to break up scan by discontinuities
        breaklist = []
        for index, (angle, distance) in enumerate(polar):
            if index == len(polar)-1:
                if abs(distance-(polar[0][1]+polar[1][1])/2) > threshold:  #make this loop around
                    break_list.append(angle+0.5)
            elif index == len(polar)-2:
                if abs(distance-(polar[index+1][1]+polar[0][1])/2) > threshold:  #make this loop around
                    break_list.append(angle+0.5)
            elif abs(distance-(polar[index+1][1]+polar[index+2][1])/2) > threshold:  #make this loop around
                break_list.append(angle+0.5)

        broken_objects = []*len(break_list)
        for index, angle in enumerate(break_list):
            broken_objects[index] = []
            if index != len(break_list)-1
                for a,d in polar:
                    if a > angle and a < break_list[index+1]:
                        broken_objects[index].append((a,d))
            else:
                for a,d in polar:
                    if a > angle and a < break_list[0]:
                        broken_objects[index].append((a,d))

        return broken_objects
