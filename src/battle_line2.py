# battle_line2.py: combat algorithm by iterating through different distances
#   and try to put our ants into lines facing enemy ants                
#
# AI bot written for AI Challenge 2011 - Ants
# Author: Bill Y
# License: all your base are belong to us

from core import *
from collections import deque
import path, math, operator
import numpy as np

# kill zone, kill zone + 1 (danger zone), kill zone + 2, kill zone + 3
ZONE_BORDER = [6, 11, 18, 27]
    
def do_combat(gamestate):
    enemy_ants = [ant for ant, owner in gamestate.enemy_ants()]
    enemy_distance_map = get_distance_map(gamestate, enemy_ants, ZONE_BORDER[3])
    combat_groups = get_combat_groups(gamestate)
    if combat_groups is None:
        return
    perf_logger.debug('get_combat_groups.finish = %s' % str(gamestate.time_elapsed()))    
    
    for combat_group in combat_groups:
        debug_logger.debug('processing combat for group %s' % str(combat_group))
        do_group_combat(gamestate, combat_group, enemy_distance_map)
        perf_logger.debug('do_group_combat(for 1 group).finish = %s' % str(gamestate.time_elapsed()))
        
def do_group_combat(gamestate, combat_group, enemy_distance_map):
    my_group, enemy_group = combat_group
        
    perf_logger.debug('do_group_combat.kill evaluation = %s' % str(gamestate.time_elapsed()))   
    debug_logger.debug('getting kill moves')
    kill_move, kill_score = get_best_move(gamestate, my_group, enemy_group, enemy_distance_map, 1, ZONE_BORDER[0])
    if int(kill_score) > 0:    
        debug_logger.debug('executing kill move %s' % (str(kill_move)))
        execute_group_move(gamestate, my_group, kill_move)
        return
    
    perf_logger.debug('do_group_combat.danger evaluation = %s' % str(gamestate.time_elapsed()))   
    debug_logger.debug('getting danger moves')
    danger_move, danger_score = get_best_move(gamestate, my_group, enemy_group, enemy_distance_map, ZONE_BORDER[0], ZONE_BORDER[1])
    if int(danger_score) >= 0:    
        debug_logger.debug('executing danger move %s' % (str(danger_move)))
        execute_group_move(gamestate, my_group, danger_move)
        return
            
    perf_logger.debug('do_group_combat.safe evaluation = %s' % str(gamestate.time_elapsed()))   
    safe_moves = generate_move(gamestate, my_group, enemy_distance_map, ZONE_BORDER[1], ZONE_BORDER[2])
    debug_logger.debug('moving %s to safety %s' % (str(my_group), str(safe_moves)))
    execute_group_move(gamestate, my_group, safe_moves[0])

def get_best_move(gamestate, my_group, enemy_group, enemy_distance_map, min_distance, max_distance):
    moves = generate_move(gamestate, my_group, enemy_distance_map, min_distance, max_distance)
    # debug_logger.debug('moves = %s' % str(moves))
    best_move = []
    best_score = -10
    for move in moves:
        total_distance = sum([enemy_distance_map[ant] for ant in move])        
        score = evaluate_move(gamestate, move, enemy_group) - total_distance / 1000.0
        debug_logger.debug('evaluating kill move %s, %s' % (str(move), score))
        if score > best_score:
            best_move = move
            best_score = score

    return best_move, best_score
    
def execute_group_move(gamestate, my_group, group_move):
    for i in range(len(my_group)):
        gamestate.issue_order_by_location(my_group[i], group_move[i])
            
def evaluate_move(gamestate, my_group, enemy_group):
    # debug_logger.debug('my_move = %s' % str(my_group))
    
    my_distance_map = get_distance_map(gamestate, my_group, ZONE_BORDER[1])    
        
    enemy_kill_moves = generate_move(gamestate, enemy_group, my_distance_map, 1, ZONE_BORDER[1])
    
    worst_score = 10
    for enemy_move in enemy_kill_moves:
        enemy_distance_map = get_distance_map(gamestate, enemy_move, ZONE_BORDER[1]) 
        my_kill_ants = [ant for ant in my_group if enemy_distance_map[ant] >= 1 
                        and enemy_distance_map[ant] < ZONE_BORDER[0]]
        enemy_kill_ants = [ant for ant in enemy_move if my_distance_map[ant] >= 1
                        and my_distance_map[ant] < ZONE_BORDER[0]]

        score = len(my_kill_ants) - len(enemy_kill_ants) 
        # debug_logger.debug('enemy_move and score: %s : %d - %d' % (str(enemy_move), len(my_kill_ants), len(enemy_kill_ants)))
        if score < worst_score:
            worst_score = score
            
    return worst_score

