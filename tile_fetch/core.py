'''
Mostly direct port of awesome article by Joe Schwartz
http://msdn.microsoft.com/en-us/library/bb259689.aspx
'''
from __future__ import division, print_function, absolute_import

from os import path

import json
import math

try:
    import urllib.request as urlrequest
except ImportError:
    import urllib as urlrequest


EARTH_RADIUS = 6378137
MIN_LAT = -85.05112878
MAX_LAT = 85.05112878
MIN_LNG = -180
MAX_LNG = 180

templates = {}
templates['osm'] = 'https://c.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png'


# check dot file in user's home directory for templates
dot_file = path.join(path.expanduser("~"), '.tile-fetch')
if path.exists(dot_file):
    with open(dot_file) as f:
        try:
            content = f.read()
            for k, v in json.loads(f.read()).items():
                templates[k] = v
        except:
            print('WARNING: Unable to read JSON in .tile-fetch file')


def normalize_url_template(template):

    full_url = None

    if template.startswith('http'):
        full_url = template
    else:
        full_url = templates.get(template, templates['osm'])

    has_x = '{{x}}' in full_url
    has_y = '{{y}}' in full_url
    has_z = '{{z}}' in full_url
    has_q = '{{q}}' in full_url

    if not (all([has_x, has_y, has_z]) or has_q):
        raise ValueError('invalid template url: {}'.format(full_url))

    return full_url


def clip_value(value, minValue, maxValue):
    '''
    Makes sure that value is within a specific range.
    If not, then the lower or upper bounds is returned
    '''
    return min(max(value, minValue), maxValue)


def get_map_dims_by_level(zoomLevel):
    '''
    Returns the width/height in pixels of the entire map
    based on the zoom level.
    '''
    return 256 << zoomLevel


def get_ground_resolution(latitude, level):
    '''
    returns the ground resolution for based on latitude and zoom level.
    '''
    latitude = clip_value(latitude, MIN_LAT, MAX_LAT)
    mapSize = get_map_dims_by_level(level)
    res = 2 * math.pi * EARTH_RADIUS / mapSize
    return math.cos(latitude * math.pi / 180) * res


def get_map_scale(latitude, level, dpi=96):
    '''
    returns the map scale on the dpi of the screen
    '''
    dpm = dpi / 0.0254  # convert to dots per meter
    return get_ground_resolution(latitude, level) * dpm


def lat_lng_to_pixel(lat, lng, level):
    '''
    returns the x and y values of the pixel
    corresponding to a latitude and longitude.
    '''
    mapSize = get_map_dims_by_level(level)
    lat = clip_value(lat, MIN_LAT, MAX_LAT)
    lng = clip_value(lng, MIN_LNG, MAX_LNG)

    x = (lng + 180) / 360
    sinlat = math.sin(lat * math.pi / 180)
    y = 0.5 - math.log((1 + sinlat) / (1 - sinlat)) / (4 * math.pi)

    pixelX = int(clip_value(x * mapSize + 0.5, 0, mapSize - 1))
    pixelY = int(clip_value(y * mapSize + 0.5, 0, mapSize - 1))
    return (pixelX, pixelY)


def pixel_to_lng_lat(pixelX, pixelY, level):
    '''
    converts a pixel x, y to a latitude and longitude.
    '''
    mapSize = get_map_dims_by_level(level)
    x = (clip_value(pixelX, 0, mapSize - 1) / mapSize) - 0.5
    y = 0.5 - (clip_value(pixelY, 0, mapSize - 1) / mapSize)

    lat = 90 - 360 * math.atan(math.exp(-y * 2 * math.pi)) / math.pi
    lng = 360 * x

    return (lng, lat)


def pixel_to_tile(pixelX, pixelY):
    '''
    Converts pixel XY coordinates into tile
    XY coordinates of the tile containing
    '''
    return(int(pixelX / 256), int(pixelY / 256))


def tile_to_pixel(tileX, tileY):
    '''
    Converts tile XY coordinates into pixel
    XY coordinates of the upper-left pixel
    '''
    return(tileX * 256, tileY * 256)


def tile_to_quad(x, y, z):
    '''
    Computes quad_key value based on tile x, y and z values.
    '''
    quad_key = ''
    for i in range(z, 0, -1):
        digit = 0
        mask = 1 << (i - 1)
        if(x & mask) != 0:
            digit += 1
        if(y & mask) != 0:
            digit += 2
        quad_key += str(digit)
    return quad_key


def quad_to_tile(quad_key):
    '''
    Computes tile x, y and z values based on quad_key.
    '''
    tileX = 0
    tileY = 0
    tileZ = len(quad_key)

    for i in range(tileZ, 0, -1):
        mask = 1 << (i - 1)
        value = quad_key[tileZ - i]

        if value == '0':
            continue

        elif value == '1':
            tileX |= mask

        elif value == '2':
            tileY |= mask

        elif value == '3':
            tileX |= mask
            tileY |= mask

        else:
            raise Exception('Invalid QuadKey')

    return (tileX, tileY, tileZ)


def lng_lat_to_tile(lng, lat, level):
    pixelX, pixelY = lat_lng_to_pixel(lat, lng, level)
    return pixel_to_tile(pixelX, pixelY)


def get_tile_origin(tileX, tileY, level):
    '''
    Returns the upper-left hand corner lat/lng for a tile
    '''
    pixelX, pixelY = tile_to_pixel(tileX, tileY)
    lng, lat = pixel_to_lng_lat(pixelX, pixelY, level)
    return (lat, lng)


def render_template(template, x=None, y=None, z=None, q=None):
    '''
    returns new tile url based on template
    '''
    url = normalize_url_template(template)

    has_x = '{{x}}' in url
    has_y = '{{y}}' in url
    has_z = '{{z}}' in url
    has_q = '{{q}}' in url

    if all([has_x, has_y, has_z]):
        return url.replace('{{x}}', str(x)).replace('{{y}}', str(y)).replace('{{z}}', str(z))  # NOQA
    elif has_q:
        return url.replace('{{q}}', str(q))
    else:
        raise ValueError('invalid template')


def get_tile(lng, lat, level=8, template='osm'):
    '''
    get tile url based on lng, lat, level

    Parameters
    ----------
    lng: longitude or x value for POI
    lat: latitude or y value for POI
    level: zoom level (defaults to level 8)
    template: url template for output (defaults to OSM)

    Returns
    -------
    url: str or tuple(x, y, z) if template is None
    '''

    x, y = lng_lat_to_tile(lng, lat, level)

    if template:
        return render_template(template, x, y, level)
    else:
        return (x, y, level)


def save_tile(output_path='.', **tile_kwargs):
    '''
    save a tile to disk based on lng, lat, level, etc.

    Parameters
    ----------
    output_path: path indicating where tile should be written
    tile_kwargs: dictionary of tile args (see get_tile)

    Returns
    -------
    output_path: echo of input path
    '''
    tile_url = get_tile(**tile_kwargs)
    urlrequest.urlretrieve(tile_url, output_path)
    return output_path


def get_tiles_by_extent(xmin, ymin, xmax, ymax, level=8, template='osm'):
    '''
    Returns a list of tile urls by extent
    '''

    # upper-left tile
    txmin, tymin = lng_lat_to_tile(xmin, ymax, level)

    # lower-right tile
    txmax, tymax = lng_lat_to_tile(xmax, ymin, level)

    for y in range(tymax, tymin - 1, -1):
        for x in range(txmin, txmax + 1, 1):
            yield render_template(template, x, y, level)
