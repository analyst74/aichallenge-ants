#!/usr/bin/env python
import sys
import traceback
import random
import time
from collections import defaultdict
from math import sqrt
from collections import deque
from decimal import *

import logging
DEBUG_LOG_NAME = 'debug.log'
logging.basicConfig(filename=DEBUG_LOG_NAME,level=logging.DEBUG,filemode='w')

HILL = 20
# enemy number will range from 1 to n-1, where n is total number of players on map
MY_ANT = 0
DEAD = -1
LAND = -2
FOOD = -3
WATER = -4

PLAYER_ANT = 'abcdefghij'
HILL_ANT = string = 'ABCDEFGHI'
PLAYER_HILL = string = '0123456789'
MAP_OBJECT = '?%*.!'
MAP_RENDER = PLAYER_ANT + HILL_ANT + PLAYER_HILL + MAP_OBJECT

AIM = {'n': (-1, 0),
       'e': (0, 1),
       's': (1, 0),
       'w': (0, -1)}
RIGHT = {'n': 'e',
         'e': 's',
         's': 'w',
         'w': 'n'}
LEFT = {'n': 'w',
        'e': 'n',
        's': 'e',
        'w': 's'}
BEHIND = {'n': 's',
          's': 'n',
          'e': 'w',
          'w': 'e'}

ALL_DIRECTIONS = ['n', 'e', 's', 'w']
          
