#! /usr/bin/env python2

import json

config = {
    u'grid_nx': 20,
    u'grid_ny': 15,
    u'grid_nz': 10,

    u'grid_origin': [0.0, 0.0, 0.0],
    u'grid_length': [5.0, 3.0, 1.0],

    u'filename': 'test.dat',
    u'vtk_width': 800,
    u'vtk_height': 800
}

if __name__ == '__main__':
    print 'config:  ', repr(config)
    config_string = json.dumps(config, sort_keys=True, indent=2)
    print 'json:    ', config_string
    decoded = json.loads(config_string)
    print 'decoded: ', decoded