def generate_move(gamestate, ant_group, opponent_distance_map, min_distance, max_distance):
    moves = generate_move_recurse(gamestate, ant_group, opponent_distance_map, min_distance, max_distance)
    
    # if there is no valid move combination, most likely due to conflict, resort to this heuristic method
    if len(moves) == 0:
        moves = generate_move_heuristic(gamestate, ant_group, opponent_distance_map, min_distance, max_distance)
        
    return moves
    
def generate_move_heuristic(gamestate, ant_group, opponent_distance_map, min_distance, max_distance):
    group_move = []
    for ant in ant_group:
        all_moves = [move for move in gamestate.passable_moves(ant) if move not in group_move]
        desirable_moves = [move for move in all_moves
                            if opponent_distance_map[move] >= min_distance
                            and opponent_distance_map[move] < max_distance]
        # if no move fits the condition, find one that is closest to min_distance
        if len(desirable_moves) == 0:
            all_distances = [opponent_distance_map[move] - min_distance for move in all_moves]
            if len(all_distances) > 0:
                positive_distances = [d for d in all_distances if d >= 0]
                if len(positive_distances) > 0:
                    best_distance = min(positive_distances)
                else:
                    best_distance = max(all_distances)
                group_move.append(all_moves[all_distances.index(best_distance)])
        else:
            group_move.append(desirable_moves[0])
        
    return [group_move]
    
def generate_move_recurse(gamestate, ant_group, opponent_distance_map, min_distance, max_distance):
    'min_distance is used with >=, and max_distance is used with <'
    # special: ant indexes do not change, in other words, actual orders needed to get from 
    # ant_group to full_result is just ant_group[i] move to full_result[n][i]
    all_moves = [move for move in gamestate.passable_moves(ant_group[0])]
    desirable_moves = [move for move in all_moves
                        if opponent_distance_map[move] >= min_distance
                        and opponent_distance_map[move] < max_distance]
    # if no move fits the condition, find one that is closest to min_distance
    if len(desirable_moves) == 0:
        all_distances = [math.fabs(opponent_distance_map[move] - min_distance) for move in all_moves]
        best_distance = min(all_distances)
        desirable_moves.append(all_moves[all_distances.index(best_distance)])
    
    full_result = []
    if len(ant_group) > 1:
        for sub_result in generate_move_recurse(gamestate, ant_group[1:], opponent_distance_map, min_distance, max_distance):
            for ant_loc in desirable_moves:
                # no duplicate locations in each formation
                if ant_loc in sub_result:
                    continue
                full_result.append([ant_loc] + sub_result)
    else:
        full_result = [[ant_loc] for ant_loc in desirable_moves]
        
    return full_result
    
def get_distance_map(gamestate, ant_group, cutoff):
    'from start_loc, find enemy ant within distance_limit'
    # http://en.wikipedia.org/wiki/Breadth-first_search#Pseudocode
    # create a queue Q
    list_q = deque(ant_group)
    # mark source, which has its value being its root, used for calculating distance
    marked_dict = {ant:ant for ant in ant_group}
    
    map = np.zeros((gamestate.rows, gamestate.cols), dtype=int) - 1
    while len(list_q) > 0:
        # dequeue an item from Q into v
        v = list_q.popleft()
        # for each edge e incident on v in Graph:
        for w in gamestate.neighbour_table[v]:
            distance = gamestate.euclidean_distance2(w, marked_dict[v])
            # set map
            map[w] = distance
            # if w is not marked
            if w not in marked_dict and w not in gamestate.water_list and distance < cutoff:                
                # mark w
                marked_dict[w] = marked_dict[v]
                # enqueue w onto Q
                list_q.append(w) 
                        
    return map
                
