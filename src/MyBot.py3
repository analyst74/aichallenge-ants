#!/usr/bin/env python
from ants import *

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
        self.issue_gather_task(ants)
        self.issue_explore_task(ants)

    # gather logic
    def issue_gather_task(self, ants):
        for food_loc in ants.food_list:
            closest_ant = ants.find_closest_ant(food_loc)
            logging.debug('closest_ant is ' + str(closest_ant))
            if closest_ant is not None:
                ants.issue_order(closest_ant)
                
        
    # explorer logic
    def issue_explore_task(self, ants):
        # loop through all my un-moved ants and set them to explore
        # the ant_loc is an ant location tuple in (row, col) form
        for ant_loc in ants.my_unmoved_ants():
            #pdb.set_trace()
            # try to move away from empire_center
            directions = ants.direction(ants.empire_center, ant_loc)
            logging.debug('directions(1) ' + ','.join(directions))
            directions += ants.passable_directions(ant_loc)
            logging.debug('directions(2) ' + ','.join(directions))            
            
            for direction in directions:
                # the destination method will wrap around the map properly
                # and give us a new (row, col) tuple
                new_loc = ants.destination(ant_loc, direction)
                
                # passable returns true if the location is valid move
                if (ants.passable(new_loc)):
                    # an order is the location of a current ant and a direction
                    ants.issue_order((ant_loc, direction))
                    # stop now, don't give multiple orders
                    break
            
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
