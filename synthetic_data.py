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

class Function(object):
    def __init__(self, grid, fun):
        self.values = []

        for i in range(0, grid.numPoints):
            self.values.append(fun(grid.points[i]))


def fun1(p):
    return math.exp(p.x)

def fun2(p):
    return 1.0 + 0.05*p.x + 0.1*p.y + 0.6*p.z

c = Point(0.5, 0.2, 0.0)
s = 1.2
def fun3(p):
    return math.exp(-((p-c)*(p-c))/(2*s*s))/(math.sqrt(2*math.pi)*s)


if __name__ == '__main__':
    opts = {'nx': 8, 'ny': 10, 'nz': 3,
        'o': [0.0, 0.0, 0.0],
        'l': [2.0, 3.0, 1.0]}
    grid = Grid(**opts)

    f1 = Function(grid, fun1)
    f2 = Function(grid, fun2)
    f3 = Function(grid, fun3)

    # print
    f = open('test.dat', 'w')
    f.write('# points ' + str(grid.numPoints) + '\n')
    f.write('# times ' + str(1) + '\n')
    f.write('# x y z t c1 c2 c3\n')
    for i in range(0, grid.numPoints):
        p = grid.points[i]
        f.write(str(p.x) + ' ' + str(p.y) + ' ' + str(p.z) + ' ' + str(0.0) + ' ' + str(f1.values[i]) + ' ' + str(f2.values[i]) + ' ' + str(f3.values[i]) + '\n')
    f.close()
