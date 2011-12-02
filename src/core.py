# core.py: core functions, definitions and such
#
# AI bot written for AI Challenge 2011 - Ants
# Author: Bill Y
# License: all your base are belong to us


import logging
#logging.basicConfig(level=debug_logger.debug)
debug_logger = logging.getLogger('debug')
debug_logger.addHandler(logging.FileHandler('debug.log', 'w'))
debug_logger.setLevel(logging.DEBUG)
debug_logger.propagate = False
perf_logger = logging.getLogger('performance')
perf_logger.addHandler(logging.FileHandler('performance.log', 'w'))
perf_logger.setLevel(logging.DEBUG)
perf_logger.propagate = False

HILL = 20
# enemy number will range from 1 to n-1, where n is total number of players on map
MY_ANT = 0
DEAD = -1
LAND = -2
FOOD = -3
WATER = -4

DECAY_RATE = 0.9
CUTOFF = 0.0001
EXPLORE_GAP = 20
FOOD_WEIGHT = 100000
RAZE_WEIGHT = 100
DEFENSE_WEIGHT = 100

AIM = {'n': (-1, 0),
       'e': (0, 1),
       's': (1, 0),
       'w': (0, -1)}
RIGHT = {'n': 'e',
         'e': 's',
         's': 'w',
         'w': 'n'}
LEFT = {'n': 'w',
        'e': 'n',
        's': 'e',
        'w': 's'}
BEHIND = {'n': 's',
          's': 'n',
          'e': 'w',
          'w': 'e'}

ALL_DIRECTIONS = ['n', 'e', 's', 'w']
