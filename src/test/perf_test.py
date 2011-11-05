# perf_test.py: performance test functions
#
# AI bot written for AI Challenge 2011 - Ants
# Author: Bill Y
# License: all your base are belong to us

import pickle, cProfile
import os, sys
cmd_folder = os.path.dirname(os.path.abspath('.'))
if cmd_folder not in sys.path:
    sys.path.insert(0, cmd_folder)
from influence import Influence

def setup_inf():
    pickle_file = open('test_data/perf_test/turn_21.gamestate', 'r')
    gamestate = pickle.load(pickle_file)
    pickle_file.close()
    inf = Influence(gamestate, 0.9)
    return inf

def run_diffuse(inf):
    for i in range(10):
        inf.diffuse()
    
if __name__ == '__main__':
    inf = setup_inf()
    #cProfile.run('run_diffuse(inf)', 'perf.result')
    cProfile.run('run_diffuse(inf)')