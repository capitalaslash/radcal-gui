#! /usr/bin/env python2

import math
import urllib
import requests
import json
import vtk

################################################################################
# user input

# center point
SEARCH_STRING = 'via Martiri di Monte Sole 4, Bologna'

# extension in meters (along parallel and along meridian)
SIZE = [5000, 6500]

################################################################################

# zoom
# Level	 Degree	 Area	         m / pixel    ~Scale
# 0	     360	 whole world	 156,412	  1:500 million
# 1	     180		              78,206	  1:250 million
# 2	     90		                  39,103	  1:150 million
# 3	     45		                  19,551	  1:70 million
# 4	     22.5	                   9,776	  1:35 million
# 5	     11.25	                   4,888	  1:15 million
# 6	     5.625	                   2,444	  1:10 million
# 7	     2.813	                   1,222	  1:4 million
# 8	     1.406	                     610.984  1:2 million
# 9	     0.703	wide area	         305.492  1:1 million
# 10	 0.352		                 152.746  1:500,000
# 11	 0.176	area	              76.373  1:250,000
# 12	 0.088		                  38.187  1:150,000
# 13	 0.044	village or town	      19.093  1:70,000
# 14	 0.022		                   9.547  1:35,000
# 15	 0.011		                   4.773  1:15,000
# 16	 0.005	small road	           2.387  1:8,000
# 17	 0.003		                   1.193  1:4,000
# 18	 0.001		                   0.596  1:2,000
# 19	 0.0005		                   0.298  1:1,000

# distance represented by one pixel
# S = C*cos(y)/2^(z+8)
# C = equatorial circumference (40,075.16 km)
# z = zoom Level
# y = latitude

# equatorial circumference in meters
EQ_CIRC = 40075016.686

# default zoom level (must be below 19)
DEFAULT_ZOOM = 18

# TODO
def convert_minsec(input_str):
    """
    convert lat/lon string to numerical value
    """
    import re
    regex = re.compile(r"""(\d{2}) # match degrees
                           \D*     # match separator
                           (\d{2}) # match minutes
                           \D*     # match separator
                           (\d{2}) # match seconds
    """, re.VERBOSE)
    value_str = re.search(regex, input_str).groups()
    value = float(value_str[0])
    value += float(value_str[1])/60.
    value += float(value_str[2])/3600.
    return value


def retrieve_map(**kwargs):
    """
    download a map based on the coordinates and size given as input
    """
    center = kwargs['center']
    zoom = kwargs['zoom']
    size = kwargs['size']
    output_map = kwargs['output_map']
    url = 'http://staticmap.openstreetmap.de/staticmap.php' + \
          '?center=' + str(center[0]) + ',' + str(center[1]) + \
          '&zoom=' + str(zoom) + \
          '&size=' + str(size[0]) + 'x' + str(size[1]) + \
          '&maptype=mapnik'
    urllib.urlretrieve(url, output_map)

def get_coords(place):
    """
    convert address to lat/lon coordinates
    """
    url = 'http://nominatim.openstreetmap.org/search/' + place + '?format=json'
    r = requests.get(url)
    data = json.loads(r.text)
    return [data[0]['lat'], data[0]['lon']]

def create_textured_plane(**kwargs):
    """
    create a plane with correct size and texture it with a map
    """
    image_reader = vtk.vtkPNGReader()
    image_reader.SetFileName(kwargs['map'])

    plane = vtk.vtkPlaneSource()
    size = kwargs['size']
    z_level = 0.0
    plane.SetOrigin(-0.5*size[0], -0.5*size[1], z_level)
    plane.SetPoint1(+0.5*size[0], -0.5*size[1], z_level)
    plane.SetPoint2(-0.5*size[0], +0.5*size[1], z_level)

    texture = vtk.vtkTexture()
    texture.SetInputConnection(image_reader.GetOutputPort())

    texture_plane = vtk.vtkTextureMapToPlane()
    texture_plane.SetInputConnection(plane.GetOutputPort())
    return texture_plane, texture

def visualize(texture_plane, texture):
    """
    visualize the textured plane
    """
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(texture_plane.GetOutputPort())

    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    actor.SetTexture(texture)

    renderer = vtk.vtkRenderer()
    renderer.AddActor(actor)

    render_win = vtk.vtkRenderWindow()
    render_win.AddRenderer(renderer)

    interactor = vtk.vtkRenderWindowInteractor()
    interactor.SetRenderWindow(render_win)

    render_win.Render()
    interactor.Start()

def set_resolution(**kwargs):
    """
    compute resolution and zoom based on map size and location
    """
    coords = kwargs['coords']
    size = kwargs['size']
    # compute resolution based on default zoom level
    pixels = []
    zoom = DEFAULT_ZOOM
    for dir in SIZE:
        pixels.append(int(dir * 256 * 2**(zoom) /
                        (EQ_CIRC * math.cos(math.radians(float(coords[0]))))))
    print "initial map size:", pixels

    # keep max resolution on a side between 512 and 1024 pixels changing zoom
    # 1024 is the maximum allowed resolution for a single picture
    ok = False
    while not ok:
        if pixels[0] < 512 and pixels[1] < 512:
            pixels[0] *= 2
            pixels[1] *= 2
            zoom += 1
        elif pixels[0] > 1024 or pixels[1] > 1024:
            pixels[0] /= 2
            pixels[1] /= 2
            zoom -= 1
        else:
            ok = True
        # 19 is the maximum allowed zoom
        if zoom == 19:
            ok = True
    print "final map size:", pixels, "zoom:", zoom
    return pixels, zoom

if __name__ == '__main__':
    """
    testsuite
    """

    coords = get_coords(SEARCH_STRING)
    pixels, zoom = set_resolution(coords=coords, size=SIZE)
    output_map = '.map.png'

    retrieve_map(center=coords,
                 zoom=zoom,
                 size=pixels,
                 output_map = output_map)

    texture_plane, texture = \
        create_textured_plane(map=output_map,
                              size=SIZE)
    visualize(texture_plane, texture)
