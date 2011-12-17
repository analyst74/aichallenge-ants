# battle_line2_test.py: unit test for battle line 2nd implementation
#
# AI bot written for AI Challenge 2011 - Ants
# Author: Bill Y
# License: all your base are belong to us

import unittest, os, sys
import numpy as np
cmd_folder = os.path.dirname(os.path.abspath('.'))
if cmd_folder not in sys.path:
    sys.path.insert(0, cmd_folder)
import gamestate as gs
from core import *
from battle_line2 import *

class TestBattle2Functions(unittest.TestCase):   
    def setUp(self):
        self.gamestate = gs.GameState()
        setup_data = """
turn 0
loadtime 3000  
turntime 1000  
rows 42
cols 38
turns 500  
viewradius2 55  
attackradius2 5  
spawnradius2 1  
player_seed 42
ready
        """
        self.gamestate.setup(setup_data)
        
    def test_get_distance_map_1(self):
        """
 23456789
2......
3......
4......
5...a..
6......
7......
8......
        """
        data = """
turn 1
a 5 5 0
go
        """
        self.gamestate.update(data)
        distance_map = get_distance_map(self.gamestate, self.gamestate.my_ants(), ZONE_BORDER[3])
        
        self.assertEqual(distance_map[5,5], 0)
        self.assertEqual(distance_map[5,6], 1)
        self.assertEqual(distance_map[4,7], 5)
        self.assertEqual(distance_map[3,8], 13)
        
    def test_get_distance_map_2(self):
        """
 23456789
2......
3..a...
4.a....
5www...
6......
7......
8......
        """
        data = """
turn 1
a 3 4 0
a 4 3 0
w 5 2
w 5 3
w 5 4
go
        """
        self.gamestate.update(data)
        distance_map = get_distance_map(self.gamestate, self.gamestate.my_ants(), ZONE_BORDER[1])
        # print(distance_map[0:10, 0:10])
        
        self.assertEqual(distance_map[3,4], 0)
        self.assertEqual(distance_map[4,3], 0)
        self.assertEqual(distance_map[3,3], 1)
        self.assertEqual(distance_map[3,2], 2)
        self.assertEqual(distance_map[6,3], 4)
        self.assertEqual(distance_map[6,4], 5)
        
        
    def test_generate_move_1(self):
        """
 23456789
2......
3......
4...b..
5......
6......
7..aa..
8......
        """
        data = """
turn 1
a 7 4 0
a 7 5 0
a 4 5 1
go
        """
        self.gamestate.update(data)
        enemy_ants = [ant for ant, owner in self.gamestate.enemy_ants()]
        distance_map = get_distance_map(self.gamestate, enemy_ants, ZONE_BORDER[3])
        
        kill_moves = generate_move(self.gamestate, self.gamestate.my_ants(), distance_map, 1, ZONE_BORDER[0])        
        self.assertEqual(len(kill_moves), 1)
        self.assertEqual(kill_moves[0], [(6,4), (6,5)])
        
        danger_moves = generate_move(self.gamestate, self.gamestate.my_ants(), distance_map, ZONE_BORDER[0], ZONE_BORDER[1])
        self.assertEqual(len(danger_moves), 4)
        self.assertTrue([(7,4), (7,5)] in danger_moves)
        self.assertTrue([(7,4), (7,6)] in danger_moves)
        self.assertTrue([(7,5), (7,6)] in danger_moves)
        
        safe_moves = generate_move(self.gamestate, self.gamestate.my_ants(), distance_map, ZONE_BORDER[1], ZONE_BORDER[3])        
        self.assertEqual(len(safe_moves), 2)
        self.assertTrue([(7,3), (8,5)] in safe_moves)
        self.assertTrue([(8,4), (8,5)] in safe_moves)
        
    def test_generate_move_2(self):
        """
 23456789
2......
3...b..
4......
5......
6......
7..aa..
8......
        """
        data = """
turn 1
a 7 4 0
a 7 5 0
a 3 5 1
go
        """
        self.gamestate.update(data)
        enemy_ants = [ant for ant, owner in self.gamestate.enemy_ants()]
        distance_map = get_distance_map(self.gamestate, enemy_ants, ZONE_BORDER[3])
        
        kill_moves = generate_move(self.gamestate, self.gamestate.my_ants(), distance_map, 1, ZONE_BORDER[0])
        self.assertEqual(len(kill_moves), 1)
        self.assertEqual(kill_moves[0], [(6,4), (6,5)])
        
        danger_moves = generate_move(self.gamestate, self.gamestate.my_ants(), distance_map, ZONE_BORDER[0], ZONE_BORDER[1])
        self.assertEqual(len(kill_moves), 1)
        self.assertEqual(kill_moves[0], [(6,4), (6,5)])
        
    def test_get_combat_groups_1(self):
        """
 23456789
2......
3...b..
4......
5......
6......
7..aa..
8......
        """
        data = """
turn 1
a 7 4 0
a 7 5 0
a 3 5 1
go
        """
        gamestate=self.gamestate
        self.gamestate.update(data)
        
        # enemy_ants = [ant for ant, owner in gamestate.enemy_ants()]
        # enemy_distance_map = get_distance_map(gamestate, enemy_ants, ZONE_BORDER[3])

        # print('---get_combat_groups_1')
        combat_groups = get_combat_groups(gamestate)
        # print(combat_groups)
        # print('===')
        self.assertTrue((7,4) in combat_groups[0][0])
        self.assertTrue((7,5) in combat_groups[0][0])
        self.assertTrue((3,5) in combat_groups[0][1])
        
    def test_get_combat_groups_2(self):
        """
 23456789
2..b....
3........
4.....b..
5..a.....
6.wa....b
7aa......
8........
        """
        data = """
turn 1
a 2 4 1
a 4 7 1
a 5 4 0
w 6 3
a 6 4 0
a 6 9 1
a 7 2 0
a 7 3 0
go
        """
        self.gamestate.update(data)
        # enemy_ants = [ant for ant, owner in self.gamestate.enemy_ants()]
        # enemy_distance_map = get_distance_map(self.gamestate, enemy_ants, ZONE_BORDER[3])
        # print('-------test_get_combat_groups_2')
        my_group, enemy_group = get_combat_groups(self.gamestate)[0]
        # print(my_group)
        # print('======')
        
        self.assertTrue(len(my_group), 2)
        self.assertEqual(my_group.index((5,4)), 0)
        self.assertEqual(my_group.index((6,4)), 1)
        
    def test_get_combat_groups_3(self):
        """
 23456789
2......
3...b..
4......
5......
6......
7..aa..
8.aa...
        """
        data = """
turn 1
a 7 4 0
a 7 5 0
a 8 4 0
a 8 3 0
a 3 5 1
go
        """
        gamestate=self.gamestate
        self.gamestate.update(data)
        
        # enemy_ants = [ant for ant, owner in gamestate.enemy_ants()]
        # enemy_distance_map = get_distance_map(gamestate, enemy_ants, ZONE_BORDER[3])

        # print('----')
        combat_groups = get_combat_groups(gamestate)                
        # print(combat_groups)
        
        self.assertTrue((7,4) in combat_groups[0][0])
        self.assertTrue((7,5) in combat_groups[0][0])
        self.assertTrue((8,4) not in combat_groups[0][0])
        self.assertTrue((8,3) not in combat_groups[0][0])
        self.assertTrue((3,5) in combat_groups[0][1])
        
    def test_get_combat_groups_4(self):
        data = """
turn 1
a 7 9 0
a 9 6 1
a 10 7 1
a 10 14 1
a 13 14 0
go
        """
        gamestate=self.gamestate
        self.gamestate.update(data)
        
        # print('---test_get_combat_groups_4')
        combat_groups = get_combat_groups(gamestate)  
        # print(combat_groups[0][0])
        # print('===')
        
        self.assertEqual(len(combat_groups), 1)
        self.assertEqual(len(combat_groups[0][0]), 1)
        self.assertTrue((7,9) in combat_groups[0][0])
        self.assertEqual(len(combat_groups[0][1]), 2)
        self.assertTrue((9,6) in combat_groups[0][1])
        self.assertTrue((10,7) in combat_groups[0][1])
        
    def test_get_combat_groups_5(self):
        """
 23456789
1....b.
2a.....
3.....b
4.a..bb
5.a..b.
6.a....
7.aa...
8.a....
        """
        data = """
turn 1
a 2 2 0
a 4 3 0
a 5 3 0
a 6 3 0
a 7 3 0
a 7 4 0
a 8 3 0
a 1 6 1
a 3 7 1
a 4 6 1
a 4 7 1
a 5 6 1
go
        """
        gamestate=self.gamestate
        self.gamestate.update(data)
        
        enemy_ants = [ant_loc for ant_loc, owner in gamestate.enemy_ants()]
        enemy_distance_map = get_distance_map(gamestate, enemy_ants, ZONE_BORDER[2])
        
        combat_groups = get_combat_groups(gamestate)
        
        self.assertEqual(len(combat_groups), 1)  
        self.assertEqual(len(combat_groups[0][0]), 6)
        self.assertEqual(len(combat_groups[0][1]), 5)
        
    def test_do_combat_1(self):
        """
 23456789
2......
3...b..
4......
5......
6......
7..aa..
8......
        """
        data = """
turn 1
a 7 4 0
a 7 5 0
a 3 5 1
go
        """
        self.gamestate.update(data)
        
        do_combat(self.gamestate)
        self.assertEqual(self.gamestate.move_table[(6,4)], (7,4))
        self.assertEqual(self.gamestate.move_table[(6,5)], (7,5))
        
    def test_do_combat_2(self):
        """
 23456789
2......
3..bb..
4......
5......
6..aa..
7......
8......
        """
        data = """
turn 1
a 6 4 0
a 6 5 0
a 3 5 1
a 3 4 1
go
        """
        self.gamestate.update(data)
        
        do_combat(self.gamestate)
        self.assertEqual(self.gamestate.move_table[(6,4)], (6,4))
        self.assertEqual(self.gamestate.move_table[(6,5)], (6,5))
        
    def test_do_combat_3(self):
        """
 23456789
2......
3..bbb.
4......
5......
6..aa..
7......
8......
        """
        data = """
turn 1
a 6 4 0
a 6 5 0
a 3 4 1
a 3 5 1
a 3 6 1
go
        """
        self.gamestate.update(data)
        
        do_combat(self.gamestate)
        # print(self.gamestate.move_table)
        self.assertEqual(self.gamestate.move_table[(6,3)], (6,4))
        self.assertEqual(self.gamestate.move_table[(6,4)], (6,5))
        
    def test_do_combat_4(self):
        """
 23456789
2..b....
3........
4.....b..
5..a.....
6.wa...b.
7aa......
8........
        """
        data = """
turn 1
a 2 4 1
a 4 7 1
a 5 4 0
w 6 3
a 6 4 0
a 6 8 1
a 7 2 0
a 7 3 0
go
        """
        gamestate = self.gamestate
        self.gamestate.update(data)
        
        # combat_groups = get_combat_groups(gamestate)  
        # print(combat_groups)
        
        do_combat(self.gamestate)
        print(self.gamestate.move_table)
        # self.assertEqual(self.gamestate.move_table[(6,4)], (5,4))
        # self.assertEqual(self.gamestate.move_table[(7,4)], (6,4))
        self.assertEqual(self.gamestate.move_table[(5,3)], (5,4))
        self.assertEqual(self.gamestate.move_table[(5,4)], (6,4))
        
    def test_do_combat_5(self):
        """
 23456789
2...b...
3..b.....
4.b......
5........
6...aa...
7........
8........
        """
        data = """
turn 1
a 2 5 1
a 3 4 1
a 4 3 1
a 6 5 0
a 6 6 0
w 5 4
w 6 3
        """
        gamestate = self.gamestate
        self.gamestate.update(data)
        
        # enemy_ants = [ant for ant, owner in gamestate.enemy_ants()]
        # enemy_distance_map = get_distance_map(gamestate, enemy_ants, ZONE_BORDER[3])
        # my_group, enemy_group = get_combat_groups(gamestate)[0]
        # all_moves = [move for move in gamestate.passable_moves(my_group[1])]
        # desirable_moves = [move for move in all_moves
                            # if enemy_distance_map[move] >= ZONE_BORDER[1]
                            # and enemy_distance_map[move] < ZONE_BORDER[2]]
        # print(enemy_distance_map[0:8,0:8])
        # print(desirable_moves)
        
        do_combat(self.gamestate)
        # print(self.gamestate.move_table)
        
        self.assertEqual(self.gamestate.move_table[(7,5)], (6,5))
        self.assertEqual(self.gamestate.move_table[(6,6)], (6,6))

if __name__ == '__main__':
    unittest.main()

