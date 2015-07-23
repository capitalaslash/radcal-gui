#! /usr/bin/env python2

import math
# import vtk

class Point(object):
    def __init__(self):
        self.x = 0.0
        self.y = 0.0
        self.z = 0.0

    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def __add__(self, other):
        return Point(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other):
        return Point(self.x - other.x, self.y - other.y, self.z - other.z)

    def __mul__(self, other):
        return self.x*other.x + self.y*other.y + self.z*other.z

    def __repr__(self):
        return '(' + repr(self.x) + ', ' + repr(self.y) + ', ' + repr(self.z) +  ')'

class Grid(object):
    def __init__(self, **opts):
        nx = opts['nx']
        ny = opts['ny']
        nz = opts['nz']
        o = opts['o']
        l = opts['l']
        h = ((l[0]-o[0])/(nx-1), (l[1]-o[1])/(ny-1), (l[2]-o[2])/(nz-1))

        self.points = []
        counter = 0
        for k in range(0, nz):
            for j in range(0, ny):
                for i in range(0, nx):
                    p = Point(o[0]+i*h[0], o[1]+j*h[1], o[2]+k*h[2])
                    self.points.append(p)
                    counter += 1
        self.numPoints = counter

class TimeRange(object):
    def __init__(self, **opts):
        ti = opts['ti']
        tf = opts['tf']
        dt = opts['dt']
        self.nt = 1+int((tf-ti)/dt)
        self.times = []

        for i in range(0, self.nt):
            self.times.append(ti + i*dt)

class Function(object):
    def __init__(self, fun, grid, time):
        self.values = []

        for t in range(0, time.nt):
            values = []
            for i in range(0, grid.numPoints):
                values.append(fun(grid.points[i], time.times[t]))
            self.values.append(values)

def fun1(p, t):
    return math.exp(p.x)*(1.0-t)

def fun2(p, t):
    return 1.0 + 0.05*p.x + 0.1*p.y + 0.6*p.z

c = Point(0.5, 0.2, 0.0)
s = 1.2
def fun3(p, t):
    return math.exp(-((p-c)*(p-c))/(2*s*s))/(math.sqrt(2*math.pi)*s)*(1.0-t)


if __name__ == '__main__':
    opts = {'nx': 8, 'ny': 10, 'nz': 3,
        'o': [0.0, 0.0, 0.0],
        'l': [2.0, 3.0, 1.0]}
    grid = Grid(**opts)

    time = TimeRange(ti=0.0, tf=1.0, dt=0.2)

    f1 = Function(fun1, grid, time)
    f2 = Function(fun2, grid, time)
    f3 = Function(fun3, grid, time)

    # print
    f = open('test.dat', 'w')
    f.write('# points ' + str(grid.numPoints) + '\n')
    f.write('# times ' + str(1) + '\n')
    f.write('# x y z t c1 c2 c3\n')
    for t in range(0, time.nt):
        for i in range(0, grid.numPoints):
            p = grid.points[i]
            f.write('{:e} {:e} {:e} {:e} {:e} {:e} {:e}\n'.format(p.x, p.y, p.z, time.times[t], f1.values[t][i], f2.values[t][i], f3.values[t][i]))
    f.close()
