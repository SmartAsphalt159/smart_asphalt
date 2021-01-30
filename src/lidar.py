#/usr/bin/python3
from time import time
from math import sqrt, abs, cos, sin, pi, floor, tan, atan
from rplidar import RPLidar

class Object:
    def __init__(self, pixels, filter_len, last_time, threshold_size,rel_velocity, last_center, box_len, sample, obj_found,err_fac=1):
        self.pixels = pixels
        self.filter_len = filter_len
        self.last_time = last_time
        self.this_time = time()
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
        self.passed = False

        if not self.len_filter():
            self.passed = False

            return None

        self.find_size()

        if not self.size_filter():
            self.passed = False

            return None

        if not self.obj_found:
            self.passed = True
            print("size x:",self.size[0]," y: ",self.size[1],"\n")
            print("at:",self.midpoint)
            return None

        if not self.location_filter():
            self.passed = False
            return None
        else:
            self.passed=True
            return None

    def len_filter(self):
        #print("len = ", len(self.pixels[0]))
        if len(self.pixels[0]) >  self.filter_len:
            return True
        else:
            return False

    """pass this object through filter. Objects too large/small are cut"""
    def size_filter(self):

        if self.size[0] > self.threshold_size or self.size[1] > self.threshold_size:
            return False
        else:
            return True

    def location_filter(self):
        if self.velocity:
            d_t = self.this_time - self.last_time
            d_pos = (self.velocity[0]*d_t,self.velocity[1]*d_t)
            d_pos_mag = sqrt(d_pos[0]**2 + d_pos[1]**2)
            err = self.err_fac*(2*1.41*(self.box_len/2) + 2*d_pos_mag)
            est_pos = (self.last_center[0] + d_pos[0],self.last_center[1] + d_pos[1])
            if abs(est_pos[0]-self.midpoint[0]) < err and abs(est_pos[1]-self.midpoint[1]) < err:
                return True
            else:
                return False
        else:
            err = self.err_fac*(2*1.41*(self.box_len/2)*3)
            est_pos = (self.last_center[0],self.last_center[1])
            if abs(est_pos[0]-self.midpoint[0]) < err and abs(est_pos[1]-self.midpoint[1]) < err:
                return True
            else:
                return False

    """find a size of box that all samples fit into"""
    def find_size(self):
        minx = maxx = self.pixels[0][0]
        maxy = miny = self.pixels[1][0]

        for i,x in enumerate(self.pixels[0]):
            if x > maxx:
                maxx = x
            if self.pixels[1][i] > maxy:
                maxy = self.pixels[1][i]
            if x < minx:
                minx = x
            if self.pixels[1][i] < miny:
                miny = self.pixels[1][i]

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
    def find_likeness(self):
        if self.midpoint[0] <= -200:
            return 0
        else:
            distance = (self.midpoint[0]**2+self.midpoint[1]**2)**0.5
            return 1000/distance
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



    def polar_to_cartesian(angle,distance):
        #may need to change due to reflection issues
        rad = 180/pi
        _tx = cos(float(angle)*rad)*float(distance)
        _ty = -sin(float(angle)*rad)*float(distance)

        cartesian = (_tx,_ty)
        return cartesian

    def polar_to_cartesian_full(self,polar):
        for index, (angle, distance) in polar:
            #may need to change due to reflection issues
            x = cos(float(angle)*rad)*float(distance)
            y = -sin(float(angle)*rad)*float(distance)
            polar[index] = (x,y)
        cartesian = polar
        return cartesian

    def break_DCs(self, polar, threshold, length):      #tries to break up scan by discontinuities
        break_list = []
        for index, (angle, distance) in enumerate(polar):
            if index == len(polar)-1:
                if abs(distance-polar[0][1]) > threshold:  #make this loop around
                    #break_list.append(angle+0.5)
                    break_list.append(polar[0][0]-0.5)
            else:
                #print("distance: " + str(abs(distance-(polar[index+1][1]+polar[index+2][1])/2)))
                if abs(distance-polar[index+1][1]) > threshold:  #make this loop around
                    #break_list.append(angle+0.5)
                    break_list.append(polar[index+1][0]-0.5)
                    break_list.sort()

        broken_objects = []
        for index, angle in enumerate(break_list):
            if index == len(break_list)-1:
                temp = ([],[])
                for a,d in polar:

                    if a > break_list[index] or a < break_list[0]:
                        lx,ly=self.polar_to_cartesian(a,d)

                        temp[0].append(lx)
                        temp[1].append(ly)
                broken_objects.append(temp)

            else:
                temp = ([],[])
                for a,d in polar:
                    if a > break_list[index] and a < break_list[index+1]:
                        lx,ly=self.polar_to_cartesian(a,d)
                        temp[0].append(lx)
                        temp[1].append(ly)
                broken_objects.append(temp)

        return broken_objects

    def scan_break_make_objects(self):
        scan = self.do_scan()
        b_scan = self.break_DCs(scan,30)
        return b_scan

    def find_object(self,broken_scans):
        break_list = []
        for index, (angle, distance) in enumerate(polar):
            if index == len(polar)-1:
                if abs(distance-polar[0][1]) > threshold:  #make this loop around
                    #break_list.append(angle+0.5)
                    break_list.append(polar[0][0]-0.5)
            else:
                #print("distance: " + str(abs(distance-(polar[index+1][1]+polar[index+2][1])/2)))
                if abs(distance-polar[index+1][1]) > threshold:  #make this loop around
                    #break_list.append(angle+0.5)
                    break_list.append(polar[index+1][0]-0.5)
                    break_list.sort()

        broken_objects = []
        for index, angle in enumerate(break_list):
            if index == len(break_list)-1:
                temp = ([],[])
                for a,d in polar:

                    if a > break_list[index] or a < break_list[0]:
                        lx,ly=self.polar_to_cartesian(a,d)

                        temp[0].append(lx)
                        temp[1].append(ly)
                broken_objects.append(temp)

            else:
                temp = ([],[])
                for a,d in polar:
                    if a > break_list[index] and a < break_list[index+1]:
                        lx,ly=self.polar_to_cartesian(a,d)
                        temp[0].append(lx)
                        temp[1].append(ly)
                broken_objects.append(temp)

        return broken_objects

    def update_velocity(self, object):
        delta_t = object.this_time - object.last_time
        delta_p = (abs(object.last_center[0]-object.midpoint[0]), abs(object.last_center[1]-object.midpoint[1]))
        delta_v = (delta_p[0]/delta_t, delta_p[1]/delta_t)
        return delta_v

    def get_position(self, object):
        if object.center:
            return object.center
        else:
            return object.midpoint

    def get_velocity(self, object):
        return object.velocity


"""
#to run
scan1 = l.do_scan(_theta,_r)
broken = l.break_DCs(scan1,400,200)
obj = l.find_obj1(broken)
"""
