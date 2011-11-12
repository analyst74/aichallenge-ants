# perf_test.py: performance test functions
#
# AI bot written for AI Challenge 2011 - Ants
# Author: Bill Y
# License: all your base are belong to us

import os, sys, numpy, timeit


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
    inf_test()
    #distance_test()
    #get_combat_zone_test()