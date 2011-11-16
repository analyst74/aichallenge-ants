# planner.py: strategic planner, aka all-knowing-hive-mind
#
# AI bot written for AI Challenge 2011 - Ants
# Author: Bill Y
# License: all your base are belong to us

from core import logging, ALL_DIRECTIONS, BEHIND
from collections import deque
from influence3 import Influence
import math, path

class Planner():    
    def __init__(self, gamestate):
        self.gamestate = gamestate
        self.enemy_hill_value = -20
        self.my_hill_value = 0
        self.food_value = -0.5
        self.my_fighter_value = -1
        self.my_explorer_value = 1
        self.enemy_ant_value = 0
        self.enemy_ninja_value = -5
        self.route_task = None
        self.winning_percentage = 0.0
        
    def do_strategy_plan(self, influence):
        'called every turn to do planning'
        self.update_task_influence(influence)
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

    def do_task(self, influence):
        'execute all the tasks'
        if self.route_task is not None:
            route, target_inf_value = self.route_task
            if influence.map[route[0]] > target_inf_value:
                self.route_task = None
            else:
                if route[0] in self.gamestate.my_unmoved_ants():
                    self.gamestate.move_away(route[0], route[1])
                for i in range(1, len(route)):
                    if route[i] in self.gamestate.my_unmoved_ants():
                        directions = []
                        if self.gamestate.is_passable(route[i-1]):
                            directions = self.gamestate.direction(route[i], route[i-1])
                        if len(directions) > 0:
                            self.gamestate.issue_order((route[i], directions[0]))
            
    def update_task_influence(self, influence):
        'update dynamic goal values depending on current situation'
        # assess situation
        my_tiles = [loc for loc in influence.map if math.fabs(influence.map[loc]) > 0.01]
        total_tile_count = self.gamestate.cols * self.gamestate.rows
        self.winning_percentage = float(len(my_tiles))/total_tile_count
        logging.debug('currently owning %d in %d tiles, ratio: %f' % 
			(len(my_tiles), total_tile_count, self.winning_percentage))
        logging.debug('my ant_hill is at %s' % str(self.gamestate.my_hills()))
        logging.debug('known enemy hill: %s' % str(self.gamestate.enemy_hills()))
        
        # alter aggressiveness as situation changes
        self.my_fighter_value = 0 - 1 - (self.winning_percentage / 0.3 % 1)
        self.enemy_ant_value = 0 - (self.winning_percentage / 0.3 % 1) * 2
        
        # hill defense
        if len(self.gamestate.my_hills()) == 1:
            my_hill = self.gamestate.my_hills()[0]
            for enemy_ninja in [ant for ant, owner in self.gamestate.enemy_ants() if self.gamestate.manhattan_distance(my_hill, ant) < 8]:
                influence.map[my_hill] += self.enemy_ninja_value
        
        ## create route task
        # find area with highest ant density
        high_dense_loc = max(influence.map, key=influence.map.get)
        high_dense_val = influence.map[high_dense_loc]
        # find closest desirable area using bfs
        route = path.bfs_findtask(self.gamestate, influence, high_dense_loc, 500)
        # setup task, only long distance ones count
        if len(route) > 8:
            self.route_task = (route, high_dense_val)
            
        logging.debug('found route_task: %s' % str(self.route_task))