def get_combat_groups(gamestate):
    enemy_ants = [ant_loc for ant_loc, owner in gamestate.enemy_ants()]
    enemy_all_distance_map = get_distance_map(gamestate, enemy_ants, 5)
    enemy_groups = []
    while len(enemy_ants) > 0:
        enemy_group = bfs_get_group(gamestate, enemy_ants, enemy_all_distance_map)
        enemy_groups.append(enemy_group)
    
    enemy_reach_distance_map = get_distance_map(gamestate, enemy_ants, ZONE_BORDER[2])
    my_combat_ant_by_distance = {ant:enemy_reach_distance_map[ant] for ant in gamestate.my_unmoved_ants() if enemy_reach_distance_map[ant] >= 0}
    my_combat_ants = [ant for ant, distance in sorted(my_combat_ant_by_distance.iteritems(), key=operator.itemgetter(1), reverse=True)]
    
    combat_groups = []
    for enemy_group in enemy_groups:
        if len(my_combat_ants) > 0:
            enemy_group_distance_map = get_distance_map(gamestate, enemy_group, ZONE_BORDER[2])
            my_group = bfs_get_group(gamestate, my_combat_ants, enemy_group_distance_map)
            # set open fighters to gamestate, later used by planner
            if len(my_group) == len(enemy_group) == 1:
                gamestate.my_combat_explorers.extend(my_group)
            elif len(my_group) > 0 and len(enemy_group) > 0:
                gamestate.my_fighters.extend(my_group)
                combat_groups.append((my_group, enemy_group))
    
    # combined_distance_map = get_distance_map(gamestate, my_combat_ants + enemy_ants, ZONE_BORDER[0])
    
    # combat_groups = []
    # while len(my_combat_ants) > 0 and len(enemy_ants) > 0:
        # my_group, enemy_group = bfs_get_combat_group(gamestate, combined_distance_map, my_combat_ants, enemy_ants)

        # if len(my_group) == len(enemy_group) == 1:
            # gamestate.my_combat_explorers.extend(my_group)
        # elif len(my_group) > 0 and len(enemy_group) > 0:
            # gamestate.my_fighters.extend(my_group)
            # combat_groups.append((my_group, enemy_group))
            
    return combat_groups
    
def bfs_get_group(gamestate, ants, distance_map):
    'returns (my_group, enemy_group)'    
    start_ant = ants.pop()
    my_group = [start_ant]
    
    # http://en.wikipedia.org/wiki/Breadth-first_search#Pseudocode
    # create a queue Q
    list_q = deque([start_ant])
    # mark source, which has its value means nothing
    marked_dict = {start_ant:True}
    
    while len(list_q) > 0:
        # dequeue an item from Q into v
        v = list_q.popleft()
        # for each neighbour of v
        for w in gamestate.neighbour_table[v]:
            # if w is not marked
            if w not in marked_dict and w not in gamestate.water_list and distance_map[w] >= 0:   
                # mark w
                marked_dict[w] = True
                # enqueue w onto Q
                list_q.append(w) 
                if w in ants:
                    my_group.append(w)
                    ants.remove(w)
                    
    return my_group

    
def bfs_get_combat_group(gamestate, enemy_distance_map, my_combat_ants, enemy_ants):
    'returns (my_group, enemy_group)'    
    start_ant = my_combat_ants.pop()
    my_group = [start_ant]
    enemy_group = []
    
    # http://en.wikipedia.org/wiki/Breadth-first_search#Pseudocode
    # create a queue Q
    list_q = deque([start_ant])
    # mark source, which has its value means nothing
    marked_dict = {start_ant:True}
    
    while len(list_q) > 0:
        # dequeue an item from Q into v
        v = list_q.popleft()
        # for each neighbour of v
        for w in gamestate.neighbour_table[v]:
            if w in enemy_ants:
                enemy_group.append(w)
                enemy_ants.remove(w)
            # if w is not marked
            if w not in marked_dict and w not in gamestate.water_list and enemy_distance_map[w] >= 0:   
                # mark w
                marked_dict[w] = True
                # enqueue w onto Q
                list_q.append(w) 
                if w in my_combat_ants:
                    my_group.append(w)
                    my_combat_ants.remove(w)
                    
    return my_group, enemy_group
