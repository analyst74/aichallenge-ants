# battle_influence.py: combat algorithm utilizing influence map
#
# AI bot written for AI Challenge 2011 - Ants
# Author: Bill Y
# License: all your base are belong to us

from core import *
from collections import deque
import numpy as np

def do_combat(gamestate):
    'perform combat action'
    # values used in multiple places
    threat_distance = gamestate.attackradius2 #gamestate.euclidean_distance_add(gamestate.attackradius2, 1)
    
    # get all my combat ants and enemy ants
    combat_distance = gamestate.euclidean_distance_add(gamestate.attackradius2, 2)
    enemy_ants = gamestate.enemy_ants()
    my_ants = sorted(bfs_find_my_combat_ants(gamestate, enemy_ants, combat_distance))

    # set up influence 
    influence_by_threat = get_influence_by_threat(gamestate, my_ants, enemy_ants, threat_distance)
    
    combat_scores = get_combat_scores(gamestate, my_ants, enemy_ants, influence_by_threat, threat_distance)
    
    # loop through all ants, move them toward highest strategy point
    # move order start from front line (highest threat)
    move_orders = []
    occupied_spots = []
    my_ants_by_threat_level = sorted([(influence_by_threat[MY_ANT][ant], ant) for ant in my_ants], reverse=True)
    for threat, ant in my_ants_by_threat_level:
        all_moves = [move for move in gamestate.passable_moves(ant)]
        all_moves_by_score = sorted([(combat_scores[move], move) for move in all_moves], reverse=True)
        debug_logger.debug('do_combat for %s' % str(ant))
        debug_logger.debug('all_move_by_score = %s' % str(all_moves_by_score))
        # only move if there is a beneficial move
        if all_moves_by_score[0][0] >= 1:
            gamestate.issue_order_by_location(ant, all_moves_by_score[0][1])
    
def bfs_find_my_combat_ants(gamestate, enemy_ants, distance_limit):
    'find all my ants within certain distance of enemy ants'
    enemy_locations = [loc for loc, owner in enemy_ants]
    list_q = deque(enemy_locations)
    # mark source, each node knows its root, to calculate distance
    marked_dict = {ant:ant for ant in enemy_locations}
    
    my_combat_ants = []
    
    while len(list_q) > 0:
        # dequeue an item from Q into v
        v = list_q.popleft()
        # for each edge e incident on v in Graph:
        for w in gamestate.neighbour_table[v]:
            # if w is not marked
            if w not in marked_dict and \
                w not in gamestate.water_list and \
                gamestate.euclidean_distance2(w, marked_dict[v]) < distance_limit:
                # mark w with its appropriate level
                marked_dict[w] = marked_dict[v]
                # enqueue w onto Q
                list_q.append(w) 
                # check if we find a lower influence spot
                if w in gamestate.ant_list and gamestate.ant_list[w][0] == MY_ANT:
                    my_combat_ants.append(w)
                        
    return my_combat_ants
    
def bfs_set_influence(gamestate, map, start_locs, distance_limit):
    'additively set influence + 1 within distance_limit of start_loc'
    list_q = deque(start_locs)
    # mark source, each node knows its root, to calculate distance
    marked_dict = {loc:loc for loc in start_locs}
    
    while len(list_q) > 0:
        # dequeue an item from Q into v
        v = list_q.popleft()
        map[v] += 1
        # for each edge e incident on v in Graph:
        for w in gamestate.neighbour_table[v]:
            # if w is not marked
            if w not in marked_dict and \
                w not in gamestate.water_list and \
                gamestate.euclidean_distance2(w, marked_dict[v]) <= distance_limit:
                # mark w with its appropriate level
                marked_dict[w] = marked_dict[v]
                # enqueue w onto Q
                list_q.append(w)

def get_influence_by_owner(gamestate, my_ants, enemy_ants, threat_distance):    
    influence_by_owner = {MY_ANT:np.zeros((gamestate.rows, gamestate.cols), dtype=np.int)}
    for ant in my_ants:
        all_moves = gamestate.passable_moves(ant)
        bfs_set_influence(gamestate, influence_by_owner[MY_ANT], all_moves, threat_distance)
    for ant, owner in enemy_ants:
        if owner not in influence_by_owner:
            influence_by_owner[owner] = np.zeros((gamestate.rows, gamestate.cols), dtype=np.int)
        all_moves = gamestate.passable_moves(ant)
        bfs_set_influence(gamestate, influence_by_owner[owner], all_moves, threat_distance)
        
    return influence_by_owner

def get_influence_by_threat(gamestate, my_ants, enemy_ants, threat_distance):
    influence_by_owner = get_influence_by_owner(gamestate, my_ants, enemy_ants, threat_distance)
    
    # for each ant and their surrounding locations figure out how many enemies is it fighting
    influence_by_threat = {owner:np.zeros((gamestate.rows, gamestate.cols), dtype=np.int) for owner in influence_by_owner}
    for ant in my_ants:
        for loc in [ant] + gamestate.neighbour_table[ant]:
            influence_by_threat[MY_ANT][loc] = sum([i[loc] for o, i in influence_by_owner.items() if o != MY_ANT])
            
    for ant, owner in enemy_ants:
        for loc in [ant] + gamestate.neighbour_table[ant]:
            influence_by_threat[owner][loc] = sum([i[loc] for o, i in influence_by_owner.items() if o != owner])

    return influence_by_threat
    
def get_combat_scores(gamestate, my_ants, enemy_ants, influence_by_threat, threat_distance):
    # loop through all our ants and their surrounding locations, figure out it's strategy points
    # by comparing each location's threat level and all its surrounding enemy's threat level
    # combat score = enemy ant it can kill / enemy ant it cannot kill
    
    combat_scores = {}
    for ant in my_ants:
        for loc in [ant] + gamestate.neighbour_table[ant]:
            threat = influence_by_threat[MY_ANT][loc]
            # no threat, neutral value
            if threat == 0:
                combat_scores[loc] = 0.99
            # at least 1 enemy in range
            else:
                enemies_in_range = [(enemy, owner) for enemy, owner in enemy_ants
                                    if gamestate.euclidean_distance2(loc, enemy) <= gamestate.attackradius2]
                                    
                dying_enemy = len([enemy for enemy, owner in enemies_in_range
                                if influence_by_threat[owner][enemy] > threat])
                surviving_enemy = len([enemy for enemy, owner in enemies_in_range
                                if influence_by_threat[owner][enemy] < threat])

                combat_scores[loc] = (dying_enemy + 1.0) / (surviving_enemy + 1.0)
                
                # TODO: need to deal with special case 1v1, in which case we don't perform anything, 
                # leave it to combat explore which works quite well
                
    return combat_scores