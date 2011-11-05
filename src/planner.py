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
        self.food_value = -5
        self.my_fighter_value = -2
        self.my_explorer_value = 2
        self.enemy_ant_value = -1
        
    def do_plan(self):
        'called every turn to do planning'
        self.update_goal_value()
        self.update_influence()
        
    def update_influence(self):
        'update influence map with goals found on gamestate'
        for food_loc in self.gamestate.food_list:
            self.strat_influence.map[food_loc] = self.food_value
        for hill_loc, owner in self.gamestate.enemy_hills():
            self.strat_influence.map[hill_loc] = self.enemy_hill_value
        # TODO: distinguish between my fighters and explorers
        for ant_loc in self.gamestate.my_ants():
            self.strat_influence.map[ant_loc] = self.my_explorer_value
            logging.debug('update_influence my_ants %s = %s' % (str(ant_loc), str(self.strat_influence.map[ant_loc])))
        for ant_loc, owner in self.gamestate.enemy_ants():
            self.strat_influence.map[ant_loc] = self.enemy_ant_value
        
    def update_goal_value(self):
        'update dynamic goal values depending on current situation'
        pass
        # assess situation
        # if winning 
        # if losing
        # unsure