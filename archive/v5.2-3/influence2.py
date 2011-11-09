# influence.py: influence mapping algorithms
#
# AI bot written for AI Challenge 2011 - Ants
# Author: Bill Y
# License: all your base are belong to us

from core import WATER
import math, path, numpy

class Influence():
    def __init__(self, gamestate, decay_multiplier):
        self.gamestate = gamestate
        self.decay_multiplier = decay_multiplier
        self.map = numpy.zeros((self.gamestate.rows, self.gamestate.cols))
        self.non_water_locs = [(row, col) for col in xrange(self.gamestate.cols) 
                    for row in xrange(self.gamestate.rows)]
    
    def diffuse(self):
        'diffuse self.map'
        # initiate buffer
        buffer = numpy.copy(self.map)
        #for key in self.map:
        #    buffer[key] = self.map[key]
            
        # for each item in self.map that is not water
        self.non_water_locs = [loc for loc in self.non_water_locs if loc not in self.gamestate.water_list]
        # find surrounding non-water nodes and diffuse to them
        for cur_loc in self.non_water_locs:
            neighbours = [loc for loc in self.gamestate.neighbour_table[cur_loc]
                        if loc not in self.gamestate.water_list]
            # new value = cur value - value goes to neighbours + value come from neighbours
            neighbour_vals = sum([self.map[loc] / 8.0 for loc in neighbours])
            cur_val = buffer[cur_loc] - self.map[cur_loc] / 8.0 * len(neighbours) + neighbour_vals
            # add node/value to buffer
            buffer[cur_loc] = cur_val
        # copy buffer to map
        self.map = buffer
    
    def set_value(self, loc, range, value):
        'set value on given loc, with its influence reaching up to range'
        # a simple/different model for diffusion is used
        self.map[loc] = value
        all_neighbours = path.bfs(self.gamestate, [loc], range**2, lambda x : True)
        for n_loc in all_neighbours:
            self.map[n_loc] = value / self.gamestate.manhattan_distance(loc, n_loc)
        
    def decay(self):
        'decay self.map'
        for key in self.map:
            self.map[key] = self.map[key] * self.decay_multiplier
            # cut off, should this be in decay instead?
            if math.fabs(self.map[key]) < 0.0001:
                self.map[key] = 0 