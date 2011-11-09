
# planner.py: strategic planner, aka all-knowing-hive-mind
#
# AI bot written for AI Challenge 2011 - Ants
# Author: Bill Y
# License: all your base are belong to us

from core import logging, ALL_DIRECTIONS, BEHIND
from collections import deque
import math

class Planner():    
    def __init__(self, gamestate):
        self.gamestate = gamestate
        self.enemy_hill_value = -10.0
        self.my_hill_value = 0.0
        self.food_value = -0.5
        self.my_fighter_value = -1.0
        self.my_explorer_value = 2.0
        self.enemy_ant_value = -3.0
    
    def do_strategy_plan(self, influence):
        'called every turn to do planning'
        self.update_task_influence(influence)
        self.update_general_influence(influence)
        
    def update_general_influence(self, influence):
        'update influence map with goals found on gamestate'
        for food_loc in self.gamestate.food_list:
            influence.set_value(food_loc, 3, self.food_value)
        
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
        pass
        # assess situation
        my_tiles = [loc for loc in influence.map if math.fabs(influence.map[loc]) > 0.01]
        total_tile_count = self.gamestate.cols * self.gamestate.rows
        logging.debug('currently owning %d in %d tiles, ratio: %f' % 
            (len(my_tiles), total_tile_count, float(len(my_tiles))/total_tile_count))
        logging.debug('my ant_hill is at %s' % str(self.gamestate.my_hills()))
        logging.debug('known enemy hill: %s' % str(self.gamestate.enemy_hills()))
        # if winning 
        # if losing
        # unsure
    