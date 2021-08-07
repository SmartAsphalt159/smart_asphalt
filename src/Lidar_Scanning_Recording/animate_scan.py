import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from math import sin, cos, pi, tan, atan, floor, ceil,sqrt
from time import time,sleep
import csv
from time import time, sleep


def polar_to_cartesian(angle,distance):
    #may need to change due to reflection issues
    tx_ = np.cos((float(angle)*np.pi/180))*float(distance)
    ty_ = -np.sin((float(angle)*np.pi/180))*float(distance)

    cartesian = (tx_,ty_)
    return cartesian


"""
    name = input("name of file\n")
    graph_data = open(name,'r').read()
    lines = graph_data.split('\n')
"""
theta = []
r = []
points = [[],[]]
lines=[]
start = time()
tx = []
ts = []
ty = []
_x = []
_y = []
ths = []
ds = []

xs = []
ys = []
nx = ny = [0]


with open('Example_Data/move_straight_data_1611711796.9998024.csv', 'r') as csvfile:     # change to file name
    plots = csv.reader(csvfile, delimiter=',')
    for k, row in enumerate(plots):
        if row[0] == 'time added':
            continue

        try:
            a = row[3]
        except IndexError:
            continue

        if float(row[2]) > 1 and float(row[3])<10000 and float(row[3]) > 200:
            theta = np.append(theta,[float(row[1])])
            r.append(float(row[3]))
            ts.append(float(row[0]))
            c = polar_to_cartesian(row[1],row[3])
            _x.append(c[0])
            _y.append(c[1])
            points[0].append(c[0])
            points[1].append(c[1])

interval_ms = 10 # delay between frames in ms
interval_s = interval_ms/1000
start_time = ts[0]
end_time = ts[len(ts)-1]
frames = np.arange(round(start_time,3),round(end_time,3),interval_s)

fig, ax = plt.subplots()


ax = plt.axis([-6000,6000,-6000,6000])

points, = plt.plot([0], [0], 'r.')
print("initializing")
sleep(5)


count = 0
def animate1(t):
    global count
    x = []
    y = []

    _theta = []
    _r = []
    index = 0
    for i,t_ in enumerate(ts):
        if t_ > t:
            index = i
            break
    if i > 150:
        num = 150
    else:
        num = i

    for j in range(i-num,i,1):
        x.append(_x[j])
        y.append(_y[j])
        _theta.append(theta[j])
        _r.append(r[j])

    points.set_data(x, y)
    return points


# Formatting for movie file
Writer = animation.writers['ffmpeg']
write = Writer(fps=15, metadata=dict(artist='Me'), bitrate=1800)
# create animation using the animate() function
myAnimation = animation.FuncAnimation(fig, animate1, frames=frames, interval=interval_ms, repeat=True)
myAnimation.save("move_straight.mp4", writer=write)

#plt.show()
