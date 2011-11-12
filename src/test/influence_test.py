# influence_test.py: unit test for influence mapping
#
# AI bot written for AI Challenge 2011 - Ants
# Author: Bill Y
# License: all your base are belong to us

import pickle, unittest, os, sys, numpy as np
cmd_folder = os.path.dirname(os.path.abspath('.'))
if cmd_folder not in sys.path:
    sys.path.insert(0, cmd_folder)

from influence5 import Influence

class TestInfluence(unittest.TestCase):

    def setUp(self):
        pass
        
    def test_diffuse_parent_greater_than_children_single_pass(self):
        'make sure parent is greater or equal to child after single pass'
        pickle_file = open('test_data/influence_test/turn_1.gamestate', 'r')
        gamestate = pickle.load(pickle_file)
        pickle_file.close()
        gamestate.map = np.array(gamestate.map)
        inf = Influence(gamestate)
        
        #print(str(gamestate.food_list))
        for food_loc in gamestate.food_list:
            inf.map[food_loc] = 4
            
        for i in xrange(5):
            inf.diffuse()
            for food_loc in gamestate.food_list:
                food_val = inf.map[food_loc]
                for n_loc in gamestate.get_neighbour_locs(food_loc):
                    #print('%f => %f' % (food_val, inf.map[n_loc]))
                    self.assertTrue(food_val >= inf.map[n_loc])

    def test_diffuse_parent_greater_than_children_multi_pass(self):
        'make sure each level of parent is greater than its children after multiple passes'
        pickle_file = open('test_data/influence_test/turn_1.gamestate', 'r')
        gamestate = pickle.load(pickle_file)
        pickle_file.close()
        inf = Influence(gamestate)
        
        for food_loc in gamestate.food_list:
            inf.map[food_loc] += 4
                 
        for i in xrange(5):
            inf.diffuse()
        for food_loc in gamestate.food_list:
            food_val = inf.map[food_loc]
            for n_loc in gamestate.get_neighbour_locs(food_loc):
                n_val = inf.map[n_loc]
                self.assertTrue(food_val > n_val)
                for nn_loc in [loc for loc in gamestate.get_neighbour_locs(n_loc) if loc != food_loc]:
                    nn_val = inf.map[nn_loc]
                    self.assertTrue(n_val > nn_val)

    def test_diffuse_with_water(self):
        'make sure influence next to water diffuse slower than open locations'
        pickle_file = open('test_data/influence_test/turn_1.gamestate', 'r')
        gamestate = pickle.load(pickle_file)
        pickle_file.close()
        inf = Influence(gamestate)
        
        inf.map[(23,18)] = 10
        inf.map[(10,10)] = 10
        for i in xrange(5):
            inf.diffuse()
            #print ('%f, %f' % (inf.map[(23,18)], inf.map[(10,10)]))
        self.assertTrue(inf.map[(23,18)] < inf.map[(10,10)])            
    
    def test_diffuse_multi_source_overshadow(self):
        'make sure larger influence over shadows the smaller opposite influence right next'
        pickle_file = open('test_data/influence_test/turn_1.gamestate', 'r')
        gamestate = pickle.load(pickle_file)
        pickle_file.close()
        inf = Influence(gamestate)
        
        x = 25
        y = 20
        inf.map[(x, y)] = 10
        inf.map[(x+1, y)] = -1
        for i in xrange(5):
            inf.diffuse()
        
        self.assertTrue(inf.map[(x,y)] > inf.map[(x+1, y)])
        self.assertTrue(inf.map[(x+1,y)] > inf.map[(x+2, y)])
        self.assertTrue(inf.map[(x+2,y)] > inf.map[(x+3, y)])
        self.assertTrue(inf.map[(x+3,y)] > inf.map[(x+4, y)])
        self.assertTrue(inf.map[(x+2,y)] > inf.map[(x+2,y+1)])
        self.assertTrue(inf.map[(x+3,y)] > inf.map[(x+3, y-1)])

    def test_diffuse_total_value_no_change(self):
        'make sure total value of all sources do not change'
        pickle_file = open('test_data/influence_test/turn_1.gamestate', 'r')
        gamestate = pickle.load(pickle_file)
        pickle_file.close()
        inf = Influence(gamestate)
        
        inf.map[(23,18)] = 100
        inf.map[(10,10)] = 100
        inf.map[(26, 18)] = -10
        for i in xrange(50):
            inf.diffuse()
        
        # give some space for float point inaccuracy
        #print (inf.map.sum())
        #self.assertTrue(inf.map.sum() > 189.9 and inf.map.sum() < 190.1)
        
if __name__ == '__main__':
    unittest.main()