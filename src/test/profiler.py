# profiler.py: profile certain routines
#
# AI bot written for AI Challenge 2011 - Ants
# Author: Bill Y
# License: all your base are belong to us

import pickle, cProfile
import os, sys, numpy, timeit, pickle
cmd_folder = os.path.dirname(os.path.abspath('.'))
if cmd_folder not in sys.path:
    sys.path.insert(0, cmd_folder)
from influence5 import Influence as Influence5
from influence6 import Influence as Influence6
import battle_line as battle


def setup_inf():
    'we use random_walk 10-2'
    pickle_file = open('test_data/perf_test/turn_11.gamestate', 'r')
    gamestate = pickle.load(pickle_file)
    pickle_file.close()
    
    inf1 = Influence5(gamestate)
    initiate_inf(inf1)
    inf2 = Influence6(gamestate)
    initiate_inf(inf2)
    
    return inf1, inf2

def initiate_inf(inf):
    for i in xrange(12):
        for j in range(12):
            if (i + j) % 3:
                inf.map[(i*10, j*10)] = -50
            else:
                inf.map[(i*10, j*10)] = 20
    for i in xrange(10):
        inf.diffuse()
        
def save_inf(inf, name):
    pickle_file = open('profiler_' + name + '.influence', 'wb')
    pickle.dump(inf, pickle_file)
    pickle_file.close()
    

def setup_combat_zones():
    pickle_file = open('test_data/perf_test/turn_177.gamestate', 'r')
    gamestate = pickle.load(pickle_file)
    pickle_file.close()
    return gamestate

def setup_overall():
    ready = """
turn 0
loadtime 3000
turntime 1000
rows 43
cols 39
turns 50
viewradius2 55
attackradius2 5
spawnradius2 1
player_seed 42
ready
    """
    setup = """
import MyBot
    """
    turns = """
turn 1
w 22 18
w 22 19
w 22 20
w 23 17
w 23 21
h 28 19 0
a 28 19 0
f 26 23
go
turn 2
h 28 19 0
a 28 20 0
f 25 26
f 26 23
go
    """
    return setup, turns

def profile_influence():
    inf1, inf2 = setup_inf()
    cProfile.run('inf1.diffuse()')
    cProfile.run('inf2.diffuse()')
    
def profile_combat_zone():
    gs = setup_combat_zones()
    cProfile.run('battle1.get_combat_zones(gs)')
    cProfile.run('battle2.get_combat_zones(gs)')

def profile_overall():
    ready, turns = setup_overall()
    
if __name__ == '__main__':
    inf1, inf2 = setup_inf()
    cProfile.run('inf1.diffuse()')
    cProfile.run('inf2.diffuse()')
