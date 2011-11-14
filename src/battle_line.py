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
                            if n_loc not in gamestate.water_list]
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
    support_distance = 1
    enemy_distance = gamestate.euclidean_distance_add(gamestate.attackradius2, 3)
    enemy_ants = [ant_loc for ant_loc, owner in gamestate.enemy_ants()]    
    if len(enemy_ants) == 0:
        return None
    # first get all my ants close to enemy, aka fighters
    open_fighters = [ma for ma in gamestate.my_unmoved_ants() 
        if min([gamestate.euclidean_distance2(ma, ea) for ea in enemy_ants]) < enemy_distance
        and path.bfs_findenemy(gamestate, ma, enemy_distance)]
    if len(open_fighters) == 0:
        return None
    # get all ants not in enemy range, but close to my fighters, aka supporters
    open_supporters = [ma for ma in gamestate.my_unmoved_ants() 
        if ma not in open_fighters
        and min([gamestate.euclidean_distance2(ma, ma2) for ma2 in open_fighters]) <= support_distance]
    
    # set open fighters to gamestate, later used by planner
    gamestate.my_fighters = open_fighters

    # group my fighter/supporters into group by proximity
    # then find all enemy ants within range for each group
    # those two groups combined is considered a combat zone
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
    min_distance_fuz = gamestate.euclidean_distance_add(min_distance, 0.4)
    #logging.debug('min_distance_fuz = %f' % min_distance_fuz)
    # find out fighting pairs by getting all_pairs that has min_distance
    fighting_pairs = [all_pairs[i] for i,x in enumerate(all_distances) if x <= min_distance_fuz]
    # create set (this ensures uniqueness)
    my_fighters = {}
    enemy_fighters = {}
    for m, e in fighting_pairs:
        my_fighters[m] = 1
        enemy_fighters[e] = 1
    
    return (float(len(my_fighters)) / len(enemy_fighters), min_distance)
    
# def do_zone_combat(gamestate, zone):
    # 'alternate between expensive and cheap combat solutions'
    # my_group, enemy_group = zone
    # if len(my_group) < 4:
        # do_zone_combat_expensive(gamestate, zone)
    # else:
        # do_zone_combat_cheap(gamestate, zone)
        
def do_zone_combat_expensive(gamestate, zone):
    'find best formation among permutations'
    my_group, enemy_group = zone
    if len(my_group) == 0 or len(enemy_group) == 0:
        return
    
    # find out possible formations
    all_formations = get_group_formations(gamestate, my_group)
    
    # score each formation
    # all dict below uses all_formation's index as key for back reference purpose
    # separating between attack and regroup based on scores
    attack_scores = {}
    attack_distances = {}
    regroup_scores = {}
    regroup_distances = {}
    for i in xrange(len(all_formations)):
        score, distance = eval_formation(gamestate, all_formations[i], enemy_group)
        if score > 1: # this value can be modified to change aggressiveness
            attack_scores[i] = score
            attack_distances[i] = distance
        else:
            regroup_scores[i] = score
            regroup_distances[i] = distance
            
    # try to attack
    if len(attack_distances) > 0:
        best_formation = all_formations[min(attack_distances,key=attack_distances.get)]
    # if no desirable attack option, regroup
    else:
        # get distances that are in a safe range
        safe_distance = gamestate.euclidean_distance_add(gamestate.attackradius2, 1)
        safe_regroup_distances = {i:distance for i,distance in regroup_distances.items()
                                if distance > safe_distance}
        #safe_regroup_scores = {i:score for i,score in regroup_scores.items() if i in safe_regroup_distances}
        # if len(safe_regroup_scores) == 0:
            # logging.debug('all_formations for %s = %s' % (str(my_group), str(all_formations)))
            # logging.debug('regroup_scores = %s' % str(regroup_scores))
            # logging.debug('regroup_distances = %s' % str(regroup_distances))
            # logging.debug('safe_regroup_distances = %s' % str(safe_regroup_distances))
            # logging.debug('safe_regroup_scores = %s' % str(safe_regroup_scores))
            # logging.debug('safe_distance = %d' % safe_distance)
        if len(safe_regroup_distances) > 0:
            # safe distance possible, pick formation closer to enemy
            best_formation = all_formations[min(safe_regroup_distances,key=safe_regroup_distances.get)]
        else:
            # no safe distance, pick one with highest score
            best_score = max([value for key,value in regroup_scores.items()])
            best_regroup_scores = {i:score for i,score in regroup_scores.items() if score==best_score}
            # then pick one with furthest distance, hoping we'll escape some of them?
            # but we're fucked here anyways
            best_regroup_distances = {i:distance for i,distance in regroup_distances.items() if i in best_regroup_scores}
            best_formation = all_formations[max(best_regroup_distances,key=best_regroup_distances.get)]
    
    logging.debug('best_formation for %s is %s' % (str(my_group), str(best_formation)))
    # issue move order
    for i in xrange(len(my_group)):
        directions = gamestate.direction(my_group[i], best_formation[i]) + [None]
        gamestate.issue_order((my_group[i], directions[0]))
    
