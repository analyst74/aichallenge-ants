# influence.py: influence mapping algorithms
#
# AI bot written for AI Challenge 2011 - Ants
# Author: Bill Y
# License: all your base are belong to us

from core import WATER
from cython_ext import diffuse_once, diffuse_n
import math, path, numpy

class Influence():
    def __init__(self, gamestate):
        self.gamestate = gamestate
        self.map = numpy.zeros((self.gamestate.rows, self.gamestate.cols)) 
    
    def diffuse(self):
        #print ('%s' % str(self.gamestate.water_list))
        self.map = diffuse_once(self.map, self.gamestate.map)
    
    def set_values(self, loc, value, level):
        'set value on given loc, with its influence reaching up to range'
        all_neighbours = [loc for loc in self.gamestate.neighbour_table[loc] 
                        if loc not in self.gamestate.water_list]
        self.map[loc] += value - 0.125 * len(all_neighbours)
        if level > 0:
            for n_loc in all_neighbours:
                self.set_value(self.map[n_loc], value * 0.125, level-1)
        
    def decay(self, decay_multiplier):
        'decay self.map'
        self.map = self.map * decay_multiplier