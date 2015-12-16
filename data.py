#! /usr/bin/env python2

import os
import vtk
import numpy as np
import reorder

class Data(object):
    """A class for reading and writing the mesh and its variables."""
    def __init__(self, **config):
        # print 'data configuration:', config
        self.config = config
        self.grid = []
        self.num_times = 0
        self.times = []

    def read(self):
        self.num_times = 1
        self.times = [0.0]

        filename = self.config['filename']
        # check if we are reading a ground or air conc
        if filename.find('Gconc') != -1:
            dim = 2
            cell_type = vtk.VTK_QUAD
        else:
            dim = 3
            cell_type = vtk.VTK_HEXAHEDRON

        print 'reading data...'
        data = np.genfromtxt(filename, delimiter=',')
        data = reorder.reorder(data, 0, dim)
        print 'done'

        num_pts = data.shape[0]

        var = vtk.vtkFloatArray()
        varname = os.path.basename(filename).split('_')[0]
        var.SetName(varname)
        var.SetNumberOfValues(num_pts)

        print 'creating points...'
        pts = vtk.vtkPoints()
        pts.SetNumberOfPoints(num_pts)
        if dim == 2:
            for i in xrange(0, num_pts):
                pts.SetPoint(i, data[i,0], data[i,1], 0.0)
                var.SetValue(i, data[i,2])
        else:
            for i in xrange(0, num_pts):
                pts.SetPoint(i, data[i,0], data[i,1], data[i,2])
                var.SetValue(i, data[i,3])
        print 'done'

        print 'creating cells...'
        cell_array = vtk.vtkCellArray()
        coord_x, indices = np.unique(data[:,0], return_index=True)
        indices_x = np.append(indices, num_pts)
        if dim == 2:
            for i in xrange(0, coord_x.shape[0]-1):
                for j in xrange(0, indices_x[i+1]-indices_x[i]-1):
                    quad = vtk.vtkQuad()
                    quad.GetPointIds().SetId(0, indices_x[i]  +j)
                    quad.GetPointIds().SetId(1, indices_x[i+1]+j)
                    quad.GetPointIds().SetId(2, indices_x[i+1]+j+1)
                    quad.GetPointIds().SetId(3, indices_x[i]  +j+1)
                    cell_array.InsertNextCell(quad)

        else:
            for i in xrange(0, coord_x.shape[0]-1):
                plane_b = data[indices_x[i]:indices_x[i+1]]
                coord_y_b, indices_y_b = np.unique(plane_b[:,1], return_index=True)
                indices_y_b = np.append(indices_y_b, plane_b.shape[0])

                plane_f = data[indices_x[i+1]:indices_x[i+2]]
                coord_y_f, indices_y_f = np.unique(plane_f[:,1], return_index=True)
                indices_y_f = np.append(indices_y_f, plane_f.shape[0])

                for j in xrange(0, coord_y_b.shape[0]-1):
                    for k in xrange(0, indices_y_b[j+2]-indices_y_b[j+1]-1):
                        hexa = vtk.vtkHexahedron()
                        p = []
                        p.append(indices_x[i]  +indices_y_b[j]  +k  )
                        p.append(indices_x[i]  +indices_y_b[j+1]+k  )
                        p.append(indices_x[i]  +indices_y_b[j+1]+k+1)
                        p.append(indices_x[i]  +indices_y_b[j]  +k+1)
                        p.append(indices_x[i+1]+indices_y_f[j]  +k  )
                        p.append(indices_x[i+1]+indices_y_f[j+1]+k  )
                        p.append(indices_x[i+1]+indices_y_f[j+1]+k+1)
                        p.append(indices_x[i+1]+indices_y_f[j]  +k+1)
                        hexa = vtk.vtkHexahedron()
                        for l in range(0,8):
                            hexa.GetPointIds().SetId(l, p[l])
                        cell_array.InsertNextCell(hexa)
        print 'done'

        self.grid.append(vtk.vtkUnstructuredGrid())
        self.grid[0].SetPoints(pts)
        self.grid[0].SetCells(cell_type, cell_array)
        self.grid[0].GetPointData().SetScalars(var)

    def get_varnames(self):
        point_data = self.grid[0].GetPointData()
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
            writer.SetInputData(self.grid[t])
            writer.Setfilename(filename_time)
            writer.Write()

if __name__ == '__main__':
    from config import Data

    data = Data(filename='data/Co-60_Gconc_012h.txt')

    data.read()

    data.write('grid.vtu')
