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

class Planner():
    def __init__(self, gamestate):
        self.gamestate = gamestate
        self.enemy_hill_value = -PLANNER_SCALE * 100
        self.my_hill_value = 0
        self.food_value = -PLANNER_SCALE * 2
        self.my_fighter_value = -PLANNER_SCALE * 0.5
        self.my_explorer_value = PLANNER_SCALE
        self.enemy_ant_value = 0
        self.enemy_ninja_value = -PLANNER_SCALE * 5
        self.winning_percentage = 0.0
        self.task_locations = []
        
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

    def update_task_influence(self, influence):
        'update dynamic goal values depending on current situation'
        # assess situation
        my_tile_count = len([v for v in np.ravel(np.fabs(influence.map)) if v > 0.01])
        total_tile_count = self.gamestate.cols * self.gamestate.rows
        self.winning_percentage = float(my_tile_count)/total_tile_count
        logging.debug('currently owning %d in %d tiles, ratio: %f' % 
            (my_tile_count, total_tile_count, self.winning_percentage))
        logging.debug('my ant_hill is at %s' % str(self.gamestate.my_hills()))
        logging.debug('known enemy hill: %s' % str(self.gamestate.enemy_hills()))
        
        # alter aggressiveness as situation changes
        self.my_fighter_value = 0 - 1 - (self.winning_percentage / 0.3 % 1)
        self.enemy_ant_value = 0 - (self.winning_percentage / 0.3 % 1) * 2
        
        # hill defense
        if len(self.gamestate.my_hills()) == 1:
            my_hill = self.gamestate.my_hills()[0]
            for enemy_ninja in [ant for ant, owner in self.gamestate.enemy_ants() if self.gamestate.manhattan_distance(my_hill, ant) < 10]:
                influence.map[enemy_ninja] += self.enemy_ninja_value
        
