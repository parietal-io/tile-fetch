from __future__ import print_function, absolute_import

from tile_fetch.core import get_tile  # NOQA
from tile_fetch.core import get_tiles_by_extent  # NOQA

from ._version import get_versions
__version__ = get_versions()['version']
