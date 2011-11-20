# planner.py: strategic planner, aka all-knowing-hive-mind
#
# AI bot written for AI Challenge 2011 - Ants
# Author: Bill Y
# License: all your base are belong to us

from core import logging, ALL_DIRECTIONS, BEHIND, CUTOFF, EXPLORE_GAP
from collections import deque
from influence5 import Influence
import math, path, numpy as np

PLANNER_SCALE = 1
PRIORITY_HILL_DEFENSE = 10
PRIORITY_HILL_RAZE = 10

class Planner():
    def __init__(self, gamestate):
        self.gamestate = gamestate
        self.enemy_hill_value = -PLANNER_SCALE * 100
        self.my_hill_value = 0
        self.food_value = -PLANNER_SCALE * 2
        self.my_fighter_value = -PLANNER_SCALE * 0.5
        self.my_explorer_value = PLANNER_SCALE
        self.enemy_ant_value = 0
        self.enemy_ninja_value = -PLANNER_SCALE * 10
        # TODO: do we need multiple strategy tasks? like strategy task is (priority, target, map)
        self.strat_route = None
        self.strat_map = None
        
    def do_strategy_plan(self, influence):
        'called every turn to do planning'
        self.update_strategy_influence(influence)
        self.update_general_influence(influence)
        
    def update_general_influence(self, influence):
        'update influence map with goals found on gamestate'
        for food_loc in self.gamestate.food_list:
            influence.map[food_loc] += self.food_value
        
        # my explorers
        for ant_loc in [ant for ant in self.gamestate.my_ants() 
                        if ant not in self.gamestate.my_fighters] :
            neighbour_ants = [ant for ant in self.gamestate.neighbour_table[ant_loc] if ant in self.gamestate.ant_list]
            influence.map[ant_loc] +=  self.my_explorer_value * (len(neighbour_ants) + 1)        
        # my fighters
        for ant_loc in self.gamestate.my_fighters:
            influence.map[ant_loc] += self.my_fighter_value
        # enemy ants
        for ant_loc, owner in self.gamestate.enemy_ants():
            influence.map[ant_loc] += self.enemy_ant_value
        # my hill
        for hill_loc in self.gamestate.my_hills():
            influence.map[hill_loc] += self.my_hill_value
        # enemy hill
        for hill_loc, owner in self.gamestate.enemy_hills():
            influence.map[hill_loc] += self.enemy_hill_value

    def update_strategy_influence(self, influence):
        'update dynamic goal values depending on current situation'
        # assess situation
        my_tile_count = len([v for v in np.ravel(np.fabs(influence.map)) if v > 0.01])
        total_tile_count = self.gamestate.cols * self.gamestate.rows
        self.gamestate.winning_percentage = float(my_tile_count)/total_tile_count
        logging.debug('currently owning %d in %d tiles, ratio: %f' % 
            (my_tile_count, total_tile_count, self.gamestate.winning_percentage))
        logging.debug('my ant_hill is at %s' % str(self.gamestate.my_hills()))
        logging.debug('known enemy hill: %s' % str(self.gamestate.enemy_hills()))
        
        # alter aggressiveness as situation changes
        self.my_fighter_value = 0 - 1 - (self.gamestate.winning_percentage / 0.3 % 1)
        self.enemy_ant_value = 0 - (self.gamestate.winning_percentage / 0.3 % 1) * 2
        
        # hill defense against ninja
        if len(self.gamestate.my_hills()) == 1:
            my_hill = self.gamestate.my_hills()[0]
            for enemy_ninja in [ant for ant, owner in self.gamestate.enemy_ants() 
                                if self.gamestate.manhattan_distance(my_hill, ant) < 10]:
                # send ants to intercept, this will cause ant on ther far side of hill also *get* it
                interception_loc = tuple([x - (x - y)/2 for x, y in zip(my_hill, enemy_ninja)])
                influence.map[interception_loc] += self.enemy_ninja_value
        
    def do_special_task(self):
        # hill defense against serious invasion
        if len(self.gamestate.my_hills()) == 1:
            my_hill = self.gamestate.my_hills()[0]
            invasion_count = len([ant for ant, owner in self.gamestate.enemy_ants() 
                                if self.gamestate.manhattan_distance(my_hill, ant) < 15])
            if invasion_count > 5:
                for my_ant in [ant for ant in self.gamestate.my_unmoved_ants()
                                if self.gamestate.manhattan_distance(my_hill, ant) < 10]:
                    self.gamestate.move_toward(my_ant, my_hill)
                    
    def do_strategic_movement(self, influence_map):
        'move ants by previously established route'
        logging.debug('do_strategic_movement start: %s' % str(self.gamestate.time_remaining())) 
        self.create_strategic_movement(influence_map)
        if self.strat_map is not None:
            for my_ant in self.gamestate.my_unmoved_ants():
                if self.strat_map[my_ant] < 0:
                    logging.debug('found ant %s on the train' % str(my_ant))
                    moves = [my_ant] + self.gamestate.passable_neighbours(my_ant)
                    route_values = [self.strat_map[n_loc] for n_loc in moves]
                    sorted_move_and_value = sorted(zip(route_values, moves))
                    preferred_value, preferred_move = sorted_move_and_value[0]
                    # intentionally discount current spot, to let the ant fall off 
                    # the train when it gets too crowded
                    directions = self.gamestate.direction(my_ant, preferred_move)
                    if len(directions) > 0:
                        logging.debug('strategic move: %s => %s' % (str(my_ant), directions[0]))
                        self.gamestate.issue_order((my_ant, directions[0]))
                    
    def create_strategic_movement(self, influence_map):
        'route my ants in high concentration area to some desired targets'
        # if our ant concentration is getting low, don't do any task
        max_val = np.amax(influence_map)
        if max_val < 0.5:
            self.strat_map = None
            self.strat_route = None
            return
        # if there is no target 
        #   or our target has been achieved, get new route/strat map
        # otherwise, continue to expand the current one
        get_new_route = True
        existing_route = []
        if self.strat_route is not None:
            existing_route, target_loc = self.strat_route
            if target_loc not in self.gamestate.my_ants():
                get_new_route = False                
        
        if get_new_route:
            logging.debug('create_strategic_movement getting new route: %s' % str(self.gamestate.time_remaining())) 
            start_loc = np.unravel_index(influence_map.argmax(), influence_map.shape)
            initial_inf = -2
                    
            # try to attack enemy hill, if any
            enemy_hills = [hill_loc for hill_loc, owner in self.gamestate.enemy_hills()]
            if len(enemy_hills) > 0:
                target_loc = min(enemy_hills, key=lambda hill_loc: self.gamestate.manhattan_distance(start_loc, hill_loc))
            # TODO: instead, try to occupy closest un-occupied region
            # try to explore closest un-explored region
            else:
                start_region = (start_loc[0] / EXPLORE_GAP, start_loc[1] / EXPLORE_GAP)
                unexplored_regions = [(row, col) for row in range(self.gamestate.region_map.shape[0])
                                                for col in range(self.gamestate.region_map.shape[1])
                                                if self.gamestate.region_map[row,col] == 0]
                if len(unexplored_regions) > 0:
                    region_to_explore = min(unexplored_regions, key = lambda region: self.gamestate.manhattan_distance(start_region, region))
                    target_loc = (region_to_explore[0] * EXPLORE_GAP, region_to_explore[1] * EXPLORE_GAP)
        else:
            logging.debug('create_strategic_movement extend current route: %s' % str(self.gamestate.time_remaining())) 
            start_loc = existing_route[-1]
            initial_inf = self.strat_map[start_loc]
        
        # don't do anything if we've already calculated the full route
        if start_loc == target_loc:
            return 
        
        # get a route
        route = path.astar(self.gamestate, start_loc, target_loc, length_limit = 100)
        # traverse the route from start, create a linear hill-descending influence map
        new_strat_map = np.zeros((self.gamestate.rows, self.gamestate.cols))
        for i in xrange(len(route)):
            cur_val = -i - 2
            new_strat_map[route[i]] = cur_val
            # set un-discovered neighbours to current + 1
            neighbour_not_in_route = [loc for loc in self.gamestate.neighbour_table[route[i]]
                                    if loc not in self.gamestate.water_list]
            for n_loc in neighbour_not_in_route:
                new_strat_map[n_loc] = min(new_strat_map[n_loc], cur_val + 1)
        
        self.strat_route = (route, target_loc)
        self.strat_map = new_strat_map 
        
        logging.debug('turn %s, strategic move created, start=>target = %s => %s' % (str(self.gamestate.current_turn), str(start_loc), str(target_loc)))
        logging.debug(self.strat_route)