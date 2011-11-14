# battle_line_test.py: unit test for battle line module
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
import battle_line

class TestBattleLineFunctions(unittest.TestCase):   

    def setUp(self):
        pickle_file = open('test_data/battle_line_test/turn_85.gamestate', 'r')
        self.gamestate = pickle.load(pickle_file)
        pickle_file.close()
        
    #def test_get_combat_zones(self):
    #    expected_zones = battle_line.get_combat_zones(self.gamestate)
    #    zones = battle_line2.get_combat_zones(self.gamestate)

    #    self.assertEqual(zones, expected_zones)
        
    def test_eval_formation_1(self):
        """
         1
        
        0 0
        """
        pair = ([(2, 0), (2, 2)], [(0, 1)])
        score, distance = battle_line.eval_formation(self.gamestate, pair[0], pair[1])
        self.assertEqual(score, 2.0)
        self.assertEqual(distance, 5)
     
    def test_eval_formation_2(self):
        """
         11
         
         
         0
        """
        pair = ([(3, 1)], [(0, 1), (0, 2)])
        score, distance = battle_line.eval_formation(self.gamestate, pair[0], pair[1])
        self.assertEqual(score, 0.5)
        self.assertEqual(distance, 9)
        
    def test_eval_formation_3(self):
        """
         11
         
            0
        """
        pair = ([(3, 3)], [(0, 1), (0, 2)])
        score, distance = battle_line.eval_formation(self.gamestate, pair[0], pair[1])
        self.assertEqual(score, 1.0)
        self.assertEqual(distance, 10)
        
    def test_eval_formation_4(self):
        """
         11
         
           0
        """
        pair = ([(3, 2)], [(0, 1), (0, 2)])
        score, distance = battle_line.eval_formation(self.gamestate, pair[0], pair[1])
        self.assertEqual(score, 0.5)
        self.assertEqual(distance, 9)
        
    def test_eval_formation_5(self):
        """
        0123456
          1
         1  
         
           0
        """
        pair = ([(3, 3)], [(0, 2), (1, 1)])
        score, distance = battle_line.eval_formation(self.gamestate, pair[0], pair[1])
        self.assertEqual(score, 0.5)
        self.assertEqual(distance, 8)
        
    def test_get_formations_1(self):
        all_formations = battle_line.get_group_formations(self.gamestate, [(5,5)])
        # print(all_formations)
        # print(self.gamestate.map[4][5])
        # print(self.gamestate.map[6][5])
        # print(self.gamestate.map[5][4])
        # print(self.gamestate.map[5][6])
        self.assertTrue([(4,5)] in all_formations)
        self.assertTrue([(5,5)] in all_formations)
        self.assertTrue([(6,5)] in all_formations)
        self.assertTrue([(5,4)] in all_formations)
        self.assertTrue([(5,6)] not in all_formations)
        
    # def test_attack_1(self):
        # """
         # 1
        
        
        
        # 0 0
        # """
        # my_group = [(4, 0), (4, 2)]
        # enemy_group = [(0, 1)]
        # orders = battle_line.get_attack_orders(self.gamestate, my_group, enemy_group)
        # self.assertTrue(((4,0), 'n') in orders)
        # self.assertTrue(((4,2), 'n') in orders)
        
    # def test_attack_2(self):
        # """
        # 0123456
       # 0   1
       # 1
       # 20
       # 3 0  
        # """
        # my_group = [(2, 0), (3, 1)]
        # enemy_group = [(0, 3)]
        # orders = battle_line.get_attack_orders(self.gamestate, my_group, enemy_group)
        # print(orders)
        # self.assertTrue(((2,0), 'n') in orders)
        # self.assertTrue(((3,1), 'n') in orders)
        
if __name__ == '__main__':
    unittest.main()