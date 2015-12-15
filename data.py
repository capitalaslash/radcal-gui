#! /usr/bin/env python2

import math
import vtk

class Data(object):
    def __init__(self, **config):
        # print 'data configuration:', config
        self.config = config
        self.grid = []
        self.num_times = 0
        self.times = []

    def read(self):
        f = open(self.config['filename'])

        # first line is number of points
        words = f.readline().split()
        num_pts = int(words[2])
        print 'number of points =', num_pts

        # second line is number of timesteps
        self.num_times = int(f.readline().split()[2])
        print 'number of times =', self.num_times

        # third line used for var names
        titles = f.readline().split()

        # ignore '#', 'x', 'y', 'z', 't'
        num_vars = len(titles)-5
        var_names = []
        for v in range(0, num_vars):
            var_names.append(titles[5+v])
        print 'variables:', var_names


        for t in xrange(0, self.num_times):
            var_list = []
            for v in range(0, num_vars):
                var = vtk.vtkFloatArray()
                var.SetName(var_names[v])
                var.SetNumberOfValues(num_pts)
                var_list.append(var)

            pts = vtk.vtkPoints()
            pts.SetNumberOfPoints(num_pts)
            for i in xrange(0, num_pts):
                words = f.readline().split()
                p = [float(words[0]), float(words[1]), float(words[2])]
                time = float(words[3])
                pts.SetPoint(i, p)
                for v in range(0, num_vars):
                    var_list[v].SetValue(i, float(words[4+v]))
            self.times.append(time)

            # delaunay
            profile = vtk.vtkPolyData()
            profile.SetPoints(pts)
            point_data = profile.GetPointData()
            for v in range(0, num_vars):
                point_data.AddArray(var_list[v])
            point_data.SetActiveScalars(var_list[0].GetName())

            self.grid.append(vtk.vtkDelaunay3D())
            if vtk.VTK_MAJOR_VERSION <= 5:
                self.grid[t].SetInput(profile)
            else:
                self.grid[t].SetInputData(profile)
            self.grid[t].SetTolerance(0.01)
            self.grid[t].SetAlpha(0.0)
            self.grid[t].BoundingTriangulationOff()

    def get_varnames(self):
        point_data = self.grid[0].GetInput().GetPointData()
        num_vars = point_data.GetNumberOfComponents()
        varnames = []
        for i in range(0, num_vars):
            varnames.append(point_data.GetArray(i).GetName())
        return varnames

    def write(self, filename):
        if filename[-4:] == '.vtu':
            filename = filename[:-4]
        writer = vtk.vtkXMLDataSetWriter()
        writer.SetDataModeToAscii()
        for t in xrange(0, self.num_times):
            filename_time = '{:s}.{:03d}.vtu'.format(filename, t)
            print "printing {:s} ...".format(filename_time)
            writer.SetInputConnection(self.grid[t].GetOutputPort())
            writer.Setfilename(filename_time)
            writer.Write()

if __name__ == '__main__':
    from config import Data

    data = Data(filename='test.dat')

    data.read()

    data.write('grid.vtu')
