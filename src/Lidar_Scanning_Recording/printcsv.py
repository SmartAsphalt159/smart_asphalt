import matplotlib.pyplot as plt
import csv
from math import sin, cos, pi, tan, atan, floor, ceil
import numpy as np
from time import time
x=[]
y=[]
angle_t = 90
rad_t = 5000
rad_res = 0.25

area_of_intrest=(8000,8000)
theta_res = 1
rho_res = 50


def hough2(_x,_y):
    print("finding hough")
    nR,nC = area_of_intrest
    img_bin = [[0]*area_of_intrest[0] for _ in range(area_of_intrest[1])]

    for i in range(len(_x)):
        x_val = floor(_x[i]+area_of_intrest[0]/2)
        y_val = floor(_y[i]+area_of_intrest[1]/2)
        if y_val < 0 or y_val > area_of_intrest[1] or x_val < 0 or x_val > area_of_intrest[0]:
            continue
        img_bin[x_val][y_val]=True

    theta1 = np.linspace(-90, 0, ceil(90/theta_res) + 1)
    theta1 = np.concatenate((theta1, -theta1[len(theta1)-2::-1]))

    D = np.sqrt((nR - 1)**2 + (nC - 1)**2)

    q = np.ceil(D/rho_res)
    nrho = 2*q + 1

    #print(f"D: {D} q:{q} nrho: {nrho}")
    rho1 = np.linspace(int(-q*rho_res), int(q*rho_res), int(nrho))
    H = np.zeros((len(rho1), len(theta1)))
    for rowIdx in range(nR):
        for colIdx in range(nC):
          if img_bin[rowIdx][colIdx]:
            for thIdx in range(len(theta1)):
              rhoVal = colIdx*np.cos(theta1[thIdx]*np.pi/180.0) + \
                  rowIdx*np.sin(theta1[thIdx]*np.pi/180)
              rhoIdx = np.nonzero(np.abs(rho1-rhoVal) == np.min(np.abs(rho1-rhoVal)))[0]
              H[rhoIdx[0]][thIdx] += 1
    print("Hough found ",f"{time()-start} s")
    return rho1, theta1, H , q

"""
def hough1(x,y):
    hough=[[0]*10000 for _ in range(180)]
    points = []
    for i in range(len(x)):
        points.append((x[i],y[i]))

    rad = 180/pi

    for a,point1 in enumerate(points):
        for b,point2 in enumerate(points):
            if a != b:

                angle = rad*atan((point1[0]-point2[0])/(point2[1]-point1[1]))
                radius = point2[0]*cos(angle)+point2[1]*sin(angle)
                if not on_line(point1[0],point2[1],point2[0],point1[1],radius,angle):
                    radius = -radius
                #print(f"a:{a} b: {b}")
                #print(f"angle:{angle} r: {radius}")

                hough[floor(angle+angle_t)][floor((radius+rad_t))]+=1


    return hough


def on_line(p1x,p1y,p2x,p2y,r,th):
    slope = (p2y-p1y)/(p2x-p1x)
    perp_point = (cos(th*pi/180)*r,sin(th*pi/180)*r)
    new_slope = (perp_point[1]-p1y)/(perp_point[0]-p1x)
    if abs(slope - new_slope) < 0.1 :
        return True
        print("found perp")
    else:
        return False

def find_maxs(hough,precentile):
    max = 0
    for a in hough:
        for b in a:
            if b > max:
                max = b
    print(max)
    for t,a in enumerate(hough):
        for r,b in enumerate(a):
            b = b*100/max
            if b<precentile:
                b = 0
            else:
                print(f"{t-angle_t} {r-rad_t} {b}")
                if t == 0:
                    continue
                m = -1/tan((t-angle_t)*pi/180)
                bb = (r-rad_t)/sin((t-angle_t)*pi/180)
                lines.append((m,bb))
    print(lines)
    return hough



def draw_lines(lines):  #(m,b)
    fig = plt.figure()
    axa = fig.add_subplot(1, 1, 1)

    tt = np.linspace(-4000,4000,1)
    for line in lines:
        ff = line[0]*tt+line[1]
        plt.plot(tt, ff, '-r')
    #plt.grid()

"""
def point_in_range(theta,last,next):

    for angle in theta:
        if angle < next and angle > last:

            return True
    return False


