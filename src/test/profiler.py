# profiler.py: profile certain routines
#
# AI bot written for AI Challenge 2011 - Ants
# Author: Bill Y
# License: all your base are belong to us

import cProfile, os, sys, numpy, timeit, pickle
cmd_folder = os.path.dirname(os.path.abspath('.'))
if cmd_folder not in sys.path:
    sys.path.insert(0, cmd_folder)
from influence5 import Influence as Influence5
import battle_line as battle
from linear_influence3 import LinearInfluence as LinearInfluence3
    
    
def setup_linear_inf():
    'we use random_walk 10-2'
    pickle_file = open('test_data/perf_test/turn_500.gamestate', 'r')
    gamestate = pickle.load(pickle_file)
    pickle_file.close()
    
    # inf2 = LinearInfluence2(gamestate)
    # inf3a = LinearInfluence3a(gamestate)
    inf3 = LinearInfluence3(gamestate)
    
    return inf3
    
def profile_linear_map_set():
    inf2, inf3a, inf3b = setup_linear_inf()
    inf_value = -12
    influence_sources = [((row,col), inf_value) for row in range(inf2.gamestate.rows) if row%25==0 
                                                for col in range(inf2.gamestate.cols) if col%20==0]
    print('total of %d influence sources' % len(influence_sources))

    cProfile.run('inf3b.set_influence(influence_sources, True)')
    
def setup_inf():
    'we use random_walk 10-2'
    pickle_file = open('test_data/perf_test/turn_11.gamestate', 'r')
    gamestate = pickle.load(pickle_file)
    pickle_file.close()

    inf1 = Influence5(gamestate)
    initiate_inf(inf1)
    
    return inf1

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

def profile_influence():
    inf1, inf2 = setup_inf()
    cProfile.run('inf1.diffuse()')
    cProfile.run('inf2.diffuse()')
    
def profile_combat_zone():
    gs = setup_combat_zones()
    cProfile.run('battle1.get_combat_zones(gs)')
    cProfile.run('battle2.get_combat_zones(gs)')

if __name__ == '__main__':
    inf1, inf2 = setup_inf()
    cProfile.run('inf1.diffuse()')
    cProfile.run('inf2.diffuse()')
    
    # inf3 = setup_linear_inf()
    # inf_value = -12
    # influence_sources = [((row,col), inf_value) for row in range(inf3.gamestate.rows) if row%20==0 
                                                # for col in range(inf3.gamestate.cols) if col%20==0]
    # print('total of %d influence sources' % len(influence_sources))

    # cProfile.run('inf3.set_influence(influence_sources, True)')
