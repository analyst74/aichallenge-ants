# influence.py: influence mapping algorithms
#
# AI bot written for AI Challenge 2011 - Ants
# Author: Bill Y
# License: all your base are belong to us

from core import WATER, CUTOFF
from cython_ext2 import diffuse_once
import math, path, numpy

class Influence():
    def __init__(self, gamestate):
        self.gamestate = gamestate
        self.map = numpy.zeros((self.gamestate.rows, self.gamestate.cols)) 
    
    def diffuse(self):
        #print ('%s' % str(self.gamestate.water_list))
        self.map = diffuse_once(self.map, self.gamestate.map, CUTOFF)
        
    def decay(self, rate):
        self.map = self.map * rate