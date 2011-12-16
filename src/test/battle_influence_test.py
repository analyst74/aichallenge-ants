# battle_influence_test.py: unit test for battle influence module
#
# AI bot written for AI Challenge 2011 - Ants
# Author: Bill Y
# License: all your base are belong to us

import unittest, os, sys
import numpy as np
cmd_folder = os.path.dirname(os.path.abspath('.'))
if cmd_folder not in sys.path:
    sys.path.insert(0, cmd_folder)
import battle_influence, gamestate as gs
from core import *

class TestBattleFunctions(unittest.TestCase):   

    def setUp(self):
        self.gamestate = gs.GameState()
        setup_data = """
turn 0
loadtime 3000  
turntime 1000  
rows 12
cols 12
turns 500  
viewradius2 55  
attackradius2 5  
spawnradius2 1  
player_seed 42
ready
        """
        self.gamestate.setup(setup_data)
                
    def test_find_my_combat_ant_1(self):
        """
 23456789
2..b..
3.....
4.....
5.a...
6.....aa
7.....
8..a..
        """
        data = """
turn 1
a 2 4 1 
a 5 3 0
a 6 7 0
a 6 8 0
a 8 4 0
go
        """
        self.gamestate.update(data)
        combat_distance = self.gamestate.euclidean_distance_add(self.gamestate.attackradius2, + 3)
        # print(self.combat_distance)
        # print(self.gamestate.euclidean_distance2((7,9),(11,12)))
        # print(self.gamestate.euclidean_distance2((7,9),(11,13)))
        # print(self.gamestate.euclidean_distance2((7,9),(14,9)))
        my_combat_ants = battle_influence.bfs_find_my_combat_ants(self.gamestate, 
                            self.gamestate.enemy_ants(), combat_distance)
        self.assertEqual(len(my_combat_ants), 2)
        self.assertTrue((5,3) in my_combat_ants)
        self.assertTrue((6,7) in my_combat_ants)
        
    def test_find_my_combat_ant_2(self):
        """
 23456789
2..b..
3.....
4.....
5.....
6.....aaa
7.....
8.....
9.....
0...b..
        """
        data = """
turn 1
a 2 4 1
a 6 7 0 
a 6 8 0 
a 6 9 0
a 10 5 1
go
        """
        self.gamestate.update(data)
        combat_distance = self.gamestate.euclidean_distance_add(self.gamestate.attackradius2, + 3)
        my_combat_ants = battle_influence.bfs_find_my_combat_ants(self.gamestate, 
                            self.gamestate.enemy_ants(), combat_distance)
        self.assertEqual(len(my_combat_ants), 2)
        self.assertTrue((6,7) in my_combat_ants)
        self.assertTrue((6,8) in my_combat_ants)
        
    def test_set_influence_1(self):
        influence_distance = self.gamestate.euclidean_distance_add(self.gamestate.attackradius2, + 1)
        map = np.zeros((self.gamestate.rows, self.gamestate.cols), dtype=np.int)
        battle_influence.bfs_set_influence(self.gamestate, map, [(3,3)], influence_distance)
        battle_influence.bfs_set_influence(self.gamestate, map, [(3,8), (4,8)], influence_distance)
        
        self.assertEqual(map[1,0], 0)
        self.assertEqual(map[1,1], 1)
        self.assertEqual(map[2,0], 1)
        self.assertEqual(map[3,0], 1)
        self.assertEqual(map[4,0], 1)
        
        self.assertEqual(map[2,5], 2)
        self.assertEqual(map[3,5], 2)
        self.assertEqual(map[4,5], 2)
        
        self.assertEqual(map[6,7], 1)
        self.assertEqual(map[6,8], 1)
        self.assertEqual(map[6,9], 1) 
        self.assertEqual(map[6,10], 1) 
        self.assertEqual(map[7,10], 0) 

    def test_get_influence_by_owner_1(self):
        """
 23456789
2..b..
3.....
4......c
5.a...
6.....aa
7.....
8.....
9..a..
        """
        data = """
turn 1
a 2 4 1 
a 5 3 0
a 6 7 0
a 6 8 0
a 9 4 0
a 4 8 2
go
        """
        self.gamestate.update(data)
        my_ants = self.gamestate.my_ants()
        enemy_ants = self.gamestate.enemy_ants()
        threat_distance = self.gamestate.attackradius2
        influence_by_owner = battle_influence.get_influence_by_owner(self.gamestate, my_ants, enemy_ants, threat_distance)
        
        self.assertEqual(len(influence_by_owner), 3)
        self.assertEqual(influence_by_owner[0][2,4], 1)
        self.assertEqual(influence_by_owner[0][6,5], 4)
        self.assertEqual(influence_by_owner[0][7,5], 4)

    def test_get_influence_by_threat_1(self):
        """
 23456789
2..b..
3.....
4.....c
5..a..
6.....aa
7.....
8.....
        """
        data = """
turn 1
a 2 4 1 
a 5 4 0
a 6 7 0
a 6 8 0
a 4 7 2
go
        """
        self.gamestate.update(data)
        my_ants = self.gamestate.my_ants()
        enemy_ants = self.gamestate.enemy_ants()
        threat_distance = self.gamestate.attackradius2
        influence_by_owner = battle_influence.get_influence_by_owner(self.gamestate, my_ants, enemy_ants, threat_distance)
        influence_by_threat = battle_influence.get_influence_by_threat(self.gamestate, my_ants, enemy_ants, threat_distance)
        
        self.assertEqual(len(influence_by_threat), 3)
        self.assertEqual(influence_by_threat[0][4,4], 2)
        self.assertEqual(influence_by_threat[0][6,4], 0)
        self.assertEqual(influence_by_threat[0][6,6], 1)
        self.assertEqual(influence_by_threat[1][2,4], 1)
        self.assertEqual(influence_by_threat[1][2,5], 2)
        self.assertEqual(influence_by_threat[2][4,6], 4)
        self.assertEqual(influence_by_threat[2][4,7], 3)

    def test_get_combat_scores_1(self):
        """
 23456789
2...b.
3.....
4.....
5.....
6..a..
7.....
8.....
        """
        data = """
turn 1
a 2 5 1
a 6 4 0
go
        """
        self.gamestate.update(data)
        my_ants = self.gamestate.my_ants()
        enemy_ants = self.gamestate.enemy_ants()
        threat_distance = self.gamestate.attackradius2
        influence_by_owner = battle_influence.get_influence_by_owner(self.gamestate, my_ants, enemy_ants, threat_distance)
        influence_by_threat = battle_influence.get_influence_by_threat(self.gamestate, my_ants, enemy_ants, threat_distance)

        combat_scores = battle_influence.get_combat_scores(self.gamestate, my_ants, enemy_ants, influence_by_threat, threat_distance)

        # print (combat_scores)
        self.assertEqual(combat_scores[(5,4)], 0.99)
        self.assertEqual(combat_scores[(6,4)], 0.99)

    def test_get_combat_scores_2(self):
        """
 23456789
2..bb.
3.....
4.....
5.....
6..aa.
        """
        data = """
turn 1
a 2 4 1 
a 2 5 1 
a 6 4 0
a 6 5 0
go
        """
        self.gamestate.update(data)
        my_ants = self.gamestate.my_ants()
        enemy_ants = self.gamestate.enemy_ants()
        threat_distance = self.gamestate.attackradius2
        influence_by_threat = battle_influence.get_influence_by_threat(self.gamestate, my_ants, enemy_ants, threat_distance)
        combat_scores = battle_influence.get_combat_scores(self.gamestate, my_ants, enemy_ants, influence_by_threat, threat_distance)

        # print (influence_by_threat)
        # print (combat_scores)
        self.assertEqual(combat_scores[(5,4)], 2.02)
        self.assertEqual(combat_scores[(6,4)], 0.99)

    def test_get_combat_scores_3(self):
        'this test makes sure when we are winning, our ant will press forward'
        """
 23456789
2b....
3...a.
4..a..
5.a...
6.....
7.....
8.....
        """
        data = """
turn 1
a 2 2 1 
a 3 5 0 
a 4 4 0 
a 5 3 0
go
        """
        self.gamestate.update(data)
        my_ants = self.gamestate.my_ants()
        enemy_ants = self.gamestate.enemy_ants()
        threat_distance = self.gamestate.attackradius2
        influence_by_threat = battle_influence.get_influence_by_threat(self.gamestate, my_ants, enemy_ants, threat_distance)
        combat_scores = battle_influence.get_combat_scores(self.gamestate, my_ants, enemy_ants, influence_by_threat, threat_distance)

        # print (influence_by_threat)
        # print (combat_scores)
        self.assertTrue(combat_scores[(3,4)] > combat_scores[(3,5)])
        self.assertTrue(combat_scores[(4,3)] > combat_scores[(4,4)])
        self.assertTrue(combat_scores[(5,2)] == combat_scores[(5,3)])

    def test_get_combat_scores_4(self):
        """
 23456789
2.b.b..
3..b.b.
4......
5......
6....a.
7......
        """
        data = """
turn 1
a 2 3 1 
a 3 5 1 
a 3 4 1 
a 3 6 1 
a 6 6 0
go
        """
        self.gamestate.update(data)
        my_ants = self.gamestate.my_ants()
        enemy_ants = self.gamestate.enemy_ants()
        threat_distance = self.gamestate.attackradius2
        influence_by_owner = battle_influence.get_influence_by_owner(self.gamestate, my_ants, enemy_ants, threat_distance)
        influence_by_threat = battle_influence.get_influence_by_threat(self.gamestate, my_ants, enemy_ants, threat_distance)
        combat_scores = battle_influence.get_combat_scores(self.gamestate, my_ants, enemy_ants, influence_by_threat, threat_distance)

        print("")
        print(influence_by_owner[0])
        print("")
        print(influence_by_owner[1])

if __name__ == '__main__':
    unittest.main()