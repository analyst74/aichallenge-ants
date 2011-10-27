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
        # if a hill is really close, do it first before all other task
        self.issue_raze_task(ants, 5)
        self.issue_gather_task(ants)
        logging.debug('after gather task: self.ant_list = %s' % str(ants.ant_list))
        self.issue_combat_task(ants)
        self.issue_raze_task(ants, 300)
        self.issue_explore_task(ants)

    def issue_gather_task(self, ants):
        'gather food'
        # optimize food search in earlier rounds
        marginal_limit = max(1, len(ants.food_list))
        search_limit = max(20, int(200 / marginal_limit))
        for food_loc in ants.food_list:            
            ants.move_to_spot(food_loc, 1, search_limit)
            logging.debug('issue_gather_task for food %s, time_remaining %s ' % (str(food_loc), str(ants.time_remaining())))
    
    def issue_combat_task(self, ants):
        'combat logic'
        logging.debug('issue_combat_task.start = ' + str(ants.time_remaining())) 
        for ant_loc in ants.my_unmoved_ants():
            # some of the previously unmoved ants might have been moved            
            if ant_loc not in ants.ant_list:
                continue
            owner, moved = ants.ant_list[ant_loc]
            if moved:
                continue
                
            (threat_level, friendly_direction, enemy_direction) = ants.calc_threat_level(ant_loc)
            if threat_level > 0:
                logging.debug('combat_task for %s' % str(ant_loc))
                logging.debug('threat_level = ' + str(threat_level))
                logging.debug('ants.time_remaining().stage 2 = ' + str(ants.time_remaining())) 
                
            # 0 means no enemy nearby
            if threat_level >= 1:
                logging.debug('retreating from %s to %s ' % (str(ant_loc), friendly_direction))
                ants.issue_order((ant_loc, BEHIND[enemy_direction]))
                ants.move_to_spot(ant_loc, 5, 100)
            elif threat_level > 0 and threat_level < 1:
                logging.debug('attacking from %s to %s ' % (str(ant_loc), enemy_direction))
                #ants.issue_order((ant_loc, enemy_direction))
                ants.flock_attack(ant_loc, enemy_direction, 20)
            #elif threat_level == 1:                     
            #    # set ant to stationary, wait for better opportunity
            #    ants.issue_order((ant_loc, None))
            #    # call for help, gang bang time!
            #    ants.move_to_spot(ants.destination(ant_loc, enemy_direction), 5, 100)
            
            # check if we still have time left to calculate more orders
            logging.debug('ants.time_remaining() = ' + str(ants.time_remaining()))    
            if ants.time_remaining() < 100:
                break
                
        logging.debug('issue_combat_task.finish = ' + str(ants.time_remaining())) 
        
    def issue_raze_task(self, ants, leader_range):
        'raze enemy hill'
        # send 20% of total ants to attack
        logging.debug('raze.start = ' + str(ants.time_remaining())) 
        max_malitia = int(len(ants.ant_list) / 5)
        for hill_loc, owner in ants.enemy_hills():
            logging.debug('issue_raze_task for %s' % str(hill_loc))
            leader_loc = ants.move_to_spot(hill_loc, 1, leader_range)
            logging.debug('leader_loc = %s' % str(leader_loc))
            logging.debug('ants.time_remaining() = ' + str(ants.time_remaining()))
            # mobilizing militia
            if leader_loc is not None:
                ants.move_to_spot(leader_loc, max_malitia, 100)
        logging.debug('raze.finish = ' + str(ants.time_remaining())) 
        
    def issue_explore_task(self, ants):
        'explore map'
        # loop through all my un-moved ants and set them to explore
        # the ant_loc is an ant location tuple in (row, col) form
        for ant_loc in ants.my_unmoved_ants():
            logging.debug('issue_explore_task for %s' % str(ant_loc))
            min_val = sys.maxsize
            best_directions = []
            for cur_direction in ants.passable_directions(ant_loc):
                # 2 levels, so the ant can "see" further
                (row,col) = ants.destination(ants.destination(ant_loc, cur_direction), cur_direction)
                # calculate new_locs plus its surrounding location score
                cur_val = ants.beaten_path[row][col]
                new_directions = ants.passable_directions((row,col))
                for (adj_row, adj_col) in [ants.destination((row,col), d) for d in new_directions]:
                    cur_val += ants.beaten_path[adj_row][adj_col]
                # then normalize it
                cur_val = cur_val / (len(new_directions) + 1)
                
                if min_val > cur_val:
                    min_val = cur_val
                    best_new_loc = (row, col)
                    best_directions = [cur_direction]
                elif min_val == cur_val:
                    best_directions.append(cur_direction)
            if len(best_directions) > 0:
                ants.issue_order((ant_loc, choice(best_directions)))
            
            # check if we still have time left to calculate more orders
            logging.debug('ants.time_remaining() = ' + str(ants.time_remaining()))    
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
