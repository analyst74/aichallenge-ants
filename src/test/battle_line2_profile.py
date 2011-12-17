# battle_line2_profile.py: performance profiler for battle_line2
#
# AI bot written for AI Challenge 2011 - Ants
# Author: Bill Y
# License: all your base are belong to us

import cProfile, os, sys, numpy, timeit
cmd_folder = os.path.dirname(os.path.abspath('.'))
if cmd_folder not in sys.path:
    sys.path.insert(0, cmd_folder)
import gamestate as gs, battle_line2 as battle

def setup_gamestate():
    gamestate = gs.GameState()
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
    gamestate.setup(setup_data)
    turn_data = """
turn 1
a 2 3 1
a 2 4 1
a 2 5 1
a 2 6 1
a 2 7 1
a 3 3 1
a 3 4 1
a 3 5 1
a 3 6 1
a 3 7 1
a 6 3 0
a 6 4 0
a 6 5 0
a 6 6 0
a 7 3 0
a 7 4 0
a 7 5 0
a 7 6 0
go
    """
    gamestate.update(turn_data)
    return gamestate

if __name__ == '__main__':
    gamestate = setup_gamestate()
    cProfile.run('battle.do_combat(gamestate)')