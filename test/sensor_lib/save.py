import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from math import sin, cos, pi, tan, atan, floor, ceil,sqrt
from time import time,sleep
import csv

rad = 180/pi

def polar_to_cartesian(angle,distance):
    #may need to change due to reflection issues
    tx_ = np.cos((float(angle)*np.pi/180))*float(distance)
    ty_ = -np.sin((float(angle)*np.pi/180))*float(distance)

    cartesian = np.array([[tx_],[ty_]])
    return cartesian

class Lidar():
    def __init__(self):
        self.time_last = 0
        self.last_measurement = None
        self.empty_scans = 0
        self.object_found = False
        self.last_obj = None


    def do_scan(self,theta,rho):
        start = 360
        last = -1
        scan = np.empty((2,0))
        for i,angle in enumerate(theta):
            distance = rho[i]
            if last == -1:
                start = angle
                last = angle+0.5
                if distance > 1:

                    scan = np.append(scan,np.array([[angle],[distance]]),axis=1)
                continue

            if last < start and angle > start:
                break

            if distance > 1:
                scan = np.append(scan,np.array([[angle],[distance]]),axis=1)
            last = angle
        return scan

    def polar_to_cartesian(self,polar):
        cartesian = polar
        cartesian[0] = np.cos(polar[0]*np.pi/180)*polar[1]
        cartesian[1] = -np.sin(polar[0]*np.pi/180)*polar[1]
        return cartesian

    def break_DCs(self, polar, threshold, length):      #tries to break up scan by discontinuities
        break_list = np.array([])
        for index in range(polar[1].size):
            distance = polar[1][index]
            angle = polar[1][index]
            if index == polar[1].size-1:
                if abs(distance-polar[1][0]) > threshold:  #make this loop around
                    break_list = np.append(break_list,[polar[0][0]-0.5])
            else:
                if abs(distance-polar[1][index+1]) > threshold:  #make this loop around

                    break_list = np.append(break_list,[polar[0][index+1]-0.5])
        break_list.sort()

        broken_objects = []

        for index in range(break_list.size):
            angle = break_list[index]
            if index == len(break_list)-1:
                temp = np.empty((2,0))
                for i in range(polar[1].size):
                    a = polar[0][i]
                    d = polar[1][i]
                    if a > break_list[index] or a < break_list[0]:
                        cartesian = polar_to_cartesian(a,d)
                        temp = np.append(temp,cartesian,axis=1)
                broken_objects.append(temp)

            else:
                temp = np.empty((2,0))
                for i in range(polar[1].size):
                    a = polar[0][i]
                    d = polar[1][i]
                    if a > break_list[index] and a < break_list[index+1]:
                        cartesian = polar_to_cartesian(a,d)
                        temp = np.append(temp,cartesian,axis=1)
                broken_objects.append(temp)

        return broken_objects

    def scan_break_make_objects(self):
        scan = self.do_scan()
        b_scan = self.break_DCs(scan,30)
        return b_scan

    def find_obj1(self, broken_scans):
        if not self.object_found:
            object_list = []
            for num,scan in enumerate(broken_scans):
                obj = Object(scan, filter_len=4, last_time=None, threshold_size=250,
                             rel_velocity=None, last_center=None, box_len=150,
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
            lc = self.last_obj.last_center
            tt = self.last_obj.this_time
            lt = self.last_obj.last_time
            """do velocity stuff"""
            if lc:
                vel = self.update_velocity(self.last_obj)

            for num,scan in enumerate(broken_scans):
                obj = Object(scan, filter_len=4, last_time=tt, threshold_size=250,
                             rel_velocity=vel, last_center=c, box_len=150,
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

                        max_index = index
                self.last_obj = object_list[max_index]
                return object_list[max_index]

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


class Object():
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
        minx = self.pixels[0].min()
        maxx = self.pixels[0].max()
        maxy = self.pixels[1].max()
        miny = self.pixels[1].min()

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

    def find_lines(self):
        self.pixels
        return 0

"""
name = input("name of file\n")
graph_data = open(name,'r').read()
lines = graph_data.split('\n')
"""
theta=np.array([])
r=np.array([])
points = np.empty((2,0))
lines=[]
start = time()
tx = np.array([])
ts = np.array([])
ty = np.array([])
_x = np.array([])
_y = np.array([])
ths = []
ds = []

xs = []
ys = []


with open('move_straight_data_1611711796.9998024.csv', 'r') as csvfile:
    plots= csv.reader(csvfile, delimiter=',')
    for k, row in enumerate(plots):
        if row[0] == 'time added':
            continue

        try:
            a = row[3]
        except IndexError:
            continue

        if float(row[2]) > 1 and float(row[3])<10000 and float(row[3]) > 200:
            theta = np.append(theta,[float(row[1])])
            r = np.append(r,[float(row[3])])
            ts = np.append(ts,[float(row[0])])
            c = polar_to_cartesian(row[1],row[3])
            _x = np.append(_x,c[0])
            _y = np.append(_y,c[1])
            points = np.append(points,c,axis=1)

interval_ms = 10 #delay between frames in ms
interval_s = interval_ms/1000
start_time = ts[0]
end_time = ts[len(ts)-1]
frames = np.arange(round(start_time,3),round(end_time,3),interval_s)

fig, ax = plt.subplots()


ax = plt.axis([-6000,6000,-6000,6000])

points, = plt.plot([0], [0], 'r.')


l = Lidar()


def printxy(_xx,_yy,ax):

    c = ax.scatter(_xx,_yy,s=10)


count = 0
def animate1(t):
    global count
    x = []
    y = []
    nx = ny = [0]
    _theta = []
    _r = []
    index = 0
    for i,t_ in enumerate(ts):
        if t_ > t:
            index = i
            break
    if i > 400:
        num = 400
    else:
        num = i

    for j in range(i-num,i,1):
        x.append(_x[j])
        y.append(_y[j])
        _theta.append(theta[j])
        _r.append(r[j])


    count += 1
    if count > 100 and count%100==0:

        print("hit")
        """
        fig1 = plt.figure()
        ax1 = fig1.add_subplot(111)
        fig2 = plt.figure()
        ax2 = fig2.add_subplot(111)
        """
        now = time()
        scan1 = l.do_scan(_theta,_r)
        broken = l.break_DCs(scan1,400,200)
        """
        temp = ([],[])

        for k in range(scan1[1].size):
            _tt = scan1[0][k]
            _dd = scan1[1][k]
            a= polar_to_cartesian(_tt,_dd)
            _xx,_yy = (a[0],a[1])
            temp[0].append(_xx)
            temp[1].append(_yy)

        printxy(temp[0],temp[1],ax2)
        for b in broken:
            xxx,yyy = b
            #print(len(xxx))
            printxy(xxx,yyy,ax1)
            #print(b, "\n")
        """
        obj = l.find_obj1(broken)
        if obj:
            print(obj.velocity)
            nx,ny = obj.pixels
        print(time()-now)
        """
        plt.show()

        fig1 = plt.figure()
        ax1 = fig1.add_subplot(111)
        """
        """
        for b in broken:

            xxx,yyy = b
            print(len(xxx))
            printxy(xxx,yyy,ax1)

        sleep(10)
        """

    points.set_data(nx, ny)
    return points,



# create animation using the animate() function
myAnimation = animation.FuncAnimation(fig, animate1, frames=frames, interval=interval_ms, repeat=True)

plt.show()
