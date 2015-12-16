import numpy as np

def reorder(data, index, maxindex):
    """Reorder numpy array data starting form index and up to maxindex columns."""
    data = data[data[:,index].argsort()]
    index += 1
    if index < maxindex:
        coord, indices = np.unique(data[:,index-1], return_index=True)
        indices = np.append(indices, data.shape[0])
        for i in range(0, coord.shape[0]):
            sub = data[indices[i]:indices[i+1]]
            sub = reorder(sub, index, maxindex)
            data[indices[i]:indices[i+1]] = sub
    return data

def reorder_file(**kwargs):
    """Reorder a RADCAL-III output file so that all variables are ascending."""

    if not 'filename_in' in kwargs:
        "no input filename provided. aborting"
        return 1
    filename_in = kwargs['filename_in']

    if not 'filename_out' in kwargs:
        "no output filename provided. aborting"
        return 1
    filename_out = kwargs['filename_out']

    data = np.genfromtxt(filename_in, delimiter=',')

    if not 'maxindex' in kwargs:
        maxindex = data.shape[1]

    data = reorder(data, 0, maxindex)

    np.savetxt(filename_out, data, delimiter=', ')

def reorder_test():
    """Unit test for the reorder function."""
    data = np.array([
        [1, 1, 1], [1, 1, 2], [1, 2, 1], [1, 2, 2],
        [2, 1, 1], [2, 1, 2], [2, 1, 3], [2, 2, 1], [2, 2, 2], [2, 2, 3],
        [3, 1, 1], [3, 1, 2], [3, 1, 3], [3, 2, 1], [3, 2, 2], [3, 2, 3]
        ])
    data_orig = np.copy(data)

    np.random.shuffle(data)
    # print data
    # np.savetxt('test_reorder.dat', data, delimiter=', ')

    data = reorder(data, 0, 3)
    print "reordered: ", (data == data_orig).all()

if __name__ == '__main__':
    import sys
    import os
    if len(sys.argv) < 2:
        print 'missing filename'
        exit(1)

    infile = sys.argv[1]
    basename, ext = os.path.splitext(infile)
    outfile = basename + '_ordered' + ext

    reorder_file(filename_in=infile, filename_out=outfile)
