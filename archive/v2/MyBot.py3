#!/usr/bin/env python
from ants import *
from random import choice

# define a class with a do_turn method
# the Ants.run method will parse and update bot input
# it will also run the do_turn method for us
class MyBot:
    def __init__(self):
        # define class level variables, will be remembered between turns
        pass
    
    # do_setup is run once at the start of the game
    # after the bot has received the game settings
    # the ants class is created and setup by the Ants.run method
    def do_setup(self, ants):
        # initialize data structures after learning the game settings
        pass
    
    # do turn is run once per turn
    # the ants class has the game state and is updated by the Ants.run method
    # it also has several helper methods to use
    def do_turn(self, ants):
        logging.debug('turn ' + str(ants.current_turn))
        self.issue_gather_task(ants)
        self.issue_combat_task(ants)
        self.issue_raze_task(ants)
        self.issue_explore_task(ants)

    def issue_gather_task(self, ants):
        'gather food'
        for food_loc in ants.food_list:
            ant_order = ants.find_closest_ant_order(food_loc)
            if ant_order is not None:
                ants.issue_order(ant_order)
    
    def issue_combat_task(self, ants):
        'combat logic'
        for ant_loc in ants.my_unmoved_ants():
            threat_level = ants.calc_threat_level(ant_loc)
            # we do not deal with threat level = 1 or 0
            # 1 means we are of equal force, so whatever
            # 0 means no enemy nearby
            if threat_level > 1:
                retreat_directions = []
                lowest_level = sys.maxsize
                for d in ants.passable_directions(ant_loc):
                    d_loc = ants.destination(ant_loc, d)
                    d_threat_level = ants.calc_threat_level(d_loc)
                    if lowest_level > d_threat_level:
                        lowest_level = d_threat_level
                        retreat_directions = [d]
                    elif lowest_level == d_threat_level:
                        retreat_directions.append(d)
                if len(retreat_directions) == 0:
                    retreat_directions = ants.passable_directions(ant_loc)
                ants.issue_order((ant_loc, choice(retreat_directions)))
            elif threat_level > 0 and threat_level < 1:
                attack_directions = []
                highest_level = 0
                for d in ants.passable_directions(ant_loc):
                    d_loc = ants.destination(ant_loc, d)
                    d_threat_level = ants.calc_threat_level(d_loc)
                    if highest_level < d_threat_level:
                        highest_level = d_threat_level
                        attack_directions = [d]
                    elif highest_level == d_threat_level:
                        attack_directions.append(d)
                if len(attack_directions) == 0:
                    attack_directions = ants.passable_directions(ant_loc)
                ants.issue_order((ant_loc, choice(attack_directions)))
    
    def issue_raze_task(self, ants):
        'raze enemy hill'
        # send 20% of total ants to attack
        attack_amount = int(len(ants.ant_list) / 5)
        for hill_loc, owner in ants.enemy_hills():
            for i in range(attack_amount):
                ant_order = ants.find_closest_ant_order(hill_loc, 500)
                if ant_order is not None:
                    ants.issue_order(ant_order)
                else:
                    # if no ants are nearby, move onto next hill
                    break 
        
    def issue_explore_task(self, ants):
        'explore map'
        # loop through all my un-moved ants and set them to explore
        # the ant_loc is an ant location tuple in (row, col) form
        for ant_loc in ants.my_unmoved_ants():
            directions = ants.passable_directions(ant_loc)
            new_locs = [ants.destination(ant_loc, d) for d in directions]
            logging.debug('ant_loc = ' + str(ant_loc))
            logging.debug('new_locs = ' + str(new_locs))
            min_val = sys.maxsize
            best_directions = []
            for (row, col) in new_locs:
                logging.debug('beaten_path[' + str((row,col)) + '] = ' + str(ants.beaten_path[row][col]))
                if min_val > ants.beaten_path[row][col]:
                    min_val = ants.beaten_path[row][col]
                    best_new_loc = (row, col)
                    best_directions = ants.direction(ant_loc, best_new_loc)
                elif min_val == ants.beaten_path[row][col]:
                    best_directions += ants.direction(ant_loc, (row, col))
            if len(best_directions) > 0:
                logging.debug('best_direction = ' + str(best_directions))
                ants.issue_order((ant_loc, choice(best_directions)))
            
            # check if we still have time left to calculate more orders
            if ants.time_remaining() < 10:
                break
                
if __name__ == '__main__':
    # psyco will speed up python a little, but is not needed
    try:
        import psyco
        psyco.full()
    except ImportError:
        pass
    
    try:
        # if run is passed a class with a do_turn method, it will do the work
        # this is not needed, in which case you will need to write your own
        # parsing function and your own game state class
        Ants.run(MyBot())
    except KeyboardInterrupt:
        print('ctrl-c, leaving ...')
