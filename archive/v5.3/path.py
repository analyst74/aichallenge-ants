# path.py: pathfinding algorithms
#
# AI bot written for AI Challenge 2011 - Ants
# Author: Bill Y
# License: all your base are belong to us

from core import *


def bfs_findtask(gamestate, influence, start_loc, counter_limit):
    'finds list of locations meeting func_condition, and within func_limit'
    #logging.debug('bfs.start for %s' % str(start_locs))
    # http://en.wikipedia.org/wiki/Breadth-first_search#Pseudocode
    lowest_inf = influence.map[start_loc]
    lowest_loc = start_loc
    # create a queue Q
    list_q = deque()
    # enqueue (source, level) onto Q
    list_q.append(start_loc)
    # mark source, which has its value being its parent, for traversing purpose
    marked_dict = {start_loc:None}
    
    counter = 0
    while len(list_q) > 0 and counter < counter_limit:
        counter += 1
        # dequeue an item from Q into v
        v = list_q.popleft()
        # for each edge e incident on v in Graph:
        for e in ALL_DIRECTIONS:
            # let w be the other end of e
            w = gamestate.destination(v, e)
            # if w is not marked
            if not w in marked_dict:
                # w must not be water
                if w not in gamestate.water_list :
                    # mark w
                    marked_dict[w] = v
                    # enqueue w onto Q
                    list_q.append(w) 
                    # check if we find friendly or enemy ant
                    if influence.map[w] < lowest_inf:
                        lowest_inf = influence.map[w]
                        lowest_loc = w

    result = [lowest_loc]
    trace_back_loc = lowest_loc
    while marked_dict[trace_back_loc] is not None:
        trace_back_loc = marked_dict[trace_back_loc]
        result.append(trace_back_loc)
        
    return result
