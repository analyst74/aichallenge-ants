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
            ant_order = ants.find_closest_ant_order(food_loc, 20)
            logging.debug('issue_gather_task for food %s, time_remaining %s ' % (str(food_loc), str(ants.time_remaining())))
            if ant_order is not None:
                ants.issue_order(ant_order)
    
    def issue_combat_task(self, ants):
        'combat logic'
        logging.debug('ants.time_remaining().start = ' + str(ants.time_remaining())) 
        for ant_loc in ants.my_unmoved_ants():
            # some of the previously unmoved ants might have been moved            
            if ant_loc not in ants.ant_list:
                continue
            owner, moved = ants.ant_list[ant_loc]
            if moved:
                continue
                
            threat_level = ants.calc_threat_level(ant_loc)
            if threat_level > 0:
                logging.debug('combat_task for %s' % str(ant_loc))
                logging.debug('threat_level = ' + str(threat_level))
                logging.debug('ants.time_remaining().stage 2 = ' + str(ants.time_remaining())) 
                
            # 0 means no enemy nearby
            if threat_level >= 1:
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
                if len(retreat_directions) > 0:
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
                if len(attack_directions) > 0:
                    ants.issue_order((ant_loc, choice(attack_directions)))

            # common combat logic
            if threat_level > 0:
                logging.debug('ants.time_remaining().stage 3 = ' + str(ants.time_remaining()))                
                # set ant to moved state, prevent being picked up by explorer
                ants.ant_list[ant_loc] = (MY_ANT, True)
                # call for help, gang bang time!
                for i in range(5): # right now it only looks for 5 max helpers
                    ant_order = ants.find_closest_ant_order(ant_loc, 100)
                    if ant_order is not None:
                        ants.issue_order(ant_order)
                        logging.debug('calling help from %s, to %s ' % (str(ant_order), str(ant_loc)))
                    else:
                        break
                logging.debug('ants.time_remaining().stage 4 = ' + str(ants.time_remaining()))    
                
    def issue_raze_task(self, ants):
        'raze enemy hill'
        # send 20% of total ants to attack
        attack_amount = int(len(ants.ant_list) / 5)
        for hill_loc, owner in ants.enemy_hills():
            leader_order = ants.find_closest_ant_order(hill_loc, 300)
            logging.debug('issue_raze_task for %s' % str(hill_loc))
            logging.debug('leader_order = %s' % str(leader_order))
            logging.debug('ants.time_remaining() = ' + str(ants.time_remaining()))    
            if leader_order is not None:
                ants.issue_order(leader_order)                # call nearby ants to follow
                leader_loc, leader_direction = leader_order
                for i in range(attack_amount):
                    militia_order = ants.find_closest_ant_order(leader_loc, 100)
                    if militia_order is not None:
                        ants.issue_order(militia_order)
                    else:
                        # if no ants are nearby, move onto next hill
                        break 
        
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
