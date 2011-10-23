#!/usr/bin/env python
from ants import *
from random import choice

EXPLORE_RADIUS = 5

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
        self.issue_raze_task(ants)
        self.issue_gather_task(ants)
        self.issue_explore_task(ants)

    def issue_gather_task(self, ants):
        'gather food'
        for food_loc in ants.food_list:
            closest_ant = ants.find_closest_ant(food_loc)
            logging.debug('closest_ant is ' + str(closest_ant))
            if closest_ant is not None:
                ants.issue_order(closest_ant)
    
    def issue_raze_task(self, ants):
        'raze enemy hill'
        # send 20% of total ants to attack
        attack_amount = int(len(ants.ant_list) / 5)
        for hill_loc, owner in ants.enemy_hills():
            for i in range(attack_amount):
                closest_ant = ants.find_closest_ant(hill_loc, 500)
                if closest_ant is not None:
                    ants.issue_order(closest_ant)
                else:
                    # if we are short on ants, focus on only one
                    # let the rest enemy hills live for a bit
                    return 
        
    def issue_explore_task(self, ants):
        'explore map'
        # loop through all my un-moved ants and set them to explore
        # the ant_loc is an ant location tuple in (row, col) form
        for ant_loc in ants.my_unmoved_ants():
            #pdb.set_trace()
            # try to move away from empire_center
            logging.debug('ant_loc ' + str(ant_loc))
            directions = ants.passable_directions(ant_loc)
            logging.debug('directions ' + str(directions))
            new_locs = [ants.destination(ant_loc, d) for d in directions]
            logging.debug('new_locs ' + str(new_locs))
            min_val = sys.maxsize
            best_direction = []
            for (row, col) in new_locs:
                if min_val > ants.beaten_path[row][col]:
                    min_val = ants.beaten_path[row][col]
                    best_new_loc = (row, col)
                    best_direction = ants.direction(ant_loc, best_new_loc)
            if len(best_direction) > 0:
                ants.issue_order((ant_loc, choice(best_direction)))
            
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
