import os
from os import path
from tile_fetch import get_tile
from tile_fetch import get_tiles_by_extent
from tile_fetch import save_tile


TEMPLATE = ('http://services.arcgisonline.com'
            '/ArcGIS/rest/services/'
            'World_Topo_Map/MapServer/tile'
            '/{{z}}/{{y}}/{{x}}.png')

here = path.abspath(path.join(path.dirname(__file__)))


def test_get_tile():
    lng = -90.283741
    lat = 29.890626
    level = 7
    tile = get_tile(lng, lat, level, template=TEMPLATE)
    print(tile)
    assert isinstance(tile, str)


def test_save_tile():
    output_path = path.join(here, 'test_save_tile.png')
    lng = -90.283741
    lat = 29.890626
    tile = None
    try:
        tile = save_tile(output_path, lng=lng, lat=lat)
        assert isinstance(tile, str)
        assert path.exists(tile)
    finally:
        if tile and path.exists(tile):
            os.remove(tile)


def test_get_tiles_by_extent():
    xmin = -90.283741
    ymin = 29.890626
    xmax = -89.912952
    ymax = 30.057766
    level = 11
    tiles = get_tiles_by_extent(xmin, ymin, xmax,
                                ymax, level, template=TEMPLATE)
    tile_list = list(tiles)
    print(tile_list)
    assert len(tile_list) == 6
