#! /usr/bin/env python2

import math
import vtk

class Data(object):
    def __init__(self, **config):
        # print 'data configuration:', config
        self.config = config
        self.grid = []
        self.numTimes = 0
        self.times = []

    def read(self):
        f = open(self.config['fileName'])

        # first line is number of points
        words = f.readline().split()
        numPts = int(words[2])
        print 'numPoints =', numPts

        # second line is number of timesteps
        self.numTimes = int(f.readline().split()[2])
        print 'numTimes =', self.numTimes

        # third line used for var names
        titles = f.readline().split()

        # ignore '#', 'x', 'y', 'z', 't'
        numVars = len(titles)-5
        varNames = []
        for v in range(0, numVars):
            varNames.append(titles[5+v])
        print 'variables:', varNames


        for t in xrange(0, self.numTimes):
            varList = []
            for v in range(0, numVars):
                var = vtk.vtkFloatArray()
                var.SetName(varNames[v])
                var.SetNumberOfValues(numPts)
                varList.append(var)

            pts = vtk.vtkPoints()
            pts.SetNumberOfPoints(numPts)
            for i in xrange(0, numPts):
                words = f.readline().split()
                p = [float(words[0]), float(words[1]), float(words[2])]
                time = float(words[3])
                pts.SetPoint(i, p)
                for v in range(0, numVars):
                    varList[v].SetValue(i, float(words[4+v]))
            self.times.append(time)

            # delaunay
            profile = vtk.vtkPolyData()
            profile.SetPoints(pts)
            for v in range(0, numVars):
                profile.GetPointData().AddArray(varList[v])
            profile.GetPointData().SetActiveScalars(varList[0].GetName())

            self.grid.append(vtk.vtkDelaunay3D())
            if vtk.VTK_MAJOR_VERSION <= 5:
                self.grid[t].SetInput(profile)
            else:
                self.grid[t].SetInputData(profile)
            self.grid[t].SetTolerance(0.01)
            self.grid[t].SetAlpha(0.0)
            self.grid[t].BoundingTriangulationOff()

    def getVarList(self):
        pointData = self.grid[0].GetInput().GetPointData()
        numVars = pointData.GetNumberOfComponents()
        varNames = []
        for i in range(0, numVars):
            varNames.append(pointData.GetArray(i).GetName())
        return varNames

    def write(self, fileName):
        if fileName[-4:] == '.vtu':
            fileName = fileName[:-4]
        writer = vtk.vtkXMLDataSetWriter()
        writer.SetDataModeToAscii()
        for t in xrange(0, self.numTimes):
            fileNameT = '{:s}.{:03d}.vtu'.format(fileName, t)
            print "printing {:s} ...".format(fileNameT)
            writer.SetInputConnection(self.grid[t].GetOutputPort())
            writer.SetFileName(fileNameT)
            writer.Write()

if __name__ == '__main__':
    from config import Data

    data = Data(fileName='test.dat')

    data.read()

    data.write('grid.vtu')
