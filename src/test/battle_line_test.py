# battle_line_test.py: unit test for battle line module
#
# AI bot written for AI Challenge 2011 - Ants
# Author: Bill Y
# License: all your base are belong to us

import pickle
import unittest
import os, sys
cmd_folder = os.path.dirname(os.path.abspath('../combat'))
if cmd_folder not in sys.path:
    sys.path.insert(0, cmd_folder)
from combat import battle_line

class TestBattleLineFunctions(unittest.TestCase):   

    def setUp(self):
        pickle_file = open('test_data/battle_line_test/turn_52.gamestate', 'r')
        self.gamestate = pickle.load(pickle_file)
        pickle_file.close()
        
    def test_get_combat_zones(self):
        expected_zones = [([(24, 17), (26, 15)], [(20, 15)]), ([(19, 7), (20, 8)], [(14, 6)]), ([(21, 23), (20, 24)], [(16, 22), (17, 21)])]
        zones = battle_line.get_combat_zones(self.gamestate)
        
        self.assertEqual(zones, expected_zones)
        
    def test_eval_formation(self):
        """
         1
        
        0 0
        """
        pair = ([(2, 0), (2, 2)], [(0, 1)])
        score, distance = battle_line.eval_formation(self.gamestate, pair[0], pair[1])
        self.assertEqual(score, 1)
        self.assertEqual(distance, 5)
     
    def test2_eval_formation(self):
        """
         11
         
         0
          0
        """
        pair = ([(2, 1), (3, 2)], [(0, 1), (0, 2)])
        score, distance = battle_line.eval_formation(self.gamestate, pair[0], pair[1])
        self.assertEqual(score, -1)
        self.assertEqual(distance, 4)
        
if __name__ == '__main__':
    unittest.main()