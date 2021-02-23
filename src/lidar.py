#/usr/bin/python3
from time import time
from math import sqrt, cos, sin, pi, floor, tan, atan
from rplidar import RPLidar
import numpy as np

class Object:
    def __init__(self, pixels, filter_len, last_time, threshold_size,rel_velocity, last_midpoint, box_len, sample, obj_found,err_fac=1):
        self.pixels = pixels
        self.filter_len = filter_len
        self.last_time = last_time
        self.this_time = time()
        self.threshold_size = threshold_size
        self.velocity = rel_velocity
        self.last_midpoint = last_midpoint
        self.box_len = box_len
        self.err_fac = err_fac
        self.obj_found = obj_found

        self.size = None
        self.midpoint = None    #found from taking center of box
        self.center = None      #center of line found
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

        print("size x:",self.size[0]," y: ",self.size[1])
        print("at:",self.midpoint)

        if not self.obj_found:
            self.passed = True

            return None

        if not self.location_filter():
            self.passed = False
            print("failed location")
            print("velocity",self.velocity)
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
            est_pos = (self.last_midpoint[0] + d_pos[0],self.last_midpoint[1] + d_pos[1])
            if abs(est_pos[0]-self.midpoint[0]) < err and abs(est_pos[1]-self.midpoint[1]) < err:
                return True
            else:
                return False
        else:
            err = self.err_fac*(2*1.41*(self.box_len/2)*3)
            est_pos = (self.last_midpoint[0],self.last_midpoint[1])
            if abs(est_pos[0]-self.midpoint[0]) < err and abs(est_pos[1]-self.midpoint[1]) < err:
                return True
            else:
                return False

    """find a size of box that all samples fit into"""
    def find_size(self):
        minx = maxx = self.pixels[0][0]
        miny = maxy = self.pixels[1][0]

        for index in range(len(self.pixels[0][1:])):
            mx = self.pixels[0][index]
            my = self.pixels[1][index]
            if mx < minx:
                minx = mx
            elif mx > maxx:
                maxx = mx

            if my < miny:
                miny = my
            elif my > maxy:
                maxy = my

        self.size = (maxx-minx, maxy-miny)
        self.midpoint = (minx + self.size[0]/2,miny+ self.size[1]/2)

    """compare last object to this object and return likely hood of being the same"""
    def find_likeness(self):
        if self.midpoint[0] <= -200:
            return 0
        else:
            distance = (self.midpoint[0]**2+self.midpoint[1]**2)**0.5
            return 1000/distance
        return likeness

    def find_line_points(self,threshold):   #refrenced from https://github.com/Robotics-kosta/AMR-Line-extraction-from-Lidar-sensor-with-Split-and-Merge-algorithm/blob/master/src/main.py
        points = np.transpose(np.array(self.pixels))
        lines = self.SAM(points,threshold)
        return lines    #returns lines as endpoints

    def SAM(self,points,threshold):
        max_d,index = self.find_distant(points)
        if max_d > threshold:
            points1 = self.SAM(points[:index+1],threshold)
            points2 = self.SAM(points[index:],threshold)
            npoints = np.vstack((points1[:-1],points2))
        else:
            npoints = np.vstack((points[0],points[-1]))
        return npoints

    def find_distant(self,points):
        max_d = 0
        index = -1
        for i in range(1,points.shape[0]):
            d = self.get_d(points[i],points[0],points[-1])
            if (d > max_d):
                index = i
                max_d = d
        return (max_d,index)

    def get_d(self,p,pstart,pend):
        if np.all(np.equal(pstart,pend)):
            return np.linalg.norm(p-pstart)
        return np.divide(np.abs(np.linalg.norm(np.cross(pend-pstart,pstart-p))),np.linalg.norm(pend-pstart))

    def find_line_data(self,p1,p2):
        center = (p2+p1)/2                  #center of line segment
        length = np.linalg.norm(p2-p1)      #length of line segment
        dp = np.flip(p2-p1)* np.array([-1,1])
        angle = np.arctan(dp[1]/dp[0])*180/np.pi      #angle from x axis to normal of line

        return angle, center, length

    def find_line_lines(self,lines):
        line_list = []
        for index in range(1,lines.shape[0]):
             line_list.append(self.find_line_data(lines[index-1],lines[index]))
        return line_list

    def colinear(self,lines,threshold_angle):
        for i,line1 in enumerate(lines):
            for j,line2 in enumerate(lines):
                if i != j:
                    if abs(line1[0]-line2[0]) < threshold_angle:
                        if line1[2]>line2[2]:
                            del lines[j]
                        else:
                            del lines[i]
        return lines

    def set_center(self,center):
        self.center = center

    def filtered_lines(self,lines):
        threshold = 5
        if len(lines) > 2:
            colinear = self.colinear(lines,1)
            if colinear:
                lines = colinear

            filtered = []
            indexes = []
            for index in range(len(lines)):
                for i in range(len(lines)):
                    if index != i:
                        if lines[index][0] + 90 < lines[i][0] + threshold and lines[index][0] + 90 > lines[i][0] - threshold:
                            if index not in indexes:
                                indexes.append(index)
                            if i not in indexes:
                                indexes.append(i)
                        elif lines[index][0] - 90 < lines[i][0] + threshold and lines[index][0] - 90 > lines[i][0] - threshold:
                            if index not in indexes:
                                indexes.append(index)
                            if i not in indexes:
                                indexes.append(i)

                for k in indexes:
                    filtered.append(lines[k])

            if len(filtered) > 0:
                return filtered
            else:
                longest = 0
                index = 0
                for i, line in enumerate(lines):
                    if line[2]>longest:
                        longest = line[2]
                        index = i
                return [lines[index]]
        else:
            return lines

