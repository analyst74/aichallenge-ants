# path.py: pathfinding algorithms
#
# AI bot written for AI Challenge 2011 - Ants
# Author: Bill Y
# License: all your base are belong to us

from core import *
from collections import defaultdict, deque

def bfs_findtask(gamestate, influence, start_loc, counter_limit):
    'find lowest influence location from start_loc, return the path'
    #debug_logger.debug('bfs.start for %s' % str(start_locs))
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
                    # check if we find a lower influence spot
                    if influence.map[w] < lowest_inf:
                        lowest_inf = influence.map[w]
                        lowest_loc = w

    result = [lowest_loc]
    trace_back_loc = lowest_loc
    while marked_dict[trace_back_loc] is not None:
        trace_back_loc = marked_dict[trace_back_loc]
        result.append(trace_back_loc)
        
    return result
    
def bfs_findenemy(gamestate, start_loc, distance_limit):
    'from start_loc, find enemy ant within distance_limit'
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
        # for each edge e incident on v in Graph:
        for e in ALL_DIRECTIONS:
            # let w be the other end of e
            w = gamestate.destination(v, e)
            # if w is not marked
            if not w in marked_dict:
                # w must not be water and within distance limit
                if w not in gamestate.water_list and gamestate.euclidean_distance2(start_loc, w) <= distance_limit:
                    # mark w
                    marked_dict[w] = v
                    # enqueue w onto Q
                    list_q.append(w) 
                    # check if we find a lower influence spot
                    if w in gamestate.ant_list and gamestate.ant_list[w][0] != MY_ANT:
                        return True
                        
    return False
        
def astar(gamestate, start, goal, length_limit):
    'a star limit by given depth'
    #en.wikipedia.org/wiki/A*_search_algorithm
        
    def reconstrct_path(came_from, current_node):
        if current_node in came_from:
            p = reconstrct_path(came_from, came_from[current_node])
            return p + [current_node]
        else:
            return [current_node]

    openset = []
    closedset = []
    came_from = {}
    
    # cost from start to best known path
    g_score = {start: 0} 
    h_score = {start: gamestate.manhattan_distance(start, goal)}
    # estimated total
    f_score = {start: g_score[start] + h_score[start]} 
    
    openset.append(start)
    while len(openset) > 0:
        #debug_logger.debug('openset = %s' % str(openset))
        current = min(openset, key=lambda loc:f_score[loc])
        # stop when we reached goal or the path length limit
        #debug_logger.debug('current = %s' % str(current))
        #debug_logger.debug('goal = %s' % str(goal))
        if current == goal:
            return reconstrct_path(came_from, goal)
        elif g_score[current] > length_limit:
            return reconstrct_path(came_from, current)
        
        openset.remove(current)
        closedset.append(current)
        for neighbour in [n_loc for n_loc in gamestate.neighbour_table[current] 
                        if n_loc not in gamestate.water_list]:
            if neighbour in closedset:
                continue
            tentative_g_score = g_score[current] + 1
            
            if neighbour not in openset:
                openset.append(neighbour)
                tentative_is_better = True
            elif tentative_g_score < g_score[neighbour]:
                tentative_is_better = True
            else:
                tentative_is_better = False
                
            if tentative_is_better:
                came_from[neighbour] = current
                g_score[neighbour] = tentative_g_score
                h_score[neighbour] = gamestate.manhattan_distance(neighbour, goal)
                f_score[neighbour] = g_score[neighbour] + h_score[neighbour]
                
    return None
