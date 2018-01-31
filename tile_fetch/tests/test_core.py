from tile_fetch import get_tile
from tile_fetch import get_tiles_by_extent


TEMPLATE = ('http://services.arcgisonline.com'
            '/ArcGIS/rest/services/'
            'World_Topo_Map/MapServer/tile'
            '/{{z}}/{{y}}/{{x}}.png')


def test_get_tile():
    lng = -90.283741
    lat = 29.890626
    level = 7
    tile = get_tile(lng, lat, level, template=TEMPLATE)
    assert isinstance(tile, str)


def test_get_tiles_by_extent():
    xmin = -90.283741
    ymin = 29.890626
    xmax = -89.912952
    ymax = 30.057766
    level = 11
    tiles = get_tiles_by_extent(xmin, ymin, xmax,
                                ymax, level, template=TEMPLATE)
    assert len(list(tiles)) == 6
