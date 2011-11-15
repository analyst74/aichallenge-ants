# MyBot.py: main program, required by contest
#
# AI bot written for AI Challenge 2011 - Ants
# Author: Bill Y
# License: all your base are belong to us

from core import *
from gamestate import GameState
from influence5 import Influence
from planner2 import Planner
from random import choice
from collections import deque

import battle_line as battle
import sys, os, pickle, traceback, math

DETAIL_LOG = False

# define a class with a do_turn method
# the Gamestate.run method will parse and update bot input
# it will also run the do_turn method for us
class MyBot:
    def __init__(self, gamestate):
        # define class level variables, will be remembered between turns
        self.gamestate = gamestate
        self.diffuse_time = 0
        self.combat_time_history = deque([0, 0, 0, 0, 0])
        self.combat_time = 0
    
    # do_setup is run once at the start of the game
    # after the bot has received the game settings
    def do_setup(self):
        # initialize data structures after learning the game settings
        self.strat_influence = Influence(self.gamestate)
        self.planner = Planner(self.gamestate)
    
    def log_turn(self, turn_no):
        logging.debug('turn ' + str(self.gamestate.current_turn))
        logging.debug('self.diffuse_time = %d' % self.diffuse_time)
        logging.debug('self.combat_time_history = %s' % str(self.combat_time_history))
        logging.debug('self.combat_time = %s' % self.combat_time)
        # logging.debug('self.strat_influence.map over 0.01 count: %d' % 
            # len([key for key in self.strat_influence.map if math.fabs(self.strat_influence.map[key]) > 0.01]))
            
    def log_detail(self):
        if DETAIL_LOG and os.path.isdir('pickle'):# and int(self.gamestate.current_turn) % 10 == 0:
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
        # detailed logging
        self.log_turn(self.gamestate.current_turn)
        
        # decay strategy influence
        #logging.debug('strat_influence.decay().start = %s' % str(self.gamestate.time_remaining())) 
        self.strat_influence.decay(DECAY_RATE)
        #self.strat_influence = Influence(self.gamestate)
        #logging.debug('strat_influence.decay().finish = %s' % str(self.gamestate.time_remaining())) 
        # use planner to set new influence
        logging.debug('self.planner.do_strategy_plan.start = %s' % str(self.gamestate.time_remaining()))
        self.planner.do_strategy_plan(self.strat_influence)
        # for row in range(self.strat_influence.map.shape[0]):
            # for col in range(self.strat_influence.map.shape[1]):
                # if math.fabs(self.strat_influence.map[row,col]):
                    # logging.debug('%d, %d = %f' % (row, col, self.strat_influence.map[row,col]))
        
        # diffuse strategy influence
        logging.debug('strat_influence.diffuse().start = %s' % str(self.gamestate.time_remaining()))        
        for i in xrange(20):
            if self.gamestate.time_remaining() <  self.combat_time + 100:
                logging.debug('bailing diffuse after %d times' % (i))
                break
            diffuse_start = self.gamestate.time_remaining()
            self.strat_influence.diffuse()
            diffuse_duration = diffuse_start - self.gamestate.time_remaining()
            self.diffuse_time = max([diffuse_duration, self.diffuse_time])
        self.diffuse_time -= 1
        logging.debug('strat_influence.diffuse().finish = %s' % str(self.gamestate.time_remaining())) 

        # razing nearby hill takes precedence
        self.raze_override()
        
        # handle combat
        combat_start = self.gamestate.time_remaining()
        self.issue_combat_task()
        self.combat_time_history.append(combat_start - self.gamestate.time_remaining())
        self.combat_time_history.popleft()
        self.combat_time = max(self.combat_time_history)
        
        self.log_detail()
        # handle explorer
        self.issue_explore_task()
        logging.debug('endturn: my_ants count = %d, time_elapsed = %s' % (len(self.gamestate.my_ants()), self.gamestate.time_elapsed()))

    def raze_override(self):
        'razing close-by hill takes precedence over combat'
        for hill_loc, owner in self.gamestate.enemy_hills():
            for n_loc in self.gamestate.neighbour_table[hill_loc]:
                if n_loc in self.gamestate.my_ants():
                    direction = self.gamestate.direction(n_loc, hill_loc) + [None]
                    self.gamestate.issue_order((n_loc, direction[0]))
        
    def issue_combat_task(self):
        'combat logic'
        logging.debug('issue_combat_task.start = %s' % str(self.gamestate.time_remaining())) 
        zones = battle.get_combat_zones(self.gamestate)
        logging.debug('get_combat_zones.finish = %s' % str(self.gamestate.time_remaining())) 
        
        if zones is not None:
            logging.debug('zones.count = %d' % len(zones))
            for zone in zones:
                # only do combat for more than 1 friendlies
                if len(zone[0]) > 1:
                    logging.debug('group combat loop for = %s' % str(zone))
                    logging.debug('do_zone_combat.start = %s' % str(self.gamestate.time_remaining())) 
                    battle.do_zone_combat(self.gamestate, zone)
                    logging.debug('do_zone_combat.start = %s' % str(self.gamestate.time_remaining())) 
                
                # check if we still have time left to calculate more orders
                if self.gamestate.time_remaining() < 50:
                    logging.debug('bailing combat zone after %d times' % (i))
                    break
                
        logging.debug('issue_combat_task.finish = ' + str(self.gamestate.time_remaining())) 
    
    def normal_explore(self, my_ant):
        'only concern influence'
        loc_influences = {}
        for d in self.gamestate.passable_directions(my_ant):
            loc_influences[d] = self.strat_influence.map[self.gamestate.destination(my_ant, d)]
            
        #logging.debug('my_ant = %s, loc_influences = %s' % (str(my_ant),str(loc_influences)))
        if len(loc_influences) > 0:
            best_directions = min(loc_influences, key=loc_influences.get)
            self.gamestate.issue_order((my_ant, best_directions))
            logging.debug('moving %s' % str((my_ant, best_directions)))
    
    def avoidance_explore(self, my_ant, enemy_ants):
        'explore under enemies presence'
        safe_distance = self.gamestate.euclidean_distance_add(self.gamestate.attackradius2, 1)
        nav_info = []
        for loc in self.gamestate.passable_neighbours(my_ant) + [my_ant]:
            influence = self.strat_influence.map[loc]
            distance = min([self.gamestate.euclidean_distance2(loc, enemy_ant) for enemy_ant in enemy_ants])
            nav_info.append((influence, distance, loc))
            
        # go for lowest influence that's safe
        nav_info.sort()
        best_loc = None
        for info in nav_info:
            (influence, distance, loc) = info
            if distance > safe_distance:
                best_loc = loc
                break
        # if no safe move try largest distance
        if best_loc is None:
            (influence, distance, loc) = sorted(nav_info, key=lambda x: x[1], reverse=True)[0]
            best_loc = loc
            
        # do the move
        directions = self.gamestate.direction(my_ant, best_loc) + [None]
        self.gamestate.issue_order((my_ant, directions[0]))
        logging.debug('moving %s' % str((my_ant, directions[0])))
        
    def issue_explore_task(self):
        'explore map based on influence'
        logging.debug('issue_explore_task.start = %s' % str(self.gamestate.time_remaining())) 
        # loop through all my un-moved ants and set them to explore
        # the ant_loc is an ant location tuple in (row, col) form
        avoidance_distance = self.gamestate.euclidean_distance_add(self.gamestate.attackradius2, 2)
        for my_ant in self.gamestate.my_unmoved_ants():
            logging.debug('explore task for %s' % str(my_ant))
            enemy_ants = [enemy_ant for enemy_ant, owner in self.gamestate.enemy_ants() 
                        if self.gamestate.euclidean_distance2(my_ant, enemy_ant) <= avoidance_distance]
            if len(enemy_ants) > 0:
                logging.debug('going into avoidance_explore')
                self.avoidance_explore(my_ant, enemy_ants)
            else:
                logging.debug('going into normal_explore')
                self.normal_explore(my_ant)
            
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
