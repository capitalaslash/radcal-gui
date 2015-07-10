#! /usr/bin/env python2

import math
from vtk import *

class Data:
    def __init__(self, config):
        self.config = config

        self.initGrid()
        self.initPointData()
        self.initCellData()

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
        writer = vtk.vtkXMLRectilinearGridWriter()
        writer.SetInputData(self.grid)
        writer.SetFileName('grid.vtr')
        writer.SetDataModeToAscii()
        writer.Write()

if __name__ == '__main__':
    from config import *

    data = Data(config)

    data.write()
