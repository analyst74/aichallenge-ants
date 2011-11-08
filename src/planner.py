# planner.py: strategic planner, aka all-knowing-hive-mind
#
# AI bot written for AI Challenge 2011 - Ants
# Author: Bill Y
# License: all your base are belong to us

from core import logging

class Planner():    
    def __init__(self, gamestate, strat_influence):
        self.gamestate = gamestate
        self.strat_influence = strat_influence
        self.enemy_hill_value = -10
        self.food_value = -2
        self.my_fighter_value = -3
        self.my_explorer_value = 1
        self.enemy_ant_value = 0
        
    def do_plan(self):
        'called every turn to do planning'
        self.update_goal_value()
        self.update_influence()
        
    def update_influence(self):
        'update influence map with goals found on gamestate'
        for food_loc in self.gamestate.food_list:
            #self.strat_influence.map[food_loc] = self.food_value
            self.strat_influence.set_value(food_loc, 2, self.food_value)
        for hill_loc, owner in self.gamestate.enemy_hills():
            self.strat_influence.map[hill_loc] += self.enemy_hill_value
        # TODO: distinguish between my fighters and explorers
        for ant_loc in self.gamestate.my_ants():
            self.strat_influence.map[ant_loc] += self.my_explorer_value
        # override with fighter value
        for ant_loc in self.gamestate.my_fighters:
            self.strat_influence.map[ant_loc] += self.my_fighter_value
        for ant_loc, owner in self.gamestate.enemy_ants():
            self.strat_influence.map[ant_loc] += self.enemy_ant_value
        
    
        
    def update_goal_value(self):
        'update dynamic goal values depending on current situation'
        pass
        # assess situation
        my_tiles = [loc for loc in self.map if self.map[loc] > 0]
        total_tile_count = self.gamestate.cols * self.gamestate.rows
        logging.debug('currently owning %d in %d tiles, ratio: %f' % 
            (len(my_tiles), total_tile_count, my_tiles/total_tile_count))
        logging.debug('my ant_hill is at %s' % str(self.gamestate.my_hills()))
        # if winning 
        # if losing
        # unsure