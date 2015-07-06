#! /usr/bin/env python2

from vtk import *

class Data:
    def __init__(self, config):
        self.config = config

        self.initGrid()
        self.initCellData()

    def initGrid(self):
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
