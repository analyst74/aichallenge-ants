#!/usr/bin/env python

from collections import deque

class PathFinder():

    def __init__(self):
        pass
        
    # http://en.wikipedia.org/wiki/Breadth-first_search#Pseudocode
    def direction_breadth_first(self, ants, source, dest):
        # create a queue Q
        # enqueue (source, level) onto Q
        list_q = deque((source, 0))
        # mark source
        marked_dict = {source}
                
        while len(list_q) > 0:
            # dequeue an item from Q into v
            (loc, level) = list_q.popleft()
            # for each edge e incident on v in Graph:
            for direction in ['n', 'e', 's', 'w']:
                # let w be the other end of e
                # if w is not marked:
                    # mark w
                    # enqueue w onto Q
        