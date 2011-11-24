# MyBot.py: main program, required by contest
#
# AI bot written for AI Challenge 2011 - Ants
# Author: Bill Y
# License: all your base are belong to us

from core import *
from gamestate import GameState
from influence5 import Influence
from linear_influence3b import LinearInfluence
from planner3 import Planner
from random import choice
from collections import deque

import battle_line as battle
import sys, os, pickle, traceback, math

DETAIL_LOG = False
DETAIL_LOG_START = 450

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
        self.explore_time = 0
    
    # do_setup is run once at the start of the game
    # after the bot has received the game settings
    def do_setup(self):
        # initialize data structures after learning the game settings
        self.food_influence = LinearInfluence(self.gamestate)
        self.raze_influence = LinearInfluence(self.gamestate)
        self.defense_influence = LinearInfluence(self.gamestate)
        self.explore_influence = Influence(self.gamestate)
        self.planner = Planner(self.gamestate)
    
    def log_turn(self, turn_no):
        debug_logger.debug('turn ' + str(self.gamestate.current_turn))
        perf_logger.debug('turn ' + str(self.gamestate.current_turn))
        perf_logger.debug('self.diffuse_time = %d' % self.diffuse_time)
        perf_logger.debug('self.combat_time_history = %s' % str(self.combat_time_history))
        perf_logger.debug('self.combat_time = %s' % self.combat_time)
        perf_logger.debug('self.explore_time = %d' % self.explore_time)
            
    def log_detail(self):
        if DETAIL_LOG and os.path.isdir('pickle') and \
            int(self.gamestate.current_turn) > DETAIL_LOG_START and \
            int(self.gamestate.current_turn) % 10 == 0 \
            :
            # dump gamestate
            pickle_file = open('pickle/turn_' + str(self.gamestate.current_turn) + '.gamestate', 'wb')
            pickle.dump(self.gamestate, pickle_file)
            pickle_file.close()
            
            # dump influence map value
            # pickle_file = open('pickle/turn_' + str(self.gamestate.current_turn) + '.influence', 'wb')
            # pickle.dump(self.explore_influence, pickle_file)
            # pickle_file.close()
    
    # do turn is run once per turn
    def do_turn(self):        
        # detailed logging
        self.log_turn(self.gamestate.current_turn)

        # razing nearby hill takes precedence
        self.raze_override()
        
        # handle combat
        combat_start = self.gamestate.time_remaining()
        self.issue_combat_task()
        self.combat_time_history.append(combat_start - self.gamestate.time_remaining())
        self.combat_time_history.popleft()
        self.combat_time = max(self.combat_time_history)        
        
        # use planner to set new influence
        perf_logger.debug('food_influence.start = %s' % str(self.gamestate.time_elapsed()))
        self.planner.update_food_influence(self.food_influence)
        perf_logger.debug('raze_influence.start = %s' % str(self.gamestate.time_elapsed()))     
        self.planner.update_raze_influence(self.raze_influence)
        perf_logger.debug('defense_influence.start = %s' % str(self.gamestate.time_elapsed()))     
        self.planner.update_defense_influence(self.defense_influence)
        perf_logger.debug('explore_influence.start = %s' % str(self.gamestate.time_elapsed()))     
        self.planner.update_explore_influence(self.explore_influence)
        perf_logger.debug('influences.finish = %s' % str(self.gamestate.time_elapsed()))        
        
        # decay strategy influence
        self.explore_influence.decay(DECAY_RATE)
        
        # diffuse explore_influence, which is the only one using molecular diffusion
        perf_logger.debug('explore_influence.diffuse().start = %s' % str(self.gamestate.time_elapsed()))
        for i in xrange(30):
            if self.gamestate.time_remaining() < self.diffuse_time + self.explore_time + 20:
                perf_logger.debug('bailing diffuse after %d times' % (i))
                break
            diffuse_start = self.gamestate.time_remaining()
            self.explore_influence.diffuse()
            diffuse_duration = diffuse_start - self.gamestate.time_remaining()
            self.diffuse_time = max([diffuse_duration, self.diffuse_time])
        self.diffuse_time -= 1
        perf_logger.debug('explore_influence.diffuse().finish = %s' % str(self.gamestate.time_elapsed())) 
        
        self.log_detail()
        
        explore_start = self.gamestate.time_remaining()
        # avoidance explorer
        self.avoidance_explore()
        perf_logger.debug('self.avoidance_explore.finish = %s' % str(self.gamestate.time_elapsed()))   
        
        # normal explore
        self.normal_explore()
        self.explore_time = max([explore_start - self.gamestate.time_remaining(), self.explore_time]) - 1
        perf_logger.debug('self.normal_explore.finish = %s' % str(self.gamestate.time_elapsed()))   
        perf_logger.debug('endturn: my_ants count = %d, time_elapsed = %s' % (len(self.gamestate.my_ants()), self.gamestate.time_elapsed()))

    def raze_override(self):
        'razing close-by hill takes precedence over combat'
        for hill_loc, owner in self.gamestate.enemy_hills():
            for n_loc in self.gamestate.neighbour_table[hill_loc]:
                if n_loc in self.gamestate.my_ants():
                    direction = self.gamestate.direction(n_loc, hill_loc) + [None]
                    self.gamestate.issue_order((n_loc, direction[0]))
        
    def issue_combat_task(self):
        'combat logic'
        perf_logger.debug('issue_combat_task.start = %s' % str(self.gamestate.time_elapsed())) 
        zones = battle.get_combat_zones(self.gamestate)
        perf_logger.debug('get_combat_zones.finish = %s' % str(self.gamestate.time_elapsed())) 
        
        if zones is not None:
            debug_logger.debug('zones.count = %d' % len(zones))
            i = 0
            for zone in zones:
                i += 1
                # debug_logger.debug('group combat loop for = %s' % str(zone))
                # perf_logger.debug('do_zone_combat.start = %s' % str(self.gamestate.time_elapsed())) 
                battle.do_zone_combat(self.gamestate, zone)
                # perf_logger.debug('do_zone_combat.start = %s' % str(self.gamestate.time_elapsed())) 
                
                # check if we still have time left to calculate more orders
                if self.gamestate.time_remaining() < 100:
                    debug_logger.debug('bailing combat zone after %d times' % (i))
                    break
                
        perf_logger.debug('issue_combat_task.finish = ' + str(self.gamestate.time_elapsed())) 
    
    def get_desired_moves(self, ant):
        desired_moves = []
        # food
        desired_moves.extend(self.get_desired_move_from_linear_influence(ant, self.food_influence))
        debug_logger.debug('desired_moves.food = %s' % str(desired_moves))
        
        # defend hill
        desired_moves.extend(self.get_desired_move_from_linear_influence(ant, self.defense_influence))
        debug_logger.debug('desired_moves.defense = %s' % str(desired_moves))
        
        # raze hill
        desired_moves.extend(self.get_desired_move_from_linear_influence(ant, self.raze_influence))
        debug_logger.debug('desired_moves.raze = %s' % str(desired_moves))
            
        # explore
        desired_moves.extend(self.get_desired_move_from_molecular_influence(ant, self.explore_influence))
        debug_logger.debug('desired_moves.explore = %s' % str(desired_moves))
            
        # uniquify
        seen = set()
        seen_add = seen.add
        desired_moves = [move for move in desired_moves if move not in seen and not seen_add(move)]
        return desired_moves

    def get_desired_move_from_molecular_influence(self, ant, influence):
        desired_moves = []
        neighbours_and_influences = sorted([(influence.map[loc], loc) for loc in [ant] + self.gamestate.passable_neighbours(ant)])
        debug_logger.debug('neighbours_and_influences = %s' % str(neighbours_and_influences))
        for inf, n_loc in neighbours_and_influences:
            desired_moves.append(n_loc)
            
        return desired_moves
    
    def get_desired_move_from_linear_influence(self, ant, influence):
        desired_moves = []
        if influence.map[ant] != 0:
            neighbours_and_influences = sorted([(influence.map[loc], loc) for loc in [ant] + self.gamestate.passable_neighbours(ant)])
            debug_logger.debug('neighbours_and_influences = %s' % str(neighbours_and_influences))
            for inf, n_loc in neighbours_and_influences:
                if inf < influence.map[ant]:
                    desired_moves.append(n_loc)
            
        return desired_moves
        
    def normal_explore(self):
        'only concern influence'
        for my_ant in self.gamestate.my_unmoved_ants():
            debug_logger.debug('normal explore task for %s' % str(my_ant))
            desired_moves = self.get_desired_moves(my_ant)
            if len(desired_moves) > 0:
                move = desired_moves[0]
                # do the move
                directions = self.gamestate.direction(my_ant, move) + [None]
                self.gamestate.issue_order((my_ant, directions[0]))           
            
            # check if we still have time left to calculate more orders
            if self.gamestate.time_remaining() < 10:
                perf_logger.debug('bailing normal explore')
                break
    
    def avoidance_explore(self):
        'explore under enemies presence'
        avoidance_distance = self.gamestate.euclidean_distance_add(self.gamestate.attackradius2, 2)
        for my_ant in self.gamestate.my_unmoved_ants():
            enemy_ants = [enemy_ant for enemy_ant, owner in self.gamestate.enemy_ants() 
                        if self.gamestate.euclidean_distance2(my_ant, enemy_ant) <= avoidance_distance]
            if len(enemy_ants) > 0:
                # don't initiate 1 on 1 exchange, but don't be afraid
                safe_distance = self.gamestate.attackradius2
                if len(enemy_ants) > 1:
                    # be safer if more enemies are around
                    safe_distance = self.gamestate.euclidean_distance_add(self.gamestate.attackradius2, 1)
                desired_moves = self.get_desired_moves(my_ant)                
                move_distances = {move:min([self.gamestate.euclidean_distance2(move, enemy_ant) for enemy_ant in enemy_ants])
                                    for move in desired_moves}
                debug_logger.debug('move_distances = %s' % str(move_distances))
                # go for lowest influence that's safe
                best_move = None
                for move in desired_moves:
                    if move_distances[move] > safe_distance:
                        best_move = move
                        break
                # if no safe move try largest distance
                if best_move is None:
                    best_move = max(move_distances, key=move_distances.get)
                    
                # do the move
                directions = self.gamestate.direction(my_ant, best_move) + [None]
                self.gamestate.issue_order((my_ant, directions[0]))
                debug_logger.debug('moving %s' % str((my_ant, directions[0])))
            
            # check if we still have time left to calculate more orders
            if self.gamestate.time_remaining() < 20:
                perf_logger.debug('bailing avoidance explore')
                break
        
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
