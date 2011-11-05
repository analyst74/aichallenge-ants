# influence_test.py: unit test for influence mapping
#
# AI bot written for AI Challenge 2011 - Ants
# Author: Bill Y
# License: all your base are belong to us

import pickle
import unittest
import os, sys
import gamestate, influence

class TestInfluence(unittest.TestCase):   

    def setUp(self):
        pass
        
    def test_food(self):
        test = gamestate.GameState()
        pickle_file = open('test/test_data/influence_test/turn_2.gamestate', 'r')
        gs = pickle.load(pickle_file)
        pickle_file.close()
        inf = influence.Influence(gs, 0.9)
        
        print(str(gs))
        # for food_loc in gamestate.food_list:
            # self.strat_influence.map[food_loc] += self.food_value
            
        # print(str(inf))

if __name__ == '__main__':
    unittest.main()