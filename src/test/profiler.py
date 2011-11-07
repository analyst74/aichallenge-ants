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
from influence import Influence
from influence2 import Influence as Influence2
from influence3 import Influence as Influence3
from combat import battle_line as battle1
from combat import battle_line2 as battle2

def setup_inf():
    pickle_file = open('test_data/perf_test/turn_11.gamestate', 'r')
    gamestate = pickle.load(pickle_file)
    pickle_file.close()    
    inf1 = Influence(gamestate, 0.9)
    initiate_inf(inf1)
    save_inf(inf1, 'inf1')
    inf2 = Influence2(gamestate, 0.9)
    initiate_inf(inf2)
    save_inf(inf2, 'inf2')
    inf3 = Influence3(gamestate, 0.9)
    initiate_inf(inf3)
    save_inf(inf3, 'inf3')
    return inf1, inf2, inf3

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
    
def run_diffuse(inf):
    for i in range(10):
        inf.diffuse()

def setup_combat_zones():
    pickle_file = open('test_data/perf_test/turn_177.gamestate', 'r')
    gamestate = pickle.load(pickle_file)
    pickle_file.close()
    return gamestate
    
if __name__ == '__main__':
    #inf, inf2, inf3 = setup_inf()
    #cProfile.run('run_diffuse(inf)')
    #cProfile.run('run_diffuse(inf2)')
    #cProfile.run('run_diffuse(inf3)')
    
    gs = setup_combat_zones()
    cProfile.run('battle1.get_combat_zones(gs)')
    cProfile.run('battle2.get_combat_zones(gs)')
