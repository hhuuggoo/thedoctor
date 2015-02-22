# needs to be tested
from __future__ import print_function
import sys
if len(sys.argv)>1 and sys.argv[1] == 'develop':
    import site
    if not hasattr(site, 'getsitepackages'):
        import setuptools
    else:
        from os.path import dirname, abspath, join
        site_packages = site.getsitepackages()[0]
        fname = join(site_packages, "thedoctor.pth")
        path = abspath(dirname(__file__))
        with open(fname, "w+") as f:
            f.write(path)
        print("develop mode, wrote path (%s) to (%s)" % (path, fname))
        sys.exit()
from distutils.core import setup
import os
import sys
__version__ = (0, 2)
setup(
    name = 'thedoctor',
    version = '.'.join([str(x) for x in __version__]),
    packages = ['thedoctor',
                'thedoctor.tests',
                ],

    url = 'http://github.com/hhuuggoo/thedoctor',
    description = 'thedoctor',
    zip_safe=False,
    author='Hugo Shi',
    author_email='hugo.r.shi@gmail.com',
    license = 'New BSD',
)
