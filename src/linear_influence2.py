# linear_influence.py: influence mapping algorithms, using bfs linear diffusion
#
# AI bot written for AI Challenge 2011 - Ants
# Author: Bill Y
# License: all your base are belong to us

import path
import numpy as np
from collections import deque
from core import ALL_DIRECTIONS, perf_logger
from cython_ext2 import merge_linear_map2 as merge_linear_map

class LinearInfluence():
    def __init__(self, gamestate):
        self.gamestate = gamestate
        self.map = np.zeros((self.gamestate.rows, self.gamestate.cols))
        
    def set_influence(self, influence_sources, abort_condition):
        perf_logger.debug('set_influence.start: %s' % str(self.gamestate.time_elapsed()))
        self.map = np.zeros((self.gamestate.rows, self.gamestate.cols))
        if len(influence_sources) == 0:
            return
        temp_maps = []
        for initial_loc, initial_value in influence_sources:
            temp_maps.append(self.get_map_for_single_loc(initial_loc, initial_value, abort_condition))        
        np_temp_maps = np.array(temp_maps)
        perf_logger.debug('set_influence.merge start: %s' % str(self.gamestate.time_elapsed()))
        perf_logger.debug('np_temp_maps.shape = %s' % str(np_temp_maps.shape))
        merge_linear_map(np_temp_maps, self.map)
        perf_logger.debug('set_influence.finish: %s' % str(self.gamestate.time_elapsed()))
        
    def get_map_for_single_loc(self, initial_loc, initial_value, abort_condition):
        'add point at initial_loc with initial_value (which also determines how far does it go'
        'abort_condition is a function reference taking location and check if is good to abort'
        modifier = 0
        if initial_value > 0:
            modifier = -1
        elif initial_value < 0:
            modifier = 1
            
        # create temporary map, add point
        temp_map = np.zeros((self.gamestate.rows, self.gamestate.cols), dtype=np.int)
        temp_map[initial_loc] = initial_value
        # diffuse
        self.bfs_linear_diffuse(initial_loc, temp_map, modifier, abort_condition)
        
        return temp_map
        
        
    def bfs_linear_diffuse(self, start_loc, temp_map, modifier, abort_condition):
        # http://en.wikipedia.org/wiki/Breadth-first_search#Pseudocode
        # create a queue Q
        list_q = deque()
        # enqueue (source, level) onto Q
        list_q.append(start_loc)
        # mark source, which has its value being its parent, for traversing purpose
        marked_dict = {start_loc:None}
        
        while len(list_q) > 0:
            # dequeue an item from Q into v
            v = list_q.popleft()
            # stop diffusion reaching 0
            if temp_map[v] == 0:
                continue
            # for each edge e incident on v in Graph:
            for e in ALL_DIRECTIONS:
                # let w be the other end of e
                w = self.gamestate.destination(v, e)
                # if w is not marked
                if not w in marked_dict:
                    # w must not be water
                    if w not in self.gamestate.water_list :
                        # set influence
                        temp_map[w] = temp_map[v] + modifier
                        # mark w
                        marked_dict[w] = v
                        # enqueue w onto Q
                        list_q.append(w) 
                        # check if we meet abort condition 
                        if abort_condition is not None and abort_condition(w):
                            return