class Lidar():
    def __init__(self, scanner, USB_port='/dev/ttyUSB0'):
        if scanner:
            self.lidar = RPLidar(USB_port)
            self.lidar.connect()
            self.iterator = self.lidar.iter_measurments(800)
        self.time_last = 0
        self.last_measurement = None
        self.object_found = False
        self.empty_scans = 0
        self.last_obj = None
        self.last_velocity = None
        self.last_line = None
        self.new_scan = None
        self.scan_read = True
        self.end_scan = False

    def restart(self):
        self.lidar.stop()
        self.lidar.connect()
        self.iterator = self.lidar.iter_measurments(800)

    def start_scan(self):
        #TODO: Implement into Producer consumer... always running
        """
        Creates loop that constantly updates a 360 degree slice. To close loop
        make self.end_scan = True
        """
        scan=[]
        start = 360
        last = -1
        count = 0
        for new_scan, quality, angle, distance in self.iterator:
            count += 1
            if quality == 0 and angle == 0 and distance == 0:
                continue

            if last == -1:
                start = angle
                last = angle+0.5
                if quality > 1 and distance > 1:
                    scan.append((angle,distance))
                continue

            if last < start and angle > start and count > 20:
                self.new_scan = scan
                self.scan_read = False
                scan = []
                start = 360
                last = -1
                count = 0
                continue

            if quality > 1 and distance > 1:
                scan.append((angle,distance))

            last = angle

            if self.end_scan:
                break

    def get_scan(self):
        #TODO: result of scan in producer consumer
        self.scan_read = True
        return self.new_scan


    def polar_to_cartesian(angle,distance):
        tx_ = np.cos((float(angle)*np.pi/180))*float(distance)
        ty_ = -np.sin((float(angle)*np.pi/180))*float(distance)

        cartesian = (tx_,ty_)
        return cartesian

    def polar_to_cartesian_full(self,polar):
        cartesian = [[],[]]
        for angle,distance in polar:
            x = np.cos(float(angle)*np.pi/180)*float(distance)
            y = -np.sin(float(angle)*np.pi/180)*float(distance)
            cartesian[0].append(x)
            cartesian[1].append(y)
        return cartesian

    def break_DCs(self, polar, threshold, length):      #tries to break up scan by discontinuities
        break_list = []
        for index, (angle, distance) in enumerate(polar):
            if index == len(polar)-1:
                if abs(distance-polar[0][1]) > threshold:  #make this loop around
                    break_list.append(polar[0][0]-0.5)
            else:
                if abs(distance-polar[index+1][1]) > threshold:  #make this loop around
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

    def scan_break_objects_lines(self,scan):
        broken = l.break_DCs(scan,400,200)
        obj = l.find_obj(broken)
        if obj:
            line_points = obj.find_line_points(25)
            lines = obj.find_line_lines(line_points)
            lines = obj.filtered_lines(lines)
            if len(lines) > 1:
                line = self.find_main_line(lines)
                self.last_line = line
            else:
                line = lines[0]
            obj.set_center(line[1])
            return obj, line
        return None

    def find_main_line(self,lines): #line: [angle center length]
        if self.last_line:
            diffs = [abs(self.last_line[0]-lines[0][0]),abs(self.last_line[0]-lines[0][0]+180),abs(self.last_line[0]-lines[0][0]-180)]
            min_difference, index = min(diffs),0

            for i,l in enumerate(lines[1:]):
                angle, center, length = l
                diffs = [abs(self.last_line[0]-angle),abs(self.last_line[0]-angle+180),abs(self.last_line[0]-angle-180)]
                md = min(diffs)
                if md < min_difference:
                    min_difference,index = md, i
            return lines[i]
        else:
            min_angle = abs(lines[0][0])
            index = 0
            for i,l in enumerate(lines):
                angle, center, length = l
                if abs(angle) < min_angle:
                    min_angle,index = abs(angle), i
            return lines[i]

    def find_obj(self, broken_scans):
        if not self.object_found:
            object_list = []
            for num,scan in enumerate(broken_scans):
                obj = Object(scan, filter_len=4, last_time=None, threshold_size=250,
                             rel_velocity=None, last_midpoint=None, box_len=150,
                             sample=None, obj_found=False, err_fac=1)
                if obj.passed:
                    object_list.append(obj)
            l = len(object_list)
            if l == 0:
                #no objects found
                print("none")
                self.last_velocity = None
                self.object_found = False
                self.empty_scans += 1
                if self.empty_scans > 5:
                    print("no objects")
                    #stop car
                    return None
            elif l == 1:
                print("only one")
                self.object_found = True
                self.empty_scans = 0
                self.last_obj = object_list[0]
                return object_list[0]
            else:
                print("multiple")
                self.object_found = True
                max_likeness = 0
                max_index = 0
                self.empty_scans = 0
                for index, obj in enumerate(object_list):
                    likeness = obj.find_likeness()
                    print("likeness: ",likeness)
                    if likeness > max_likeness:
                        max_likeness = likeness

                        max_index = index
                self.last_obj = object_list[max_index]
                return object_list[max_index]
        else:
            object_list = []
            vel = None
            last_t = self.last_obj
            v = self.last_obj.velocity
            c = self.last_obj.midpoint
            lc = self.last_obj.last_midpoint
            tt = self.last_obj.this_time
            lt = self.last_obj.last_time
            """do velocity stuff"""
            if lc:
                vel = self.update_velocity(self.last_obj)

            for num,scan in enumerate(broken_scans):
                obj = Object(scan, filter_len=4, last_time=tt, threshold_size=250,
                             rel_velocity=vel, last_midpoint=c, box_len=150,
                             sample=None, obj_found=True, err_fac=1)
                if obj.passed:
                    object_list.append(obj)
            l = len(object_list)
            if l == 0:
                #no objects found
                print("none")
                self.last_velocity = None
                self.object_found = False
                self.empty_scans += 1
            elif l == 1:
                print("only one")
                self.object_found = True
                self.empty_scans = 0
                self.last_obj = object_list[0]
                return object_list[0]
            else:
                print("multiple")
                self.object_found = True
                max_likeness = 0
                max_index = 0
                self.empty_scans = 0
                for index, obj in enumerate(object_list):
                    likeness = obj.find_likeness()
                    print("likeness: ",likeness)
                    if likeness > max_likeness:
                        max_likeness = likeness

                        max_index = indexupdate_velocity
                self.last_obj = object_list[max_index]
                return object_list[max_index]

    def update_velocity(self, object):
        delta_t = object.this_time - object.last_time
        delta_p = (object.midpoint[0]-object.last_midpoint[0], object.midpoint[1]-object.last_midpoint[1])
        delta_v = (delta_p[0]/delta_t, delta_p[1]/delta_t)
        return delta_v

    def get_position(self, object):
        if object.center:
            return object.center
        else:
            return object.midpoint

    def get_velocity(self, object):
        return object.velocity

#added comment

"""
#to run
scan1 = l.do_scan(_theta,_r)
broken = l.break_DCs(scan1,400,200)
obj = l.find_obj(broken)
if obj:
    lines = obj.find_line_lines(line_points)
    lines = obj.filtered_lines(lines)
"""