def do_zone_combat_cheap(gamestate, zone):
    'do no pruning, push all ants to be smallest value above average distance'
    my_group, enemy_group = zone
    if len(my_group) == 0 or len(enemy_group) == 0:
        return
        
    score, target_distance = eval_formation(gamestate, my_group, enemy_group)
    
    #logging.debug('score, target_distance = %s, %s' % 
    #    (str(score), str(target_distance)))
    # be closer to enemy if feeling strong
    if score > 1:
        target_distance = 0
    # be further away from enemy if not so
    elif score <= 1:
        target_distance = gamestate.euclidean_distance_add(gamestate.attackradius2, 1)
    
    # for each ant, figure out a position that is smallest above average
    for ant in my_group:
        possible_moves = [ant] + [n_loc for n_loc in gamestate.get_neighbour_locs(ant) 
            if gamestate.is_passable(n_loc)]
        move_distances = []
        for move in possible_moves:
            me_pair = [(move,e) for e in enemy_group]
            me_distances = [gamestate.euclidean_distance2(m,e) for (m,e) in me_pair]
            move_distances.append(min(me_distances))
        # move to place closest to and greater than target_distance
        preferred_distances = [distance for distance in move_distances if distance > target_distance]
        if len(preferred_distances) > 0:
            best_move = possible_moves[move_distances.index(min(preferred_distances))]
        # all moves are below target distance, run for your lives!
        else:
            best_move = possible_moves[move_distances.index(max(move_distances))]
        #logging.debug('possible_moves = %s' % str(possible_moves))
        #logging.debug('move_distances = %s' % str(move_distances))
        #logging.debug('preferred_distances = %s' % str(preferred_distances))
        #logging.debug('best_move = %s' % str(best_move))
        
        # order
        direction = gamestate.direction(ant, best_move)
        gamestate.issue_order((ant, None if len(direction) == 0 else direction[0]))

def do_zone_combat(gamestate, zone):
    'zone combat'
    my_group, enemy_group = zone
    if len(my_group) == 0 or len(enemy_group) == 0:
        return
        
    score, target_distance = eval_formation(gamestate, my_group, enemy_group)
    
    logging.debug('score, target_distance = %s, %s' % (str(score), str(target_distance)))
    # if feeling strong, attack!
    if score > 1:
        attack(gamestate, my_group, enemy_group)
    # if not, regroup at safe distance
    elif score <= 1:
        regroup2(gamestate, my_group, enemy_group)
        
        
def attack(gamestate, my_group, enemy_group):    
    # for each ant, figure out a position that is closer to enemy
    for ant in my_group:
        possible_moves = [ant] + [n_loc for n_loc in gamestate.get_neighbour_locs(ant) 
                                if gamestate.is_passable(n_loc)]
        move_distances = []
        for move in possible_moves:
            me_pair = [(move,e) for e in enemy_group]
            me_distances = [gamestate.euclidean_distance2(m,e) for (m,e) in me_pair]
            move_distances.append(min(me_distances))
        best_move = possible_moves[move_distances.index(min(move_distances))]
        
        # order
        direction = gamestate.direction(ant, best_move) + [None]
        order = (ant, direction[0])
        gamestate.issue_order(order)
        logging.debug('attack order: %s' % (str(order)))
        
def regroup(gamestate, my_group, enemy_group):
    'permutation selection'
    # get all formations
    # TODO: eliminate formations with loose formation (how to determine that?)
    # for each formation, calculate its min_distance and average distance
    # get rid of min_distance lower than safe range
    # use the lowest average distance
    pass
    
def regroup2(gamestate, my_group, enemy_group):
    'alternatively, find optimal places, and have each ant claim closest one, allow ants in distress to choose first'
    min_distance = gamestate.euclidean_distance_add(gamestate.attackradius2, 1)
    move_table = {}
    
    # work on distressed ants
    un_distressed_ants = []
    for my_ant in my_group:
        distance = min([gamestate.euclidean_distance2(my_ant, enemy_ant) for enemy_ant in enemy_group])
        if distance <= min_distance:
            order = move_to_distance(gamestate, my_ant, enemy_group, min_distance, ignore_ant=True)
            gamestate.issue_order(order)
            logging.debug('regroup2 order: %s' % (str(order)))
        else:
            un_distressed_ants.append(my_ant)
            
    # work on non distressed ones
    for my_ant in un_distressed_ants:
        order = move_to_distance(gamestate, my_ant, enemy_group, min_distance, ignore_ant=False)
        gamestate.issue_order(order)
        logging.debug('regroup2 order: %s' % (str(order)))
        
        
def move_to_distance(gamestate, my_ant, enemy_group, min_distance, ignore_ant):
    'move an ant to closest spot to enmy_group, above min_distance'
    if ignore_ant:
        all_moves = [my_ant] + [n_loc for n_loc in gamestate.neighbour_table[my_ant]     
                                if n_loc not in gamestate.water_list]
    else:
        all_moves = [my_ant] + [n_loc for n_loc in gamestate.neighbour_table[my_ant]     
                                if gamestate.is_passable(n_loc)]
    
    all_distances = []
    for move in all_moves:
        distance = min([gamestate.euclidean_distance2(move, enemy_ant) for enemy_ant in enemy_group])
        all_distances.append(distance)
    
    # sort the moves and distances together
    sorted_list = sorted(zip(all_distances, all_moves))
    
    # use the lowest distance that's above min distance
    target_move = None
    for distance, move in sorted_list:
        if distance > min_distance:
            target_move = move
            break
    # if all moves are below min distance, use the highest distance
    if target_move == None:
        target_move = sorted_list[-1][1]
        
    # issue order
    direction = gamestate.direction(my_ant, target_move) + [None]
    return (my_ant, direction[0])