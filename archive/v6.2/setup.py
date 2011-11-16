# setup.py: setup script for submission
#
# AI bot written for AI Challenge 2011 - Ants
# Author: Bill Y
# License: all your base are belong to us

from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext
import numpy as np

ext_modules = [Extension("cython_ext2", ["cython_ext2.pyx"], include_dirs=[np.get_include()])]

setup(
    name = 'Cython extension functions',
    cmdclass ={'build_ext': build_ext},
    ext_modules = ext_modules
)