class Ants():
    def __init__(self):
        self.cols = None
        self.rows = None
        self.map = None
        self.beaten_path = None
        self.hill_list = {}
        self.ant_list = {}
        self.dead_list = defaultdict(list)
        self.food_list = []
        self.turntime = 0
        self.loadtime = 0
        self.turn_start_time = None
        self.vision = None
        self.viewradius2 = 0
        self.attackradius2 = 0
        self.spawnradius2 = 0
        self.turns = 0
        self.current_turn = 0
        self.sqrt_table = {}
        # formation permutation counter, to be removed after profiling
        self.counter = 0

    def setup(self, data):
        'parse initial input and setup starting game state'
        for line in data.split('\n'):
            line = line.strip().lower()
            if len(line) > 0:
                tokens = line.split()
                key = tokens[0]
                if key == 'cols':
                    self.cols = int(tokens[1])
                elif key == 'rows':
                    self.rows = int(tokens[1])
                elif key == 'player_seed':
                    random.seed(int(tokens[1]))
                elif key == 'turntime':
                    self.turntime = int(tokens[1])
                elif key == 'loadtime':
                    self.loadtime = int(tokens[1])
                elif key == 'viewradius2':
                    self.viewradius2 = int(tokens[1])
                elif key == 'attackradius2':
                    self.attackradius2 = int(tokens[1])
                elif key == 'spawnradius2':
                    self.spawnradius2 = int(tokens[1])
                elif key == 'turns':
                    self.turns = int(tokens[1])
        self.map = [[LAND for col in range(self.cols)]
                    for row in range(self.rows)]
        self.beaten_path = [[0 for col in range(self.cols)]
                            for row in range(self.rows)]
                            
    def update(self, data):
        'parse engine input and update the game state'
        self.counter = 0
        
        # start timer
        self.turn_start_time = time.clock()
        
        # reset vision
        self.vision = None
        
        # reduce beaten path
        self.beaten_path = [[int(max(0, x-max(x/10,1))) for x in y] for y in self.beaten_path]
        
        # hill is slightly different, we do want to remember 
        # where hills are, so we know where to attack
        hills_to_remove = []
        for row, col in self.hill_list.keys():
            if self.map[row][col] != HILL:
                hills_to_remove.append((row,col))
        for loc in hills_to_remove:
            del self.hill_list[loc]

        # clear ant and food data
        for row, col in self.ant_list.keys():
            self.map[row][col] = LAND
        self.ant_list = {}
        
        for row, col in self.dead_list.keys():
            self.map[row][col] = LAND            
        self.dead_list = defaultdict(list)
        
        for row, col in self.food_list:
            self.map[row][col] = LAND            
        self.food_list = []
        
        # update map and create new ant and food lists
        for line in data.split('\n'):
            line = line.strip().lower()
            if len(line) > 0:
                tokens = line.split()
                if len(tokens) == 2:
                    # log current turn
                    self.current_turn = tokens[1]
                elif len(tokens) >= 3 and len(tokens[0]) == 1:
                    row = int(tokens[1])
                    col = int(tokens[2])
                    if tokens[0] == 'w':
                        self.map[row][col] = WATER
                    elif tokens[0] == 'f':
                        self.map[row][col] = FOOD
                        self.food_list.append((row, col))
                    else:
                        owner = int(tokens[3])
                        if tokens[0] == 'a':
                            self.map[row][col] = owner
                            self.ant_list[(row, col)] = (owner, False)
                        elif tokens[0] == 'd':
                            # food could spawn on a spot where an ant just died
                            # don't overwrite the space unless it is land
                            if self.map[row][col] == LAND:
                                self.map[row][col] = DEAD
                            # but always add to the dead list
                            self.dead_list[(row, col)].append(owner)
                        elif tokens[0] == 'h':
                            owner = int(tokens[3])
                            self.map[row][col] = HILL
                            self.hill_list[(row, col)] = owner

    def time_remaining(self):
        return self.turntime - self.time_elapsed()
    
    def time_elapsed(self):
        return int(1000 * (time.clock() - self.turn_start_time))
    
    def issue_order(self, order):
        'issue an order by writing the proper ant location and direction'
        (row, col), direction = order
        #early exit
        if direction is None:
            self.ant_list[(row,col)] = (MY_ANT, True)
            logging.debug('moving %s -- stationary' % str((row, col)))
            return
        
        (newrow, newcol) = self.destination((row, col), direction)
        if self.passable((newrow, newcol)):
            sys.stdout.write('o %s %s %s\n' % (row, col, direction))
            sys.stdout.flush()
            logging.debug('moving %s to %s' % (str((row, col)), str((newrow, newcol))))
            # update ant moved flag
            del self.ant_list[(row,col)]
            self.ant_list[(newrow, newcol)] = (MY_ANT, True)
            # update map info (to avoid to ants moving into the same spot)
            self.map[newrow][newcol] = MY_ANT
            self.map[row][col] = LAND
            # set level of beaten path
            self.beaten_path[row][col] += 10
            # increase adjacent ones too
            for d in self.passable_directions((row, col)):
                (adj_row, adj_col) = self.destination((row, col), d)
                self.beaten_path[adj_row][adj_col] += 5
    
    def finish_turn(self):
        'finish the turn by writing the go line'
        sys.stdout.write('go\n')
        sys.stdout.flush()
    
    def my_hills(self):
        return [loc for loc, owner in self.hill_list.items()
                    if owner == MY_ANT]

    def enemy_hills(self):
        return [(loc, owner) for loc, owner in self.hill_list.items()
                    if owner != MY_ANT]
        
    def my_ants(self):
        'return a list of all my ants'
        return [(row, col) for (row, col), (owner, moved) in self.ant_list.items()
                    if owner == MY_ANT]

    def my_unmoved_ants(self):
        'return a list of un-moved ants'
        return [(row, col) for (row, col), (owner, moved) in self.ant_list.items()
                    if owner == MY_ANT and not moved]
                    
    def enemy_ants(self):
        'return a list of all visible enemy ants'
        return [((row, col), owner)
                    for (row, col), (owner, moved) in self.ant_list.items()
                    if owner != MY_ANT]

    def is_ant(self, loc, has_moved, is_my_ant):
        'get active ant, hack: enemy ant is always active'
        if loc in self.ant_list:
            owner, moved = self.ant_list[loc]
            if moved == has_moved and is_my_ant == (owner == MY_ANT):
                return True
        return False
                    
    def food(self):
        'return a list of all food locations'
        return self.food_list[:]

    def passable(self, loc):
        'true if not water or ant or food'
        row, col = loc
        return self.map[row][col] > FOOD and self.map[row][col] != MY_ANT
        
    def passable_directions(self, loc):
        'finds valid move from given location, based on passable'
        passable_directions = []
        for direction in ALL_DIRECTIONS:
            new_loc = self.destination(loc, direction)
            if (self.passable(new_loc)):
                passable_directions.append(direction)
                
        return passable_directions
        
    def unoccupied(self, loc):
        'true if no ants are at the location'
        row, col = loc
        return self.map[row][col] in (LAND, DEAD)

    def destination(self, loc, direction):
        'calculate a new location given the direction and wrap correctly'
        row, col = loc
        d_row, d_col = AIM[direction]
        return ((row + d_row) % self.rows, (col + d_col) % self.cols)        

    def manhattan_distance(self, loc1, loc2):
        'calculate the manhattan distance between to locations'
        row1, col1 = loc1
        row2, col2 = loc2
        d_col = min(abs(col1 - col2), self.cols - abs(col1 - col2))
        d_row = min(abs(row1 - row2), self.rows - abs(row1 - row2))
        return d_row + d_col

    def euclidean_distance2(self, loc1, loc2):
        'calculate the euclidean distance between to locations'
        row1, col1 = loc1
        row2, col2 = loc2
        d_col = min(abs(col1 - col2), self.cols - abs(col1 - col2))
        d_row = min(abs(row1 - row2), self.rows - abs(row1 - row2))
        return d_row**2 + d_col**2
        
    def euclidean_distance_add(self, distance2, addition):
        'do euclidean math.add'
        distance = self.get_sqrt(distance2)
        return (distance+addition)**2

    def get_sqrt(self, num):
        if num not in self.sqrt_table:
            self.sqrt_table[num] = sqrt(num)
        return self.sqrt_table[num]
            
    def direction(self, loc1, loc2):
        'determine the 1 or 2 fastest (closest) directions to reach a location'
        row1, col1 = loc1
        row2, col2 = loc2
        height2 = self.rows//2
        width2 = self.cols//2
        d = []
        if row1 < row2:
            if row2 - row1 >= height2:
                d.append('n')
            if row2 - row1 <= height2:
                d.append('s')
        if row2 < row1:
            if row1 - row2 >= height2:
                d.append('s')
            if row1 - row2 <= height2:
                d.append('n')
        if col1 < col2:
            if col2 - col1 >= width2:
                d.append('w')
            if col2 - col1 <= width2:
                d.append('e')
        if col2 < col1:
            if col1 - col2 >= width2:
                d.append('e')
            if col1 - col2 <= width2:
                d.append('w')
        return d        

    def move_to_spot(self, loc, max_ant, max_search = 100):
        'find closet ant that belongs to self to a particular location'
        # return location of the first ant (after its move)
        first_ant_loc = None
        moved_ant_count = 0
        
        # http://en.wikipedia.org/wiki/Breadth-first_search#Pseudocode
        # create a queue Q
        list_q = deque()
        # enqueue (source, level) onto Q
        list_q.append(loc)
        # mark source
        marked_dict = { loc: True }
        
        search_count = 0
        while len(list_q) > 0:
            # limit max search depth and max ant moved
            if search_count > max_search or moved_ant_count > max_ant:
                break
            search_count += 1
            # dequeue an item from Q into v
            v = list_q.popleft()
            # for each edge e incident on v in Graph:
            for e in ALL_DIRECTIONS:
                # let w be the other end of e
                w = self.destination(v, e)
                # if w is not marked
                if w not in marked_dict:
                    # w must not be water
                    (w_row, w_col) = w
                    if self.map[w_row][w_col] != WATER:
                        # mark w
                        marked_dict[w] = True
                        # enqueue w onto Q
                        list_q.append(w)       
                        # break out if we find our own ant
                        if w in self.my_ants():
                            (owner, moved) = self.ant_list[w]
                            # if ant has not moved yet, use it
                            if not moved:
                                # only move in if target spot is move-in-able
                                # there is only one case where v is not passable
                                #   when it is the starting spot (i.e. hill raze leader)
                                if self.passable(v):
                                    self.issue_order((w, BEHIND[e]))
                                else:
                                    # stay stationary otherwise
                                    self.issue_order((w, None))
                                # set first ant
                                if first_ant_loc is None:
                                    first_ant_loc = w
                                # increment ant count
                                moved_ant_count += 1
                        
        return first_ant_loc  
    
    def visible(self, loc):
        ' determine which squares are visible to the given player '

        if self.vision == None:
            if not hasattr(self, 'vision_offsets_2'):
                # precalculate squares around an ant to set as visible
                self.vision_offsets_2 = []
                mx = int(sqrt(self.viewradius2))
                for d_row in range(-mx,mx+1):
                    for d_col in range(-mx,mx+1):
                        d = d_row**2 + d_col**2
                        if d <= self.viewradius2:
                            self.vision_offsets_2.append((
                                d_row%self.rows-self.rows,
                                d_col%self.cols-self.cols
                            ))
            # set all spaces as not visible
            # loop through ants and set all squares around ant as visible
            self.vision = [[False]*self.cols for row in range(self.rows)]
            for ant in self.my_ants():
                a_row, a_col = ant.loc
                for v_row, v_col in self.vision_offsets_2:
                    self.vision[a_row+v_row][a_col+v_col] = True
        row, col = loc
        return self.vision[row][col]
    
    def is_water(self, loc):
        (row, col) = loc
        return self.map[row][col] == WATER
        
    def get_neighbour_locs(self, loc):
        'get all neighbour locations, except those are water'
        return [self.destination(loc, direction) for direction in ALL_DIRECTIONS        
                        if not self.is_water(loc)]

    def bfs(self, start_locs, range_limit, func_condition):
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
                w = self.destination(v, e)
                # if w is not marked
                if not w in marked_dict:
                    # w must not be water and 
                    (w_row, w_col) = w  
                    distance = min([self.euclidean_distance2(loc, w) for loc in start_locs])
                    if (self.map[w_row][w_col] != WATER and 
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

    def get_my_ants_in_range(self, enemy_group, range):        
        'find all my ants within distance of enemy_group'
        # instead of looping through all self.my_ants() like we do with finding enemy ants
        # we want to use bfs with self.map, as self.my_ants() could be fairly big in late game
        my_group = self.bfs(enemy_group, range, 
            lambda loc : self.map[loc[0]][loc[1]] == MY_ANT and self.ant_list[loc][1] == False)
        
        return my_group
        
    def get_combat_zones(self):
        'get all current combat zones'        
        #group_distance = self.viewradius2
        group_distance = self.euclidean_distance_add(self.attackradius2, 2)
        enemy_ants = [ant_loc for ant_loc, owner in self.enemy_ants()]
        open_set = enemy_ants + self.get_my_ants_in_range(enemy_ants, group_distance)
        group_set = []
        while len(open_set) > 0:
            ant_loc = open_set.pop()
            group_i = 0
            zone_ants = [ant_loc]
            while len(zone_ants) > group_i:
                nearby_ants = [ant for ant in open_set 
                    if self.euclidean_distance2(zone_ants[group_i], ant) <= group_distance]
                open_set = [ant for ant in open_set if ant not in nearby_ants]
                zone_ants.extend(nearby_ants)
                group_i += 1
            
            group_set.append(([ant for ant in zone_ants if self.ant_list[ant][0] == MY_ANT], 
                [ant for ant in zone_ants if self.ant_list[ant][0] != MY_ANT]))

        #logging.debug('get_combat_zones, group_set = %s' % (str(group_set)))
        
        return group_set
        
    def get_fighter_groups(self):
        'get all my fighter ants in groups'
        group_distance = self.euclidean_distance_add(self.attackradius2, 2)
        enemy_ants = [ant_loc for ant_loc, owner in self.enemy_ants()]
        open_fighters = self.bfs(enemy_ants, group_distance, 
            lambda loc : self.map[loc[0]][loc[1]] == MY_ANT and self.ant_list[loc][1] == False)
            
        fighter_groups = []
        while len(open_fighters) > 0:
            first_ant = open_fighters.pop()
            group = [first_ant]
            group_i = 0
            while len(group) > group_i:
                friends = [ant for ant in open_fighters if self.euclidean_distance2(group[group_i], ant) < self.attackradius2]
                group.extend(friends)
                open_fighters = [ant for ant in open_fighters if ant not in friends]
                group_i += 1
                
            fighter_groups.append(group)
            
        return fighter_groups
    
    def get_group_formations(self, group):
        'get all possible formation of a group in a single turn'
        # special: ant indexes do not change, in other words, actual orders needed to get from 
        # group to full_result is just group[i] move to full_result[i]
        all_locs = [group[0]] + self.get_neighbour_locs(group[0])
        full_result = []
        if len(group) > 1:
            for sub_result in self.get_group_formations(group[1:]):
                for ant_loc in all_locs:
                    # no duplicate locations in each formation
                    if ant_loc in sub_result:
                        continue
                    full_result.append([ant_loc] + sub_result)
        else:
            full_result = [[ant_loc] for ant_loc in all_locs]
            
        return full_result
        
    def eval_formation(self, my_formation, enemy_formation):
        'return score, min_distance for the given my_formation/enemy_formation'
        # generate all pairs
        all_pairs = [(m, e) for m in my_formation for e in enemy_formation]
        # find the min_distance between our ants, using manhattan_distance for now
        # TODO: figure out if we can use euclidean distance, with a way to round distance 
        all_distances = [self.manhattan_distance(m,e) for m in my_formation for e in enemy_formation]
        min_distance = min(all_distances)
        # find out fighting pairs by getting all_pairs that has min_distance
        fighting_pairs = [all_pairs[i] for i,x in enumerate(all_distances) if x == min_distance]
        # create set (this ensures uniqueness)
        my_fighters = {}
        enemy_fighters = {}
        for m, e in fighting_pairs:
            my_fighters[m] = 1
            enemy_fighters[e] = 1
        
        return (len(my_fighters) - len(enemy_fighters), min_distance)
        
    def eval_formation_2(self, my_formation, enemy_formation):
        'return score, min_distance for the given my_formation/enemy_formation'
        fighting_pairs = [(m, e) for m in my_formation for e in enemy_formation if self.euclidean_distance2(m,e) <= self.attackradius2]
        my_fighters = {}
        enemy_fighters = {}
        for m, e in fighting_pairs:
            my_fighters[m] = 1
            enemy_fighters[e] = 1
        
        return len(my_fighters) - len(enemy_fighters)
    
    def get_best_formation_cohesion(self, formations):
        'return the formation with tightest group cohesion'
        cohesion_values = [self.get_formation_cohesion(f) for f in formations]
        return formations[cohesion_values.index(max(cohesion_values))]
        
    def get_formation_cohesion(self, formation):
        'return formation cohesion value, euclidean_distance2 < 3'
        value = 0
        for ant in formation:
            value += len([a for a in formation if self.euclidean_distance2(ant,a) < 3])
            
        return value
    
    def do_group_combat(self, group):
        'optimize for best cohesion'
        formations = self.get_group_formations(group)
        logging.debug('my_formations.count = %d, time_remaining = %s' % (len(formations), str(self.time_remaining())))
        best_formation = self.get_best_formation_cohesion(formations)
        logging.debug('finished finding best_formation, time_remaining = %s' % (str(self.time_remaining())))
        logging.debug('best_formation = %s' % (str(best_formation)))
        # issue orders
        for i in range(len(group)):	
            direction = self.direction(group[i], best_formation[i])
            self.issue_order((group[i], None if len(direction) == 0 else direction[0]))
    
    def do_zone_combat2(self, zone):
        'optimize best move for given combat_zone, which is (my_ants, enemy_ants)'
        #logging.debug('do_zone_combat.start = %s' % str(self.time_remaining()))
        my_group, enemy_group = zone
        my_formations = self.get_group_formations(my_group)
        # all_scores = []
        # for my_formation in my_formations:
            # score = self.eval_formation_2(my_formation, enemy_group)
            # all_scores.append(score)
            
        # best_score = max(all_scores)
        # logging.debug('best_score = %s' % str(best_score))
        
        #if all_scores.count(best_score) == 1 or best_score > 0:
        #    best_formation = my_formations[all_scores.index(best_score)]
        #else:
        #    # smallest best_score can ever be is 0, with eval_2 function, prefer cohesion
        #    valid_formations = [formation for i, formation in enumerate(my_formations) if all_scores[i] == best_score]
        #    best_formation = self.get_best_formation_cohesion(valid_formations)
        logging.debug('my_formations.count = %d, time_remaining = %s' % (len(my_formations), str(self.time_remaining())))
        best_formation = self.get_best_formation_cohesion(my_formations)
        logging.debug('finished finding best_formation, time_remaining = %s' % (str(self.time_remaining())))
            
        logging.debug('best_formation = %s' % (str(best_formation)))
        # issue orders
        for i in range(len(my_group)):	
            direction = self.direction(my_group[i], best_formation[i])
            self.issue_order((my_group[i], None if len(direction) == 0 else direction[0]))
        
        
    def do_zone_combat(self, zone):
        'optimize best move for given combat_zone, which is (my_ants, enemy_ants)'
        #logging.debug('do_zone_combat.start = %s' % str(self.time_remaining()))
        # - do 1-step permutation on my_group, and find the optimal formation:
        # - find euclidean distance of all enemy/my ant pairs, only keep the pairs with smallest distance
        # - count distinct enemy_ant_count and my_ant_count
        # - score = my_ant_count - enemy_ant_count, bigger is preferable
        # - in case of same score, do the following:
        #       if score > 0: prefer smaller distance
        #       if score < 0: prefer largest distance
        #       if score == 0: prefer smallest distance larger than attack_radius + 1, else largest distance
        my_group, enemy_group = zone
        my_formations = self.get_group_formations(my_group)
        all_scores = []
        all_min_dist = []
        i = 0
        logging.debug('my_formations.count = %d, time_remaining = %s' % (len(my_formations), str(self.time_remaining())))
        for my_formation in my_formations:
            score, min_dist = self.eval_formation(my_formation, enemy_group)
            all_scores.append(score)
            all_min_dist.append(min_dist)
        logging.debug('finished calculating best_score, time_remaining = %s' % (str(self.time_remaining())))
            
        best_score = max(all_scores)
        logging.debug('best_score = %s' % str(best_score))
        # logging.debug('my_formations = %s' % str(my_formations))
        # logging.debug('all_scores = %s' % str(all_scores))
        # logging.debug('all_min_dist = %s' % str(all_min_dist))
        
        if all_scores.count(best_score) == 1:
            best_formation = my_formations[all_scores.index(best_score)]
        else:
            best_score_indexes = [i for i,x in enumerate(all_scores) if x == best_score]
            valid_best_distances = [dist for i, dist in enumerate(all_min_dist) if i in best_score_indexes]
            if best_score > 0:
                best_distance = min(valid_best_distances)
            elif best_score < 0:
                best_distance = max(valid_best_distances)
            else:
                safe_distances = [distance for distance in valid_best_distances 
                    if distance > self.euclidean_distance_add(self.attackradius2, 2)]
                logging.debug('safe_distances = %s' % (str(safe_distances)))
                if len(safe_distances) > 0:
                    best_distance = min(valid_best_distances)
                else:
                    best_distance = max(valid_best_distances)
            best_formation = my_formations[all_min_dist.index(best_distance)]
            
        logging.debug('best_formation = %s' % (str(best_formation)))
        # issue orders
        for i in range(len(my_group)):	
            direction = self.direction(my_group[i], best_formation[i])
            self.issue_order((my_group[i], None if len(direction) == 0 else direction[0]))
        
    def render_text_map(self):
        'return a pretty string representing the map'
        tmp = ''
        for row in self.map:
            tmp += '# %s\n' % ''.join([MAP_RENDER[col] for col in row])
        return tmp

    # static methods are not tied to a class and don't have self passed in
    # this is a python decorator
    @staticmethod
    def run(bot):
        'parse input, update game state and call the bot classes do_turn method'
        ants = Ants()
        map_data = ''
        while(True):
            try:
                current_line = sys.stdin.readline().rstrip('\r\n') # string new line char
                if current_line.lower() == 'ready':
                    ants.setup(map_data)
                    bot.do_setup(ants)
                    ants.finish_turn()
                    map_data = ''
                elif current_line.lower() == 'go':
                    ants.update(map_data)
                    # call the do_turn method of the class passed in
                    bot.do_turn(ants)
                    ants.finish_turn()
                    map_data = ''
                else:
                    map_data += current_line + '\n'
            except EOFError:
                break
            except KeyboardInterrupt:
                raise
            except:
                # don't raise error or return so that bot attempts to stay alive
                traceback.print_exc(file=sys.stderr)
                sys.stderr.flush()