from setuptools import find_packages, setup

import versioneer

setup(name='tile-fetch',
      version=versioneer.get_version(),
      cmdclass=versioneer.get_cmdclass(),
      description='Simple Map Tile URL Generator / Fetcher',
      url='http://github.com/parietal-io/tile-fetch',
      packages=find_packages(),
      zip_safe=False,
      include_package_data=True)
