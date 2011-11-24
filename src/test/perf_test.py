# perf_test.py: performance test functions
#
# AI bot written for AI Challenge 2011 - Ants
# Author: Bill Y
# License: all your base are belong to us

import os, sys, numpy, timeit

def linear_inf_test():
    setup = """
import os, sys
cmd_folder = os.path.dirname(os.path.abspath('.'))
if cmd_folder not in sys.path:
    sys.path.insert(0, cmd_folder)
from cython_ext2 import merge_linear_map, merge_linear_map2
import numpy as np
rows = cols = 150
layers = 10
inf_map = np.zeros((rows,cols))
temp_maps = []
#np_temp_maps = np.ndarray(layers, rows, cols)
for i in range(layers):
    temp_maps.append(np.random.randint(10, size=(rows,cols)))
np_temp_maps = np.array(temp_maps)    
    """
    s1 = """
for row in range(rows):
    for col in range(cols):
        buffer = np_temp_maps[:,row,col]
        inf_map[row,col] = min(buffer) + 0.001 * sum(buffer)
    """
    t1 = timeit.Timer(s1, setup)
    print 't1.timeit'
    print t1.timeit(number=10)
    
    s2 = 'merge_linear_map(np_temp_maps, inf_map)'
    t2 = timeit.Timer(s2, setup)
    print 't2.timeit'
    print t2.timeit(number=10)

    s3 = 'merge_linear_map2(np_temp_maps, inf_map)'
    t3 = timeit.Timer(s3, setup)
    print 't3.timeit'
    print t3.timeit(number=10)

def inf_test():
    setup = """
import profiler
inf1, inf2, inf3 = profiler.setup_inf()
    """
    s1 = 'inf1.diffuse()'
    t1 = timeit.Timer(s1, setup)
    print 't1.timeit'
    print t1.timeit(number=10)
    
    s2 = 'inf2.diffuse()'
    t2 = timeit.Timer(s2, setup)
    print 't2.timeit'
    print t2.timeit(number=10)  
    
    s3 = 'inf3.diffuse()'
    t3 = timeit.Timer(s3, setup)
    print 't3.timeit'
    print t3.timeit(number=10)  
    

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

    
if __name__ == '__main__':
    linear_inf_test()
    #inf_test()
    #distance_test()
    #get_combat_zone_test()
