# influence.py: influence mapping algorithms
#
# AI bot written for AI Challenge 2011 - Ants
# Author: Bill Y
# License: all your base are belong to us

from core import WATER
import math, path

class Influence():
    def __init__(self, gamestate):
        self.gamestate = gamestate
        self.map = {(row, col): 0.0 for col in xrange(self.gamestate.cols) 
                    for row in xrange(self.gamestate.rows)}
    
    def diffuse(self, cutoff=0.01):
        'diffuse self.map'
        # initiate buffer
        buffer = {}
        for key in self.map:
            buffer[key] = self.map[key]
            
        # for each item in self.map that is not water
        non_water_locs = [loc for loc in self.map if loc not in self.gamestate.water_list and math.fabs(self.map[loc]) > cutoff]
        # find surrounding non-water nodes and diffuse to them
        for cur_loc in non_water_locs:
            neighbours = [loc for loc in self.gamestate.neighbour_table[cur_loc]
                        if loc not in self.gamestate.water_list]
            # * 0.125 is three times faster than / 8.0
            neighbour_val = self.map[cur_loc] * 0.125
            cur_val = -neighbour_val * len(neighbours)
            # add node/value to buffer
            buffer[cur_loc] += cur_val
            for n_loc in neighbours:
                buffer[n_loc] += neighbour_val
        # copy buffer to map
        self.map = buffer
    
    def set_value(self, loc, range, value):
        'set value on given loc, with its influence reaching up to range'
        # a simple/different model for diffusion is used
        self.map[loc] += value
        all_neighbours = path.bfs(self.gamestate, [loc], range**2, lambda x : True)
        for n_loc in all_neighbours:
            self.map[n_loc] += value / self.gamestate.manhattan_distance(loc, n_loc)
        
    def decay(self, decay_multiplier):
        'decay self.map'
        self.map = {key:val * decay_multiplier for key,val in self.map.items()}