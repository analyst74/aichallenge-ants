# MyBot.py: main program, required by contest
#
# AI bot written for AI Challenge 2011 - Ants
# Author: Bill Y
# License: all your base are belong to us

from core import *
from gamestate import GameState
from influence import Influence
from planner import Planner
from combat import battle_line as battle
from random import choice
import traceback

import sys, os, pickle

DETAIL_LOG = False

# define a class with a do_turn method
# the Gamestate.run method will parse and update bot input
# it will also run the do_turn method for us
class MyBot:
    def __init__(self, gamestate):
        # define class level variables, will be remembered between turns
        self.gamestate = gamestate
        self.planner_time = gamestate.turntime / 2
    
    # do_setup is run once at the start of the game
    # after the bot has received the game settings
    def do_setup(self):
        # initialize data structures after learning the game settings
        self.strat_influence = Influence(self.gamestate, STRAT_DECAY)
        self.planner = Planner(self.gamestate, self.strat_influence)
    
    def log_turn(self, turn_no):
        if DETAIL_LOG and os.path.isdir('pickle'):
            # dump gamestate
            pickle_file = open('pickle/turn_' + str(self.gamestate.current_turn) + '.gamestate', 'wb')
            pickle.dump(self.gamestate, pickle_file)
            pickle_file.close()
            
            # dump influence map value
            pickle_file = open('pickle/turn_' + str(self.gamestate.current_turn) + '.influence', 'wb')
            pickle.dump(self.strat_influence, pickle_file)
            pickle_file.close()
    
    # do turn is run once per turn
    def do_turn(self):
        logging.debug('turn ' + str(self.gamestate.current_turn))
        
        # detailed logging
        self.log_turn(self.gamestate.current_turn)
        
        # handle combat
        self.issue_combat_task()
        
        plan_start = self.gamestate.time_remaining()
        # decay strategy influence
        logging.debug('strat_influence.decay().start = %s' % str(self.gamestate.time_remaining())) 
        self.strat_influence.decay()
        logging.debug('strat_influence.decay().finish = %s' % str(self.gamestate.time_remaining())) 
        # use planner to set new influence
        self.planner.do_plan()
        plan_duration = plan_start - self.gamestate.time_remaining()
        self.planner_time = max([plan_duration, self.planner_time])
        
        # diffuse strategy influence
        logging.debug('strat_influence.diffuse().start = %s' % str(self.gamestate.time_remaining())) 
        for i in xrange(3):
            self.strat_influence.diffuse()
            if self.gamestate.time_remaining() < self.planner_time + 50:
                logging.debug('stopped diffuse after %d times' % i)
                break
        logging.debug('strat_influence.diffuse().finish = %s' % str(self.gamestate.time_remaining())) 

        # handle explorer
        self.issue_explore_task()
        logging.debug('endturn: ant_count = %d, time_elapsed = %s' % (len(self.gamestate.ant_list), self.gamestate.time_elapsed()))

    def issue_combat_task(self):
        'combat logic'
        logging.debug('issue_combat_task.start = %s' % str(self.gamestate.time_remaining())) 
        zones = battle.get_combat_zones(self.gamestate)
        
        logging.debug('zones = %s' % str(zones))
        for zone in zones:
            logging.debug('group combat loop for = %s' % str(zone))
            if len(zone[0]) > 0:
                battle.do_zone_combat(self.gamestate, zone)
            
            # check if we still have time left to calculate more orders
            if self.gamestate.time_remaining() < self.planner_time + 50:
                break
                
        logging.debug('issue_combat_task.finish = ' + str(self.gamestate.time_remaining())) 
        
    def issue_explore_task(self):
        'explore map'
        logging.debug('issue_explore_task.start = %s' % str(self.gamestate.time_remaining())) 
        # loop through all my un-moved ants and set them to explore
        # the ant_loc is an ant location tuple in (row, col) form
        for cur_loc in self.gamestate.my_unmoved_ants():
            all_locs = [cur_loc] + [self.gamestate.destination(cur_loc, d) 
                                    for d in self.gamestate.passable_directions(cur_loc)]
            loc_influences = [self.strat_influence.map[loc] for loc in all_locs]
            best_directions = self.gamestate.direction(cur_loc, all_locs[loc_influences.index(min(loc_influences))])
            if len(best_directions) > 0:
                self.gamestate.issue_order((cur_loc, choice(best_directions)))
            
            # check if we still have time left to calculate more orders
            if self.gamestate.time_remaining() < 10:
                break
        logging.debug('issue_explore_task.finish = ' + str(self.gamestate.time_remaining())) 


    # static methods are not tied to a class and don't have self passed in
    # this is a python decorator
    @staticmethod
    def run():
        'parse input, update game state and call the bot classes do_turn method'
        gamestate = GameState()
        bot = MyBot(gamestate)
        map_data = ''
        while(True):
            try:
                current_line = sys.stdin.readline().rstrip('\r\n') # string new line char
                if current_line.lower() == 'ready':
                    gamestate.setup(map_data)
                    bot.do_setup()
                    gamestate.finish_turn()
                    map_data = ''
                elif current_line.lower() == 'go':
                    gamestate.update(map_data)
                    # call the do_turn method of the class passed in
                    bot.do_turn()
                    gamestate.finish_turn()
                    map_data = ''
                else:
                    map_data += current_line + '\n'
            except EOFError:
                break
            except KeyboardInterrupt:
                raise
            except:
                # don't raise error or return so that bot attempts to stay alive
                traceback.print_exc(file=sys.stderr)
                sys.stderr.flush()
                
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
        MyBot.run()
    except KeyboardInterrupt:
        print('ctrl-c, leaving ...')
