# influence.py: influence mapping algorithms
#
# AI bot written for AI Challenge 2011 - Ants
# Author: Bill Y
# License: all your base are belong to us

from core import WATER
import math

class Influence():
    def __init__(self, gamestate, decay_multiplier):
        self.gamestate = gamestate
        self.decay_multiplier = decay_multiplier
        self.map = {(row, col): 0.0 for col in xrange(self.gamestate.cols) 
                    for row in xrange(self.gamestate.rows)}
    
    def diffuse(self):
        'diffuse self.map'
        # initiate buffer
        buffer = {(row, col): 0 for col in xrange(self.gamestate.cols) 
                for row in xrange(self.gamestate.rows)}
        # for each item in self.map that is not water
        non_water_locs = [loc for loc in self.map if not self.gamestate.is_water(loc)]
        # find surrounding non-water nodes and diffuse to them
        for cur_loc in non_water_locs:
            neighbours = [loc for loc in self.gamestate.get_neighbour_locs(cur_loc) 
                        if not self.gamestate.is_water(loc)]
            neighbour_val = self.map[cur_loc] / 8.0
            cur_val = -neighbour_val * len(neighbours)
            # add node/value to buffer
            buffer[cur_loc] += cur_val
            for n_loc in neighbours:
                buffer[n_loc] += neighbour_val
        # merge buffer to map
        for key in buffer:
            self.map[key] += buffer[key]
        
    def decay(self):
        'decay self.map'
        for key in self.map:
            self.map[key] = self.map[key] * self.decay_multiplier
            # cut off, should this be in decay instead?
            if math.fabs(self.map[key]) < 0.0001:
                self.map[key] = 0 