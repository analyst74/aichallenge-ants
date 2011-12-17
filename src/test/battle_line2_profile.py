# battle_line2_profile.py: performance profiler for battle_line2
#
# AI bot written for AI Challenge 2011 - Ants
# Author: Bill Y
# License: all your base are belong to us

import cProfile, os, sys, numpy, timeit, pickle
cmd_folder = os.path.dirname(os.path.abspath('.'))
if cmd_folder not in sys.path:
    sys.path.insert(0, cmd_folder)
import gamestate as gs
import battle_line2 as battle
import cython_ext2
import numpy as np

def setup_gamestate():
    'we use random_walk 10-2'
    pickle_file = open('test_data/battle_line2_profile/turn_270.gamestate', 'r')
    gamestate = pickle.load(pickle_file)
    pickle_file.close()
    return gamestate

def pre_calc_distance(gamestate):
    gamestate.distance_table = {}
    for row in range(gamestate.rows):
        for col in range(gamestate.cols):
            gamestate.distance_table[(row,col)] = np.zeros((gamestate.rows, gamestate.cols), dtype=int) + 100
            for d_row in range(row-5, row+6):
                for d_col in range(col-5, col+6):
                    d_row = d_row % gamestate.rows
                    d_col = d_col % gamestate.cols
                    gamestate.distance_table[(row,col)][d_row, d_col] = \
                        cython_ext2.euclidean_distance2(row, col, d_row, d_col, gamestate.rows, gamestate.cols)

if __name__ == '__main__':
    gamestate = setup_gamestate()
    pre_calc_distance(gamestate)
    cProfile.run('battle.do_combat(gamestate)')