def break_lines(theta,r,res):   #try to segregate lines
    line_list = []

    rotation = [0]*360
    break_list = []
    linex = []
    liney = []
    last=0
    for _deg in range(0,360,res):
        if point_in_range(theta,last,_deg):
            for _arc in range(last,last+res,1):
                #print(last,_arc)
                rotation[_arc]=1
        last = _deg
    #print(rotation)
    for i,_deg in enumerate(rotation):
        if i == len(rotation)-1:
            sobel = _deg - rotation[0]
        elif i == 0:
            sobel = _deg - rotation[len(rotation)-1]
        else:
            sobel = _deg - rotation[i+1]
        break_list.append(sobel)
    #print(len(break_list),break_list)
    _on = False
    last_rise = 0
    first = True
    for index,edge in enumerate(break_list):


        if edge == -1:
            last_rise = index
            _on = True
            if first:
                first = False

            continue

        if edge == 1:
            if _on:
                for i in range(len(theta)):
                    if theta[i] > last_rise and theta[i] < index:
                        linex.append(floor(cos(float(theta[i])*rad)*float(r[i])))
                        liney.append(floor(-sin(float(theta[i])*rad)*float(r[i])))
                if len(linex) > 4:
                    line_list.append((linex,liney))
                linex = []
                liney = []
            elif first:
                for i in range(len(theta)):
                    if theta[i] > 0 and theta[i] < index:
                        linex.append(floor(cos(float(theta[i])*rad)*float(r[i])))
                        liney.append(floor(-sin(float(theta[i])*rad)*float(r[i])))
                if len(linex) > 4:
                    line_list.append((linex,liney))
            _on = False
            continue


    if _on == True:
        for i in range(len(theta)):
            if theta[i] > last_rise and theta[i] < 360:
                linex.append(floor(cos(float(theta[i])*rad)*float(r[i])))
                liney.append(floor(-sin(float(theta[i])*rad)*float(r[i])))
        if len(linex) > 4:
            line_list.append((linex,liney))


    return line_list

def break_lines2(_x,_y,_t,_r,_res):
    break_midpoint = []
    condit = [] #rise = 1, fall = -1
    sobel = []
    index = []
    linex = []
    liney = []
    line_list  =[]
    print(len(_x))
    for i in range(len(_x)):
        if i < len(_x) - 1 and i > 0:
            m1 = (_y[i]-_y[i+1])/(_x[i]-_x[i+1])
            m2 = (_y[i]-_y[i-1])/(_x[i]-_x[i-1])
            err = 2*(m1-m2)/(m1+m2)
            print(i,err)
            if abs(err) > _res:
                break_midpoint.append(((_x[i]+_x[i+1])/2, (_y[i]+_y[i+1])/2))
                index.append(i)
                if _r[i] < _r[i+1]:
                    condit.append(1)
                else:
                    condit.append(-1)
                i +=1

        elif i ==0:
            m1 = (_y[i]-_y[i+1])/(_x[i]-_x[i+1])
            m2 = (_y[i]-_y[len(_x)-1])/(_x[i]-_x[len(_x)-1])
            err = 2*(m1-m2)/(m1+m2)
            if abs(err) > _res:
                break_midpoint.append(((_x[i]+_x[i+1])/2, (_y[i]+_y[i+1])/2))
                index.append(i)
                if _r[i] < _r[i+1]:
                    condit.append(1)
                else:
                    condit.append(-1)
                i +=1

        elif i == len(_x)-1:
            m1 = (_y[i]-_y[0])/(_x[i]-_x[0])
            m2 = (_y[i]-_y[i-1])/(_x[i]-_x[i-1])
            err = 2*(m1-m2)/(m1+m2)
            if abs(err) > _res:
                break_midpoint.append(((_x[i]+_x[0])/2, (_y[i]+_y[0])/2))
                index.append(i)
                if _r[i] < _r[0]:
                    condit.append(1)
                else:
                    condit.append(-1)

    print("here")
    _on = True
    last_rise = 0
    for k,edge in enumerate(condit):
        if edge == 1:
            last_rise = index[k]
            _on = True
            continue
            print(k,index[k])

        if edge == -1:
            if _on:
                for i in range(last_rise,k,1):
                        linex.append(_x[i])
                        liney.append(_y[i])
                if len(linex) > 4:
                    line_list.append((linex,liney))
                linex = []
                liney = []
            _on = False
            continue

    """
    if _on == True:
        while(_on):
            k = 0
            if condit[k] == -1:
                for i in range(last_rise,len(condit-1),1):
                        linex.append(_x[i])
                        liney.append(_y[i])
                for i in range(0,k,1):
                        linex.append(_x[i])
                        liney.append(_y[i])
                if len(linex) > 4:
                    line_list.append((linex,liney))
                linex = []
                liney = []
                _on = False
                break
            else:
                k += 1
    """
    return line_list

theta=[]
r=[]
points = []
lines=[]
start = time()
print("starting")
print("Processing CSV")
with open('static_ahead_data_1611711547.7482073.csv', 'r') as csvfile:
    plots= csv.reader(csvfile, delimiter=',')
    for k, row in enumerate(plots):
        if row[0] == 'time added':
            continue

        if k < 3415:
            continue
        elif k > 3717:
            break

        if float(row[2]) > 1 and float(row[3])<10000 and float(row[3]) > 200:
            #print(f"k: {k} theta: {row[1]} distance: {row[3]}")
            rad = pi/180
            theta.append(float(row[1]))
            r.append(float(row[3]))
            tx = cos(float(row[1])*rad)*float(row[3])
            ty = -sin(float(row[1])*rad)*float(row[3])
            x.append(tx)
            y.append(ty)
            points.append((tx,ty))

