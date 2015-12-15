import numpy as np

def reorder_3d(**kwargs):
    """Reorder a RADCAL-III air output file so that all variables are ascending"""

    if not 'filename_in' in kwargs:
        "no input filename provided. aborting"
        return 1
    filename_in = kwargs['filename_in']

    if not 'filename_out' in kwargs:
        "no output filename provided. aborting"
        return 1
    filename_out = kwargs['filename_out']

    data = np.genfromtxt(filename_in, delimiter=',')

    data = data[data[:,0].argsort()]
    coord_x, indices_x = np.unique(data[:,0], return_index=True)
    indices_x = np.append(indices_x, data.shape[0])

    for i in range(0, coord_x.shape[0]):
        plane = data[indices_x[i]:indices_x[i+1]]
        coord_y, indices_y = np.unique(plane[:,1], return_index=True)
        indices_y = np.append(indices_y, plane.shape[0])
        plane = plane[plane[:,1].argsort()]
        for j in range(0, coord_y.shape[0]):
            line = plane[indices_y[j]:indices_y[j+1]]
            line = line[line[:,2].argsort()]
            plane[indices_y[j]:indices_y[j+1]] = line

        data[indices_x[i]:indices_x[i+1]] = plane

    np.savetxt(filename_out, data, delimiter=', ')

if __name__ == '__main__':
    import sys
    import os
    if len(sys.argv) < 2:
        print 'missing filename'
        exit(1)

    infile = sys.argv[1]
    basename, ext = os.path.splitext(infile)
    outfile = basename + '_ordered' + ext

    reorder_3d(filename_in=infile, filename_out=outfile)
