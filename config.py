#! /usr/bin/env python2

import json

config = {
    u'grid_nx': 4,
    u'grid_ny': 3,
    u'grid_nz': 2,

    u'grid_origin': [0.0, 0.0, 0.0],
    u'grid_length': [1.0, 1.0, 1.0]
}

if __name__ == '__main__':
    print 'config:  ', repr(config)
    config_string = json.dumps(config, sort_keys=True, indent=2)
    print 'json:    ', config_string
    decoded = json.loads(config_string)
    print 'decoded: ', decoded
