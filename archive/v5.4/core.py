# core.py: core functions, definitions and such
#
# AI bot written for AI Challenge 2011 - Ants
# Author: Bill Y
# License: all your base are belong to us

from collections import defaultdict, deque
from math import sqrt

import logging
DEBUG_LOG_NAME = 'debug.log'
#logging.basicConfig(filename=DEBUG_LOG_NAME,level=logging.DEBUG,filemode='w')

HILL = 20
# enemy number will range from 1 to n-1, where n is total number of players on map
MY_ANT = 0
DEAD = -1
LAND = -2
FOOD = -3
WATER = -4

STRAT_DECAY = 0.8

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