print("CSV processed ", f"{time()-start} s")

def forceAspect(ax,aspect=1):
    im = ax.get_images()
    extent =  im[0].get_extent()
    ax.set_aspect(abs((extent[1]-extent[0])/(extent[3]-extent[2]))/aspect)


def print_stuff(_x,_y,i):
    fig = plt.figure()
    ax = fig.add_subplot(111)
    h = hough2(_x,_y)
    #print(len(h[2]),h)
    plt.imshow(h[2])
    ax.set_aspect(2)
    forceAspect(ax,aspect=1)
    #fig.savefig(f'force{i}.png')


def print_houghs(line_list):
    for i,list in enumerate(line_list):
        _x,_y = list
        #print("\n",i,len(list[1]),list)
        print_stuff(_x,_y,i)
    #print_stuff(line_list[0][0],line_list[0][1],10)

def find_hough_lines(lines):
    hough_vals = []
    line_vals = []
    for line in lines:
        print("Finding hough")
        _x,_y = line
        h = hough2(_x,_y)
        #print(len(h[1]),h)
        max = 0
        max_pos = ()
        for r,angle in enumerate(h[2]):
            for th,val in enumerate(angle):
                if val > max:
                    max = val
                    temp_pos = (th,r)
                    max_pos = (180-th*theta_res,(r*rho_res)-11350)
        if max == 0:
            continue
        else:
            print(max,temp_pos)
            print(max_pos)
            hough_vals.append(max_pos)


    for pair in hough_vals:
        m = -1/tan((pair[0])*pi/180)
        bb = (pair[1])/sin((pair[0])*pi/180)
        line_vals.append((m,bb))

    return line_vals

def print_lines(standard_lines,broken_lines):
    fig2 = plt.figure()
    ax2 = fig2.add_subplot(111)
    for line in standard_lines:
        _x = np.linspace(-4000,4000,10)

        #plt.plot(_x, line[0]*_x+line[1]-4000*line[0]+4000, '-r')
        plt.plot(_x, line[0]*_x+line[1]-4000+4000*line[0])

    #for a in range(len(x)):
    #    x2,y2 = (x[a]-4000,y[a]-4000)
    #c2 = ax2.scatter(x,y,s=2)
    for i in broken_lines:
        xx,yy = i
        printxy(xx,yy,ax2)
    #plt.xlim([-4000,4000])
    #plt.ylim([-4000,4000])


def printxy(_x,_y,ax):

    c = ax.scatter(_x,_y,s=10)
    plt.xlim([-4000,4000])
    plt.ylim([-3000,2000])
print("breaking lines")

fig1 = plt.figure()
ax1 = fig1.add_subplot(111)
printxy(x,y,ax1)

broken_lines = break_lines(theta,r,2)

broken_lines = broken_lines[1:]
print("lines broken ",f"{time()-start} s")
#print(broken_lines)
#broken_lines = break_lines2(x,y,theta,r,0.8)
#fig6 = plt.figure()
#ax6 = fig6.add_subplot(111)
"""
for i in broken_lines:
    xx,yy = i
    printxy(xx,yy,ax6)
"""
#fig7 = plt.figure()
#ax7 = fig7.add_subplot(111)

#print(broken_lines)
#print("printing houghs")
print_houghs(broken_lines)

#print("Houghs printed ",f"{time()-start} s")
print("creating standard lines")
standard_lines = find_hough_lines(broken_lines)
print("standard lines found ",f"{time()-start} s")
print(f"standard_lines {standard_lines}")
print("printing lines")
print_lines(standard_lines,broken_lines)
print("lines printed",f"{time()-start} s")
plt.show()


#plt.imshow(hough1(x,y))
#fig1 = plt.figure()
#ax1 = fig1.add_subplot(111,projection ='polar')

#print(h)
#plt.imshow(h)
#h = hough2(x,y)
#plt.imshow(h[2])

"""
#plt.imshow(find_maxs(h,50),interpolation='none', extent=[-5000,5000,-90,90])
#c1 = ax3.scatter(h[0],h[1],s=2)

fig2 = plt.figure()
ax2 = fig2.add_subplot(111)
c2 = ax2.scatter(x,y,s=2)
plt.xlim([-4000,4000])
plt.ylim([-4000,4000])

#draw_lines(lines)
#fig = plt.figure()
#ax = fig.add_subplot(1, 1, 1)
x = np.linspace(-4000,4000,10)

plt.plot(x, -0.123*x+713, '-r', label='y=2x+1')
plt.xlim([-4000,4000])
plt.ylim([-4000,4000])

plt.show()
"""
plt.show()
