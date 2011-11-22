# planner3.py: strategic planner, aka all-knowing-hive-mind, accomodating multi-level influence
#
# AI bot written for AI Challenge 2011 - Ants
# Author: Bill Y
# License: all your base are belong to us

from core import debug_logger, ALL_DIRECTIONS, BEHIND, CUTOFF, EXPLORE_GAP
#from influence5 import Influence
import math, path, numpy as np

class Planner():
    def __init__(self, gamestate):
        self.gamestate = gamestate
        self.enemy_hill_value = -30
        self.my_hill_value = -15
        self.food_value = -10
        self.my_fighter_value = - 0.5
        self.my_explorer_value = 1
        self.enemy_ant_value = 0
                
    def update_food_influence(self, food_influence):
        influence_sources = [(loc, self.food_value) for loc in self.gamestate.food_list]
        food_influence.set_influence(influence_sources, lambda loc: loc in self.gamestate.my_unmoved_ants())
        
    def update_raze_influence(self, raze_influence):
        influence_sources = [(loc, self.enemy_hill_value) for loc, owner in self.gamestate.enemy_hills()]
        raze_influence.set_influence(influence_sources, None)
        
    def update_defense_influence(self, defense_influence):
        # ignore multi-hill situation, go all out in multi-maze 
        # also, we can't defend when there is no hill...
        influence_sources = []
        my_hill = None
        if len(self.gamestate.my_hills()) == 1:
            my_hill = self.gamestate.my_hills()[0]
            all_invaders = [ant for ant, owner in self.gamestate.enemy_ants() 
                            if self.gamestate.manhattan_distance(my_hill, ant) < 15]
            for invader in all_invaders:
                defense_value = self.my_hill_value
                influence_sources.append((invader, defense_value))
            # if len(all_invaders) > 0:
                # defense_value = self.my_hill_value if len(all_invaders) < 4 else self.my_hill_value * 2     
                # influence_sources = [(my_hill, defense_value)]
        defense_influence.set_influence(influence_sources, None)
        # special for defense, we want to make the hill less desirable, so it doesn't get blocked
        if my_hill is not None:
            defense_influence.map[my_hill] = 0
        
    def update_explore_influence(self, explore_influence):
        # my explorers
        for ant_loc in [ant for ant in self.gamestate.my_ants() 
                        if ant not in self.gamestate.my_fighters] :
            neighbour_ants = [ant for ant in self.gamestate.neighbour_table[ant_loc] if ant in self.gamestate.ant_list]
            explore_influence.map[ant_loc] +=  self.my_explorer_value * (len(neighbour_ants) + 1)
        # my fighters
        debug_logger.debug('update_explore_influence setting my fighters: %s' % str(self.gamestate.my_fighters))
        for ant_loc in self.gamestate.my_fighters:
            explore_influence.map[ant_loc] += self.my_fighter_value
        

    def update_aggressiveness(self, influence):
        'update dynamic goal values depending on current situation'
        # assess situation
        my_tile_count = len([v for v in np.ravel(np.fabs(influence.map)) if v > 0.01])
        total_tile_count = self.gamestate.cols * self.gamestate.rows
        self.gamestate.winning_percentage = float(my_tile_count)/total_tile_count
        debug_logger.debug('currently owning %d in %d tiles, ratio: %f' % 
            (my_tile_count, total_tile_count, self.gamestate.winning_percentage))
        debug_logger.debug('my ant_hill is at %s' % str(self.gamestate.my_hills()))
        debug_logger.debug('known enemy hill: %s' % str(self.gamestate.enemy_hills()))
        
        # alter aggressiveness as situation changes
        self.my_fighter_value = 0 - 1 - (self.gamestate.winning_percentage / 0.3 % 1)
        self.enemy_ant_value = 0 - (self.gamestate.winning_percentage / 0.3 % 1) * 2
