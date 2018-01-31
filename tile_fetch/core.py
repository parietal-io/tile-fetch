'''
Mostly direct port of awesome article by Joe Schwartz
http://msdn.microsoft.com/en-us/library/bb259689.aspx
'''
from __future__ import division
import math


EARTH_RADIUS = 6378137
MIN_LAT = -85.05112878
MAX_LAT = 85.05112878
MIN_LNG = -180
MAX_LNG = 180


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
    return math.cos(latitude * math.pi / 180) * 2 * math.pi * EARTH_RADIUS / mapSize


def get_map_scale(latitude, level, dpi=96):
    '''
    returns the map scale on the dpi of the screen
    '''
    dpm = dpi / 0.0254  # convert to dots per meter
    return get_ground_resolution(latitude, level) * dpm


def lat_lng_to_pixel(lat, lng, level):
    '''
    returns the x and y values of the pixel corresponding to a latitude and longitude.
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
    Converts pixel XY coordinates into tile XY coordinates of the tile containing
    '''
    return(int(pixelX / 256), int(pixelY / 256))


def tile_to_pixel(tileX, tileY):
    '''
    Converts tile XY coordinates into pixel XY coordinates of the upper-left pixel
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


def quad_to_tile(self, quad_key):
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


def render_template(template, x, y, z):
    '''
    returns new tile url based on template
    '''
    return template.replace('{{x}}', str(x)).replace('{{y}}', str(y)).replace('{{z}}', str(z))


def get_tile(lng, lat, level=8,
             template='https://c.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png'):
    x, y = lng_lat_to_tile(xmin, ymax, level)
    return render_template(template, x, y, level)


def get_tiles_by_extent(xmin, ymin, xmax, ymax, level=8,
                        template='https://c.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png'):
    '''
    Returns a list of tile urls by extent
    '''
    # upper-left tile
    txmin, tymin = lng_lat_to_tile(xmin, ymax, level)

    # lower-right tile
    tmax, tymax = lng_lat_to_tile(xmax, ymin, level)

    for y in range(tymax, tymin - 1, -1):
        for x in range(txmin, txmax + 1, 1):
            yield render_template(template, x, y, level)
