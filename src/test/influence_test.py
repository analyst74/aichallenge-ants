# influence_test.py: unit test for influence mapping
#
# AI bot written for AI Challenge 2011 - Ants
# Author: Bill Y
# License: all your base are belong to us

import pickle
import unittest
import os, sys
cmd_folder = os.path.dirname(os.path.abspath('.'))
if cmd_folder not in sys.path:
    sys.path.insert(0, cmd_folder)

from influence import Influence

class TestInfluence(unittest.TestCase):   

    def setUp(self):
        pass
        
    def test_diffuse_1(self):
        pickle_file = open('test_data/influence_test/turn_1.gamestate', 'r')
        gamestate = pickle.load(pickle_file)
        pickle_file.close()
        inf = Influence(gamestate, 0.9)
        
        #print(str(gamestate.food_list))
        for food_loc in gamestate.food_list:
            inf.map[food_loc] += -4
            
        #print(str([(key, inf.map[key]) for key in inf.map if inf.map[key] != 0]))        
        inf.diffuse()
        self.assertEqual(inf.map[food_loc], -2)
        for n_loc in gamestate.get_neighbour_locs(food_loc):
            self.assertEqual(inf.map[n_loc], -0.5)
        #print(str([(key, inf.map[key]) for key in inf.map if inf.map[key] != 0]))

    def test_diffuse_2(self):
        pickle_file = open('test_data/influence_test/turn_1.gamestate', 'r')
        gamestate = pickle.load(pickle_file)
        pickle_file.close()
        inf = Influence(gamestate, 0.9)
        
        for food_loc in gamestate.food_list:
            inf.map[food_loc] += -16
                 
        inf.diffuse()
        inf.diffuse()
        self.assertEqual(inf.map[food_loc], -5)
        for n_loc in gamestate.get_neighbour_locs(food_loc):
            self.assertEqual(inf.map[n_loc], -2)
        nn_loc = gamestate.destination(gamestate.destination(food_loc, 'n'), 'n')
        self.assertEqual(inf.map[nn_loc], -0.25)
        nw_loc = gamestate.destination(gamestate.destination(food_loc, 'n'), 'w')
        self.assertEqual(inf.map[nw_loc], -0.5)
        
        # print([(key, inf.map[key]) for key in inf.map if inf.map[key] != 0])
        
        # map_data = [[0 for col in range(inf.gamestate.cols)]
                    # for row in range(inf.gamestate.rows)]                    
        # for (row, col) in inf.map:
            # map_data[row][col] = inf.map[(row, col)]
        # for row in map_data:
            # print(row)

    def test_diffuse_with_water(self):
        pickle_file = open('test_data/influence_test/turn_1.gamestate', 'r')
        gamestate = pickle.load(pickle_file)
        pickle_file.close()
        inf = Influence(gamestate, 0.9)
        
        inf.map[(23,18)] = 10
        inf.diffuse()
        self.assertEqual(inf.map[(23,18)], 7.5)
        self.assertEqual(inf.map[(23,19)], 1.25)
        self.assertEqual(inf.map[(24,18)], 1.25)
        inf.diffuse()
        inf.diffuse()
        # print([(key, inf.map[key]) for key in inf.map if inf.map[key] != 0])
        # map_data = [[0 for col in range(inf.gamestate.cols)]
                    # for row in range(inf.gamestate.rows)]                    
        # for (row, col) in inf.map:
            # map_data[row][col] = inf.map[(row, col)]
        # for row in map_data:
            # print ','.join("%.2f" % f for f in row)
            
    def test_multi_diffuse_1(self):
        pickle_file = open('test_data/influence_test/turn_1.gamestate', 'r')
        gamestate = pickle.load(pickle_file)
        pickle_file.close()
        inf = Influence(gamestate, 0.9)
        
        for food_loc in gamestate.food_list:
            inf.map[food_loc] += -5
        for ant_loc in gamestate.my_ants():
            inf.map[ant_loc] += 2
            
        inf.diffuse()
        inf.diffuse()
        
        # print([(key, inf.map[key]) for key in inf.map if inf.map[key] != 0])
        # map_data = [[0 for col in range(inf.gamestate.cols)]
                    # for row in range(inf.gamestate.rows)]                    
        # for (row, col) in inf.map:
            # map_data[row][col] = inf.map[(row, col)]
        # for row in map_data:
            # print(row)
        
        
if __name__ == '__main__':
    unittest.main()