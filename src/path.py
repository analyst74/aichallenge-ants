# path.py: pathfinding algorithms
#
# AI bot written for AI Challenge 2011 - Ants
# Author: Bill
# License: all your base are belong to us

from core import *

def bfs(gamestate, start_locs, range_limit, func_condition):
    'finds list of locations meeting func_condition, and within func_limit'
    #logging.debug('bfs.start for %s' % str(start_locs))
    # http://en.wikipedia.org/wiki/Breadth-first_search#Pseudocode
    result = []
    # create a queue Q
    list_q = deque()
    # enqueue (source, level) onto Q
    list_q.extend(start_locs)
    # mark source, which has its value being its parent, for traversing purpose
    marked_dict = {}
    for loc in start_locs:
        marked_dict[loc] = None

    while len(list_q) > 0:
        # dequeue an item from Q into v
        v = list_q.popleft()
        # for each edge e incident on v in Graph:
        for e in ALL_DIRECTIONS:
            # let w be the other end of e
            w = gamestate.destination(v, e)
            # if w is not marked
            if not w in marked_dict:
                # w must not be water and 
                (w_row, w_col) = w  
                distance = min([gamestate.euclidean_distance2(loc, w) for loc in start_locs])
                if (gamestate.map[w_row][w_col] != WATER and 
                    distance <= range_limit) :
                    # mark w
                    marked_dict[w] = v
                    # enqueue w onto Q
                    list_q.append(w) 
                    # check if we find friendly or enemy ant
                    if func_condition(w):
                        result.append(w)

    #logging.debug('bfs found result %s ' % str(result))
    return result
