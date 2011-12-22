# influence.py: influence mapping algorithms
#
# AI bot written for AI Challenge 2011 - Ants
# Author: Bill Y
# License: all your base are belong to us

from core import WATER, CUTOFF
from cython_ext2 import gaussian_blur
import math, path, numpy

class Influence():
    def __init__(self, gamestate):
        self.gamestate = gamestate
        self.map = numpy.zeros((self.gamestate.rows, self.gamestate.cols)) 
    
    def diffuse(self):
        self.map = gaussian_blur(self.map, self.gamestate.map)
        
    def decay(self, rate):
        self.map = self.map * rate