#/usr/bin/python3
from time import time
from math import sqrt, abs, cos, sin, pi, floor, tan, atan
from rplidar import RPLidar

class Object:
    def __init__(self, pixels, filter_len, last_time, threshold_size,
                 rel_velocity, last_center, box_len, sample, err_fac=1, obj_found):
        self.pixels = pixels
        self.filter_len = filter_len
        self.last_time = last_time
        self.this_time = time.time()
        self.threshold_size = threshold_size
        self.velocity = rel_velocity
        self.last_center = last_center
        self.box_len = box_len
        self.err_fac = err_fac
        self.obj_found = obj_found

        self.size = None
        self.midpoint = None
        self.center = None
        self.angle = None
        self.correct_object_score = None
        self.last_pixels = None

        if not self.len_filter():
            return False

        self.find_size()

        if not self.size_filter():
            return False

        if not self.obj_found:
            return True

        if not self.location_filter():
            return False
        else:
            return True

    def len_filter(self):
        if len(self.pixels) >  self.filter_len:
            return True
        else:
            return False

    """pass this object through filter. Objects too large/small are cut"""
    def size_filter(self):
        if self.size[0] > threshold_size and self.size[1] > threshold_size:
            return False
        else:
            return True

    def location_filter(self):
        if rel_velocity:
            d_t = self.this_time - self.last_time
            d_pos = rel_velocity*d_t
            d_pos_mag = sqrt(d_pos[0]**2 + d_pos[1]**2)
            err = self.err_fac*(2*1.41*(self.box_len/2) + 2*d_pos_mag)
            est_pos = (last_center[0] + d_pos[0],last_center[1] + d_pos[1])
            if abs(est_pos[0]-self.midpoint[0]) < err and abs(est_pos[1]-self.midpoint[1]) < err:
                return True
            else:
                return False
        else:
            err = self.err_fac*(2*1.41*(self.box_len/2)*3)
            est_pos = (last_center[0] + d_pos[0],last_center[1])
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
        self.object_found = False
        self.empty_scans = 0
        self.last_obj = None
        self.last_velocity = None

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

        return scan

    def polar_to_cartesian(self,polar):
        for index, (angle, distance) in polar:
            #may need to change due to reflection issues
            x = cos(angle*(180/pi))*distance
            y = -sin(angle*(180/pi))*distance
            polar[index] = (x,y)
        cartesian = polar
        return cartesian

    def break_DCs(self, polar, threshold):      #tries to break up scan by discontinuities
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

    def scan_break_make_objects(self):
        scan = self.do_scan()
        b_scan = self.break_DCs(scan,30)
        return b_scan

    def find_object(self):
        if self.object_found:
            broken_scans = self.scan_break_make_objects()
            object_list = []
            for scan in broken_scans:
                sc = polar_to_cartesian(scan)
                obj = Object(sc, filter_len=3, last_time=None, threshold_size=40,
                             rel_velocity=None, last_center=None, box_len=15,
                             sample=None, err_fac=1, object_found=False)
                if obj:
                    object_list.append()
            l = len(object_list)
            if l == 0:
                #no objects found
                self.last_velocity = None
                empty_scans += 1
                if empty_scans > 5:
                    #stop car
                    return None
            elif l == 1:
                self.object_found = True
                self.last_obj = object_list[0]
                return object_list[0]
            else:
                self.object_found = True
                max_likeness = 0
                max_index = 0
                for index, obj in enumerate(object_list):
                    likeness = obj.find_likeness()
                    if likeness > max_likeness:
                        max_likeness = likeness
                        max_index = index
                self.last_obj = object_list[index]
                return object_list[index]
        else:
            now = time.time()
            broken_scans = self.scan_break_make_objects()
            object_list = []
            for scan in broken_scans:
                sc = polar_to_cartesian(scan)
                lt = self.last_obj.this_time
                center = self.last_obj.midpoint
                if self.last_obj.last_center:
                    velocity = self.update_velocity(self.last_obj)
                else:
                    velocity = None
                obj = Object(sc, filter_len=3, last_time=lt, threshold_size=40,
                             rel_velocity=velocity, last_center=center,
                             box_len=15, sample=None, err_fac=1, object_found=True)
                if obj:
                    object_list.append()
            l = len(object_list)
            if l == 0:
                #no objects found
                self.last_velocity = None
                self.object_found = False
                self.empty_scans += 1
                if self.empty_scans > 5:
                    #stop car
                    return None
            elif l == 1:
                self.last_obj = object_list[0]
                return object_list[0]
            else:
                max_likeness = 0
                max_index = 0
                for index, obj in enumerate(object_list):
                    likeness = obj.find_likeness()
                    if likeness > max_likeness:
                        max_likeness = likeness
                        max_index = index
                self.last_obj = object_list[0]
                return object_list[index]

    def update_velocity(self, object):
        delta_t = object.this_time - object.last_time
        delta_p = (abs(object.last_center[0]-object.midpoint[0]), abs(object.last_center[1]-object.midpoint[1]))
        delta_v = delta_p/delta_v
        return delta_v

    def get_position(self, object):
        if object.center:
            return object.center
        else:
            return object.midpoint

    def get_velocity(self, object):
        return object.velocity
