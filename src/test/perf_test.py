# perf_test.py: performance test functions
#
# AI bot written for AI Challenge 2011 - Ants
# Author: Bill Y
# License: all your base are belong to us

import os, sys, numpy, timeit, pickle
cmd_folder = os.path.dirname(os.path.abspath('.'))


def merge_map_test():
    setup = """
import os, sys
cmd_folder = os.path.dirname(os.path.abspath('.'))
if cmd_folder not in sys.path:
    sys.path.insert(0, cmd_folder)
from cython_ext2 import merge_linear_map
import numpy as np
rows = cols = 150
layers = 10
inf_map = np.zeros((rows,cols))
temp_maps = []
temp_maps2 = []
for i in range(layers):
    temp_map = np.random.randint(10, size=(rows,cols))
    temp_maps.append(temp_map)
    temp_maps2.append(list(temp_map))
np_temp_maps = np.array(temp_maps)    
    """
    s1 = """
for row in range(rows):
    for col in range(cols):
        buffer = np_temp_maps[:,row,col]
        inf_map[row,col] = min(buffer) + 0.001 * sum(buffer)
    """
    # t1 = timeit.Timer(s1, setup)
    # print 't1.timeit'
    # print t1.timeit(number=10)
    
    
    s4 = 'merge_linear_map_temp(np_temp_maps, inf_map)'
    t4 = timeit.Timer(s4, setup)
    print 't4.timeit  : ' + str(t4.timeit(number=10))

    s3 = 'merge_linear_map2(np_temp_maps, inf_map)'
    t3 = timeit.Timer(s3, setup)
    print 't3.timeit  : ' + str(t3.timeit(number=10))

    s2 = 'merge_linear_map(np_temp_maps, inf_map)'
    t2 = timeit.Timer(s2, setup)
    print 't2.timeit  : ' + str(t2.timeit(number=10))

    
def linear_map_set_test():
    setup = """
from profiler import setup_linear_inf
inf2, inf3a, inf3b = setup_linear_inf()
inf_value = -12
influence_sources = [((row,col), inf_value) for row in range(inf2.gamestate.rows) if row%25==0 
                                            for col in range(inf2.gamestate.cols) if col%20==0]
#print('total of %d influence sources' % len(influence_sources))
    """
    s2 = 'inf2.set_influence(influence_sources, lambda loc: loc in inf2.gamestate.my_unmoved_ants())'
    t2 = timeit.Timer(s2, setup)
    print 't2.timeit  : ' + str(t2.timeit(number=1))
    
    s3a = 'inf3a.set_influence(influence_sources, lambda loc: loc in inf2.gamestate.my_unmoved_ants())'
    t3a = timeit.Timer(s3a, setup)
    print 't3a.timeit : ' + str(t3a.timeit(number=1))
    
    s3b = 'inf3b.set_influence(influence_sources, True)'
    t3b = timeit.Timer(s3b, setup)
    print 't3b.timeit : ' + str(t3b.timeit(number=1))

def inf_test():
    setup = """
import profiler
inf1 = profiler.setup_inf()
    """
    s1 = 'inf1.diffuse()'
    t1 = timeit.Timer(s1, setup)
    print 't1.timeit'
    print t1.timeit(number=10)
    
    # s2 = 'inf2.diffuse()'
    # t2 = timeit.Timer(s2, setup)
    # print 't2.timeit'
    # print t2.timeit(number=10)  
    
    # s3 = 'inf3.diffuse()'
    # t3 = timeit.Timer(s3, setup)
    # print 't3.timeit'
    # print t3.timeit(number=10)  
    

def get_combat_zone_test():
    setup = """
import profiler
from combat import battle_line as battle1
from combat import battle_line2 as battle2
gs = profiler.setup_combat_zones()
    """
    s1 = 'battle1.get_combat_zones(gs)'
    s2 = 'battle2.get_combat_zones(gs)'
    t1 = timeit.Timer(s1, setup)
    t2 = timeit.Timer(s2, setup)
    print t1.timeit(number=10)
    print t2.timeit(number=10) 

    
def distance_test():
    setup = """
import profiler
gs = profiler.setup_combat_zones()
loc1 = (5,8)
loc2 = (10,10)
    """
    s1 = 'gs.euclidean_distance2(loc1, loc2)'
    s2 = 'gs.manhattan_distance(loc1, loc2)'
    t1 = timeit.Timer(s1, setup)
    t2 = timeit.Timer(s2, setup)
    print t1.timeit(number=10000)
    print t2.timeit(number=10000)  

def battle_line2_do_combat_test():
    pickle_file = open('test_data/battle_line2_profile/turn_270.gamestate', 'r')
    gamestate = pickle.load(pickle_file)
    pickle_file.close()
    
    battle.do_combat(gamestate)

if __name__ == '__main__':
    #linear_map_set_test()
    #merge_map_test()
    inf_test()
    #distance_test()
    #get_combat_zone_test()
