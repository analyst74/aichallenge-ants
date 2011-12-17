# battle_line.py: combat algorithm utilizing a line-of-battle strategy
#
# AI bot written for AI Challenge 2011 - Ants
# Author: Bill Y
# License: all your base are belong to us

from core import *
import path

def do_combat(gamestate):
    zones = get_combat_zones(gamestate)
    
    if zones is not None:
        debug_logger.debug('zones.count = %d' % len(zones))
        for zone in zones:
            do_zone_combat(gamestate, zone)
            
def get_group_formations(gamestate, group):
    'get all possible formation of a group in a single turn'
    # special: ant indexes do not change, in other words, actual orders needed to get from 
    # group to full_result is just group[i] move to full_result[i]
    all_locs = gamestate.passable_moves(group[0])
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
    group_distance = 2**2
    support_distance = 2**2
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
        and min([gamestate.euclidean_distance2(ma, ma2) for ma2 in open_fighters]) < support_distance]

    # group my fighter/supporters into group by proximity
    # then find all enemy ants within range for each group
    # those two groups combined is considered a combat zone
    fighter_groups = []
    gamestate.my_fighters = []
    gamestate.my_combat_explorers = []
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
        
        # set open fighters to gamestate, later used by planner
        if len(group) > 1:
            gamestate.my_fighters.extend(group)
        elif len(group) == 1:
            gamestate.my_combat_explorers.extend(group)
        #debug_logger.debug('get_combat_zones setting my_fighters: %s' % str(gamestate.my_fighters))
        #debug_logger.debug('get_combat_zones setting my_combat_explorers: %s' % str(gamestate.my_combat_explorers))

    return fighter_groups
    
def eval_formation(gamestate, my_formation, enemy_formation):
    'return score, min_distance for the given my_formation/enemy_formation'
    # generate all pairs
    all_pairs = [(m, e) for m in my_formation for e in enemy_formation]
    # find the min_distance between our ants
    all_distances = [gamestate.euclidean_distance2(m,e) for m in my_formation for e in enemy_formation]
    min_distance = min(all_distances)
    # if there is no fighting, count the ants closest (loosely speaking) to enemies
    if min_distance > gamestate.attackradius2:
        min_distance_fuz = gamestate.euclidean_distance_add(min_distance, 0.4)
        #debug_logger.debug('min_distance_fuz = %f' % min_distance_fuz)
        # find out fighting pairs by getting all_pairs that has min_distance
        fighting_pairs = [all_pairs[i] for i,x in enumerate(all_distances) if x <= min_distance_fuz]
    # if there is fighting, just count all fighting ants
    else:
        fighting_pairs = [all_pairs[i] for i,x in enumerate(all_distances) if x <= gamestate.attackradius2]
        
    # create set (this ensures uniqueness)
    my_fighters = {}
    enemy_fighters = {}
    for m, e in fighting_pairs:
        my_fighters[m] = 1
        enemy_fighters[e] = 1
    
    return (float(len(my_fighters)) / len(enemy_fighters), min_distance)
    
def do_zone_combat(gamestate, zone):
    'zone combat'
    my_group, enemy_group = zone
    # either group is empty, invalid zone
    if len(my_group) == 0 or len(enemy_group) == 0:
        return
    # if we have only 1 ant, we can't win, skip and leave it to avoidance explore
    if len(my_group) == 1:    
        #debug_logger.debug('do_zone_combat.skipping due to 1v1')
        #gamestate.my_fighters.remove(my_group[0])
        return
        
    # we minimax on enemy stayed put or attacked (we're probably missing if enemy regrouped, but that's hard to predict)
    enemy_attack_formation, enemy_attack_orders = simulate_attack(gamestate, enemy_group, my_group)
       
    # TODO: re work this logic to be more elegant (but should have similar behaviour)
    # then try following 3 things, in that order:
    # 1, try to move into attackradius - 1 to attackradius - 2 (that's closest we can get, both we and enemy attack)
    # 2, try move into attackradius to attackradius - 1 (we regroup, enemy attack, we'll still fight)
    # 3, try move into attackradius + 1 to attackradius (we retreat, enemy attack, no fight)
    
    score, target_distance = eval_formation(gamestate, my_group, enemy_group)
    
    #debug_logger.debug('score, target_distance = %s, %s' % (str(score), str(target_distance)))
    # confidence is increased if we're winning overall
    if gamestate.winning_percentage > 0.65:
        confidence_threshold = 0.8
    else:
        confidence_threshold = 1.0
    attack_formation1, attack_orders1 = simulate_attack(gamestate, my_group, enemy_group)
    attack_score1, attack_distance1 = eval_formation(gamestate, attack_formation1, enemy_group)
    attack_formation2, attack_orders2 = simulate_attack(gamestate, my_group, enemy_attack_formation)
    attack_score2, attack_distance2 = eval_formation(gamestate, attack_formation2, enemy_attack_formation)
    
    # debug_logger.debug('attack_score1, attack_distance1 = %f, %d' % (attack_score1, attack_distance1))
    # debug_logger.debug('attack_score2, attack_distance2 = %f, %d' % (attack_score2, attack_distance2))
    
    if attack_score1 <= attack_score2:
        attack_score = attack_score2
        attack_orders = attack_orders2
    else:
        attack_score = attack_score1
        attack_orders = attack_orders1
    
    # if attacking is a good idea, then go!
    if attack_score > confidence_threshold:
        # materialize attack orders
        # debug_logger.debug('attack order: %s' % (str(attack_orders)))
        for order in attack_orders:
            ant, dest = order
            gamestate.issue_order_by_location(ant, dest)
    else:
        regroup(gamestate, my_group, enemy_group)
        
