#! /usr/bin/env python2

import math
from vtk import *

class Data:
    def __init__(self, config):
        self.config = config

    def read(self):
        f = open(self.config['fileName'])

        # first line is number of points
        words = f.readline().split()
        numPts = int(words[2])

        # second line is number of timesteps
        numTimes = int(f.readline().split()[2])

        # third line used for var names
        titles = f.readline().split()

        # ignore '#', 'x', 'y', 'z', 't'
        numVars = len(titles)-5
        varList = []
        for v in range(0, numVars):
            name = titles[5+v]
            print 'creating array', name
            var = vtkFloatArray()
            var.SetName(name)
            var.SetNumberOfValues(numPts)
            varList.append(var)

        pts = vtkPoints()
        pts.SetNumberOfPoints(numPts)
        counter = 0
        for line in f:
            words = line.split()
            p = [float(words[0]), float(words[1]), float(words[2])]
            pts.SetPoint(counter, p)
            for v in range(0, numVars):
                varList[v].SetValue(counter, float(words[4+v]))
            counter = counter+1

        # # build a fake unstructured grid
        # self.grid = vtkUnstructuredGrid()
        # self.grid.SetPoints(pts)
        #
        # self.grid.Allocate(numCells, numCells)
        # for k in xrange(0, nz-1):
        #     for j in xrange(0, ny-1):
        #         for i in xrange(0, nx-1):
        #             hexa = vtk.vtkHexahedron()
        #             idx = i + nx*(j + ny*k)
        #             hexa.GetPointIds().SetId(0, idx)
        #             hexa.GetPointIds().SetId(1, idx+1)
        #             hexa.GetPointIds().SetId(2, idx+1+nx)
        #             hexa.GetPointIds().SetId(3, idx  +nx)
        #             hexa.GetPointIds().SetId(4, idx     +nx*ny)
        #             hexa.GetPointIds().SetId(5, idx+1   +nx*ny)
        #             hexa.GetPointIds().SetId(6, idx+1+nx+nx*ny)
        #             hexa.GetPointIds().SetId(7, idx+ +nx+nx*ny)
        #             self.grid.InsertNextCell(hexa.GetCellType(),
        #                 hexa.GetPointIds())
        # for v in range(0, numVars):
        #     self.grid.GetPointData().AddArray(varList[v])
        # self.grid.GetPointData().SetActiveScalars(varList[0].GetName())

        # delaunay
        profile = vtkPolyData()
        profile.SetPoints(pts)
        for v in range(0, numVars):
            profile.GetPointData().AddArray(varList[v])
        profile.GetPointData().SetActiveScalars(varList[0].GetName())

        self.grid = vtkDelaunay3D()
        self.grid.SetInputData(profile)
        self.grid.SetTolerance(0.01)
        self.grid.SetAlpha(0.0)
        self.grid.BoundingTriangulationOff()

    def initGrid(self):
        config = self.config
        nx = config['grid_nx']
        ny = config['grid_ny']
        nz = config['grid_nz']

        o = config['grid_origin']
        l = config['grid_length']

        h = [(l[0]-o[0])/nx, (l[1]-o[1])/ny, (l[2]-o[2])/nz]

        xCoords = vtkFloatArray()
        xCoords.SetName('xCoords')
        xCoords.SetNumberOfValues(nx+1)
        for i in xrange(0, nx+1):
            xCoords.SetValue(i, o[0] + h[0]*i)

        yCoords = vtkFloatArray()
        yCoords.SetName('yCoords')
        yCoords.SetNumberOfValues(ny+1)
        for j in xrange(0, ny+1):
            yCoords.SetValue(j, o[1] + h[1]*j)

        zCoords = vtkFloatArray()
        zCoords.SetName('zCoords')
        zCoords.SetNumberOfValues(nz+1)
        for k in xrange(0, nz+1):
            zCoords.SetValue(k, o[2] + h[2]*k)

        self.grid = grid = vtkRectilinearGrid()
        grid.SetDimensions(nx+1, ny+1, nz+1)
        grid.SetXCoordinates(xCoords)
        grid.SetYCoordinates(yCoords)
        grid.SetZCoordinates(zCoords)

    def initCellData(self):
        numCells = self.grid.GetNumberOfCells()

        idData = vtkIntArray()
        idData.SetName('id')
        idData.SetNumberOfValues(numCells)
        for i in xrange(0, numCells):
            idData.SetValue(i, i)

        self.grid.GetCellData().AddArray(idData)
        self.grid.GetCellData().SetActiveScalars('id')

    def initPointData(self):
        grid = self.grid
        o = self.config['grid_origin']
        l = self.config['grid_length']
        mean1 = (0.5*l[0], 0.1*l[1], 0.0*l[2])
        sigma1 = 1.2
        mean2 = (0.5*l[0], 0.1*l[1], 0.0*l[2])
        sigma2 = 1.6

        numPts = grid.GetNumberOfPoints()
        c1 = vtkFloatArray()
        c1.SetName('c1')
        c1.SetNumberOfTuples(numPts)
        c2 = vtkFloatArray()
        c2.SetName('c2')
        c2.SetNumberOfTuples(numPts)
        for i in xrange(0, numPts):
            p = grid.GetPoint(i)
            dist = (p[0]-mean1[0])*(p[0]-mean1[0])+(p[1]-mean1[1])*(p[1]-mean1[1])+(p[2]-mean1[2])*(p[2]-mean1[2])
            gauss = math.exp(- dist / (2*sigma1*sigma1)) / (math.sqrt(2*math.pi)*sigma1)
            c1.SetValue(i, gauss)
            dist = (p[0]-mean2[0])*(p[0]-mean2[0])+(p[1]-mean2[1])*(p[1]-mean2[1])+(p[2]-mean2[2])*(p[2]-mean2[2])
            gauss = math.exp(- dist / (2*sigma2*sigma2)) / (math.sqrt(2*math.pi)*sigma2)
            c2.SetValue(i, gauss)

        grid.GetPointData().AddArray(c1)
        grid.GetPointData().AddArray(c2)
        grid.GetPointData().SetActiveScalars('c1')

        numPoints = self.grid.GetNumberOfPoints()

        idData = vtkIntArray()
        idData.SetName('id')
        idData.SetNumberOfValues(numPoints)
        for i in xrange(0, numPoints):
            idData.SetValue(i, i)
        self.grid.GetPointData().AddArray(idData)

    def getVarList(self):
        pointData = self.grid.GetPointData()
        numVars = pointData.GetNumberOfComponents()
        varNames = []
        for i in range(0, numVars):
            varNames.append(pointData.GetArray(i).GetName())
        print varNames
        return varNames

    def write(self):
        writer = vtk.vtkXMLDataSetWriter()
        writer.SetInputConnection(self.grid.GetOutputPort())
        writer.SetFileName('grid.vtu')
        writer.SetDataModeToAscii()
        writer.Write()

if __name__ == '__main__':
    from config import *

    config['fileName'] = 'test_notime.dat'
    data = Data(config)

    data.read()

    data.write()
