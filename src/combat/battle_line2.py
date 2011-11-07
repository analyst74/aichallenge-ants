# battle_line.py: combat algorithm utilizing a line-of-battle strategy
#
# AI bot written for AI Challenge 2011 - Ants
# Author: Bill Y
# License: all your base are belong to us

from core import *
import path

def get_group_formations(gamestate, group):
    'get all possible formation of a group in a single turn'
    # special: ant indexes do not change, in other words, actual orders needed to get from 
    # group to full_result is just group[i] move to full_result[i]
    all_locs = [group[0]] + [n_loc for n_loc in gamestate.get_neighbour_locs(group[0]) 
        if not gamestate.is_passable(n_loc)]
    full_result = []
    if len(group) > 1:
        for sub_result in get_group_formations(gamestate, group[1:]):
            for ant_loc in all_locs:
                # no duplicate locations in each formation
                if ant_loc in sub_result:
                    continue
                full_result.append([ant_loc] + sub_result)
    else:
        full_result = [[ant_loc] for ant_loc in all_locs]
        
    return full_result

def get_combat_zones(gamestate):
    'get all my fighter ants in groups'
    group_distance = 3**2
    enemy_distance = gamestate.euclidean_distance_add(gamestate.attackradius2, 3)
    enemy_ants = [ant_loc for ant_loc, owner in gamestate.enemy_ants()]    
    if len(enemy_ants) == 0:
        return None
    
    open_fighters = [ma for ma in gamestate.my_unmoved_ants() 
        if min([gamestate.euclidean_distance2(ma, ea) for ea in enemy_ants]) < enemy_distance]
    if len(open_fighters) == 0:
        return None
        
    #open_supporters = path.bfs(gamestate, open_fighters, group_distance, 
    #    lambda loc : gamestate.is_my_unmoved_ant(loc) and loc not in open_fighters)
    open_supporters = [ma for ma in gamestate.my_unmoved_ants() 
        if ma not in open_fighters
        and min([gamestate.euclidean_distance2(ma, ma2) for ma2 in open_fighters]) < group_distance]
    
    # set open fighters to gamestate
    gamestate.my_fighters = open_fighters

    fighter_groups = []
    while len(open_fighters) > 0:
        first_ant = open_fighters.pop()
        group = [first_ant]
        group_i = 0
        while len(group) > group_i:
            fighter_friends = [ant for ant in open_fighters 
                if gamestate.euclidean_distance2(group[group_i], ant) < group_distance]
            supporter_friends = [ant for ant in open_supporters 
                if gamestate.euclidean_distance2(group[group_i], ant) < group_distance]
            group.extend(fighter_friends)
            group.extend(supporter_friends)
            open_fighters = [ant for ant in open_fighters if ant not in fighter_friends]
            open_supporters = [ant for ant in open_supporters if ant not in supporter_friends]
            group_i += 1
        
        group_enemy = [ea for ea in enemy_ants 
            if min([gamestate.euclidean_distance2(ma, ea) for ma in group]) < enemy_distance]
        fighter_groups.append((group, group_enemy))

    return fighter_groups
    
def eval_formation(gamestate, my_formation, enemy_formation):
    'return score, min_distance for the given my_formation/enemy_formation'
    # generate all pairs
    all_pairs = [(m, e) for m in my_formation for e in enemy_formation]
    # find the min_distance between our ants
    all_distances = [gamestate.euclidean_distance2(m,e) for m in my_formation for e in enemy_formation]
    min_distance = min(all_distances)
    min_distance_fuz = gamestate.euclidean_distance_add(min_distance, 0.5)
    # find out fighting pairs by getting all_pairs that has min_distance
    fighting_pairs = [all_pairs[i] for i,x in enumerate(all_distances) if x <= min_distance_fuz]
    # create set (this ensures uniqueness)
    my_fighters = {}
    enemy_fighters = {}
    for m, e in fighting_pairs:
        my_fighters[m] = 1
        enemy_fighters[e] = 1
    
    return (len(my_fighters) - len(enemy_fighters), min_distance)

def do_zone_combat(gamestate, zone):
    'do no pruning, push all ants to be smallest value above average distance'
    my_group, enemy_group = zone
    if len(my_group) == 0 or len(enemy_group) == 0:
        return
        
    score, target_distance = eval_formation(gamestate, my_group, enemy_group)
    
    #logging.debug('score, target_distance = %s, %s' % 
    #    (str(score), str(target_distance)))
    # be closer to enemy if feeling strong
    if score > 0:
        target_distance = 0
    elif score < 0:
        target_distance = gamestate.euclidean_distance_add(target_distance, 1)
        
    # for each ant, figure out a position that is smallest above average
    for ant in my_group:
        possible_moves = [ant] + [n_loc for n_loc in gamestate.get_neighbour_locs(ant) 
            if gamestate.is_passable(n_loc)]
        move_distances = []
        for move in possible_moves:
            me_pair = [(move,e) for e in enemy_group]
            me_distances = [gamestate.euclidean_distance2(m,e) for (m,e) in me_pair]
            move_distances.append(min(me_distances))
        preferred_distances = [distance for distance in move_distances 
            if distance > target_distance]
        if len(preferred_distances) > 0:
            best_move = possible_moves[move_distances.index(min(preferred_distances))]
        else:
            best_move = possible_moves[move_distances.index(max(move_distances))]
        #logging.debug('possible_moves = %s' % str(possible_moves))
        #logging.debug('move_distances = %s' % str(move_distances))
        #logging.debug('preferred_distances = %s' % str(preferred_distances))
        #logging.debug('best_move = %s' % str(best_move))
        
        # order
        direction = gamestate.direction(ant, best_move)
        gamestate.issue_order((ant, None if len(direction) == 0 else direction[0]))
   