def simulate_attack(gamestate, my_group, enemy_group):    
    # for each ant, figure out a position that is closer to enemy
    attack_formation = list(my_group)
    attack_orders = []
    for ant in my_group:
        possible_moves = [ant] + [n_loc for n_loc in gamestate.neighbour_table[ant]
                                if gamestate.is_passable_override(n_loc, attack_formation, my_group)]
        move_distances = []        
        for move in possible_moves:
            me_pair = [(move,e) for e in enemy_group]
            me_distances = [gamestate.euclidean_distance2(m,e) for (m,e) in me_pair]
            move_distances.append(min(me_distances))
        best_move = possible_moves[move_distances.index(min(move_distances))]
        
        # order
        attack_orders.append((ant, best_move))
        attack_formation.remove(ant)
        attack_formation.append(best_move)
        
    return attack_formation, attack_orders
    
def regroup(gamestate, my_group, enemy_group):
    'alternatively, find optimal places, and have each ant claim closest one, allow ants in distress to choose first'
    min_distance = gamestate.euclidean_distance_add(gamestate.attackradius2, 1)
    regroup_formation = list(my_group)
    # dict of source_loc => (order, target_loc), used for retract purpose
    regroup_orders = {}

    # work on ants from lowest distance to highest
    ant_distances = []
    for my_ant in my_group:
        ant_distances.append(min([gamestate.euclidean_distance2(my_ant, enemy_ant) for enemy_ant in enemy_group]))
        
    my_ants_by_distance = [ant for distance, ant in sorted(zip(ant_distances, my_group))]
    for my_ant in my_ants_by_distance:
        resolve_regroup_move(gamestate, my_ant, regroup_formation, regroup_orders, my_ants_by_distance, enemy_group, min_distance, [])
        
    for my_ant in my_ants_by_distance:
        gamestate.issue_order_by_location(my_ant, regroup_orders[my_ant])
        # debug_logger.debug('regroup order: %s' % (str(order)))
        
def resolve_regroup_move(gamestate, my_ant, regroup_formation, regroup_orders, my_ants_by_distance, enemy_group, min_distance, retracted_from):
    'ugly recursive function to make sure all moves are valid, if this damn thing proves to be slow, its probably better to just rewrite using minimax'
    # get all moves based on preference, move into the first available spot
    moves_by_preference = get_moves_by_preference(gamestate, my_ant, regroup_formation, enemy_group, min_distance)
    best_move = None
    regroup_formation.remove(my_ant)
    for move in moves_by_preference:
        if gamestate.is_passable_override(move, regroup_formation, my_ants_by_distance): 
            best_move = move
            break

    # if no best move was found, this means all the possible positions, including the ant's current location are taken
    # we need to retract to previous ant and make it move else where    
    retract_ant = None    
    if best_move is None:
        # debug_logger.debug('move retraction logic triggered!')
        # find last order moved into any of my possible moves
        for ant in reversed(my_ants_by_distance):
            if ant in regroup_orders:
                target_loc = regroup_orders[ant]
                # valid retractable must be a possible move (moves_by_preference)
                # AND it cannot be within retracted_from, to prevent infinite loop
                if target_loc in moves_by_preference and target_loc not in retracted_from:
                    # undo that one
                    regroup_formation.remove(target_loc)
                    regroup_formation.append(ant)
                    del regroup_orders[ant]
                    # do this one
                    best_move = target_loc
                    break

    # some bug must've happened
    if best_move is None:
        debug_logger.debug('move retraction failed!')
        debug_logger.debug('my_ant = %s' % str(my_ant))
        debug_logger.debug('regroup_orders = %s' % str(regroup_orders))
        debug_logger.debug('my_ants_by_distance = %s' % str(my_ants_by_distance))
        debug_logger.debug('regroup_formation = %s' % str(regroup_formation))
        debug_logger.debug('retracted_from = %s' % str(retracted_from))
        debug_logger.debug('moves_by_preference = %s' % str(moves_by_preference))
        
        
    # convert to direction
    directions = gamestate.direction(my_ant, best_move) + [None]
    
    # add the move 
    regroup_formation.append(best_move)
    regroup_orders[my_ant] = best_move
    
    # try do retracted one again, if any
    if retract_ant is not None:
        resolve_regroup_move(gamestate, my_ant, regroup_formation, regroup_orders, my_ants_by_distance, enemy_group, min_distance, retracted_from + [best_move])
    
        
def get_moves_by_preference(gamestate, my_ant, regroup_formation, enemy_group, min_distance):
    'move an ant to closest spot to enmy_group, above min_distance'
    all_moves = [my_ant] + [n_loc for n_loc in gamestate.neighbour_table[my_ant]     
                            if gamestate.is_passable(n_loc)]
    
    all_scores = []
    for move in all_moves:
        distance = min([gamestate.euclidean_distance2(move, enemy_ant) for enemy_ant in enemy_group])
        # score the moves based on following rules:
        # 1, for move distance > min_distance, score = 1 / distance, the smaller distance the better the score
        if distance > min_distance:
            # distance+1 to avoid division by 0
            all_scores.append(float(1)/(distance+1))
        # 2, for move distance < min_distance, score = - distance, the greater distance the better the score
        else:
            all_scores.append(float(1)/-(distance+1))
    
    # sort the moves and distances together
    sorted_score_moves = sorted(zip(all_scores, all_moves), reverse=True)
    
    # debug_logger.debug('sorted_score_moves = %s' % (str(sorted_score_moves)))
    return [move for score, move in sorted_score_moves]
