#! /usr/bin/env python2

import math
import vtk

class Data:
    def __init__(self, **config):
        print 'data configuration:', config
        self.config = config

    def read(self):
        f = open(self.config['fileName'])

        # first line is number of points
        words = f.readline().split()
        numPts = int(words[2])
        print 'numPoints =', numPts

        # second line is number of timesteps
        numTimes = int(f.readline().split()[2])
        print 'numTimes =', numTimes

        # third line used for var names
        titles = f.readline().split()

        # ignore '#', 'x', 'y', 'z', 't'
        numVars = len(titles)-5
        varList = []
        for v in range(0, numVars):
            name = titles[5+v]
            print 'creating array', name
            var = vtk.vtkFloatArray()
            var.SetName(name)
            var.SetNumberOfValues(numPts)
            varList.append(var)

        pts = vtk.vtkPoints()
        pts.SetNumberOfPoints(numPts)
        for i in xrange(0, numPts):
            words = f.readline().split()
            p = [float(words[0]), float(words[1]), float(words[2])]
            pts.SetPoint(i, p)
            for v in range(0, numVars):
                varList[v].SetValue(i, float(words[4+v]))

        # # build a fake unstructured grid
        # self.grid = vtk.vtkUnstructuredGrid()
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
        profile = vtk.vtkPolyData()
        profile.SetPoints(pts)
        for v in range(0, numVars):
            profile.GetPointData().AddArray(varList[v])
        profile.GetPointData().SetActiveScalars(varList[0].GetName())

        self.grid = vtk.vtkDelaunay3D()
        self.grid.SetInputData(profile)
        self.grid.SetTolerance(0.01)
        self.grid.SetAlpha(0.0)
        self.grid.BoundingTriangulationOff()


    def getVarList(self):
        pointData = self.grid.GetInput().GetPointData()
        numVars = pointData.GetNumberOfComponents()
        varNames = []
        for i in range(0, numVars):
            varNames.append(pointData.GetArray(i).GetName())
        print varNames
        return varNames

    def write(self, fileName):
        writer = vtk.vtkXMLDataSetWriter()
        writer.SetInputConnection(self.grid.GetOutputPort())
        writer.SetFileName(fileName)
        writer.SetDataModeToAscii()
        writer.Write()

if __name__ == '__main__':
    from config import *

    data = Data(fileName='test_notime.dat')

    data.read()

    data.write('grid.vtu')
