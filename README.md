# tile-fetch
Small and simple library for getting map tiles from popular tile map services.

This library was based one of my old blog posts here: https://bcdcspatial.blogspot.com/2012/02/onlineoffline-mapping-finding-tile-urls.html

## Installation
Conda is the best way to install the library in your local conda environment
```bash
conda install -c parietal.io tile_fetch
```

If not conda, you can use the setup.py file:
```bash
git clone https://github.com/parietal-io/tile-fetch.git
cd tile-fetch
python setup.py install
```

## Basic Usage


```python
from tile_fetch import get_tile

lng = -90.283741
lat = 29.890626
level = 7
tile = get_tile(lng, lat, level)
```

```python
from tile_fetch import get_tiles_by_extent

xmin = -90.283741
ymin = 29.890626
xmax = -89.912952
ymax = 30.057766
tiles = get_tiles_by_extent(xmin, ymin, xmax, ymax)
```
