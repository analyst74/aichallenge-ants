# gamestate.py: stuff related to game state management, including I/O with game engine
#
# AI bot written for AI Challenge 2011 - Ants
# Author: Bill Y
# License: all your base are belong to us

import sys, random, time, numpy as np
import cython_ext2
from core import *
from math import sqrt
from collections import defaultdict

PLAYER_ANT = 'abcdefghij'
HILL_ANT = string = 'ABCDEFGHI'
PLAYER_HILL = string = '0123456789'
MAP_OBJECT = '?%*.!'
MAP_RENDER = PLAYER_ANT + HILL_ANT + PLAYER_HILL + MAP_OBJECT


class GameState():
    def __init__(self):
        self.cols = None
        self.rows = None
        self.map = None
        # simplified nodes of if a map is explored
        # TODO: convert to boolean array instead of int
        self.region_map = None
        self.hill_list = {}
        self.ant_list = {}
        self.my_fighters = []
        self.my_combat_explorers = []
        self.water_list = {}
        self.dead_list = defaultdict(list)
        self.food_list = []
        self.turntime = 0
        self.loadtime = 0
        self.turn_start_time = None
        self.vision = None
        self.viewradius2 = 0
        self.attackradius2 = 0
        self.spawnradius2 = 0
        self.turns = 0
        self.current_turn = 0
        self.sqrt_table = {}
        self.neighbour_table = {}
        self.winning_percentage = 0.0
        self.vision_offsets_2 = []
        # move_table is in the format of destination_location:ant_location
        # using destination as key for faster invalid move check
        self.move_table = {}
        self.distance_table = {}

    def setup(self, data):
        'parse initial input and setup starting game state'
        for line in data.split('\n'):
            line = line.strip().lower()
            if len(line) > 0:
                tokens = line.split()
                key = tokens[0]
                if key == 'cols':
                    self.cols = int(tokens[1])
                elif key == 'rows':
                    self.rows = int(tokens[1])
                elif key == 'player_seed':
                    random.seed(int(tokens[1]))
                elif key == 'turntime':
                    # self.turntime = min(600, int(tokens[1]))
                    self.turntime = int(tokens[1])
                elif key == 'loadtime':
                    self.loadtime = int(tokens[1])
                elif key == 'viewradius2':
                    self.viewradius2 = int(tokens[1])
                elif key == 'attackradius2':
                    self.attackradius2 = int(tokens[1])
                elif key == 'spawnradius2':
                    self.spawnradius2 = int(tokens[1])
                elif key == 'turns':
                    self.turns = int(tokens[1])

        self.map = np.array([[LAND for col in range(self.cols)]
                    for row in range(self.rows)])
        self.region_map = np.zeros((int(self.rows/EXPLORE_GAP), int(self.cols/EXPLORE_GAP)))

        # setup neighbour table
        self.neighbour_table = {(row,col):[self.destination((row,col), direction) for direction in ALL_DIRECTIONS]
                                for row in xrange(self.rows)
                                for col in xrange(self.cols)}

        # precalculate squares around an ant to set as visible
        mx = int(sqrt(self.viewradius2))
        for d_row in range(-mx,mx+1):
            for d_col in range(-mx,mx+1):
                d = d_row**2 + d_col**2
                if d <= self.viewradius2:
                    self.vision_offsets_2.append((
                        d_row%self.rows-self.rows,
                        d_col%self.cols-self.cols
                    ))

        # for row in range(self.rows):
            # for col in range(self.cols):
                # self.distance_table[(row,col)] = np.zeros((self.rows, self.cols), dtype=int) + 100
                # for d_row in range(row-5, row+6):
                    # for d_col in range(col-5, col+6):
                        # d_row = d_row % self.rows
                        # d_col = d_col % self.cols
                        # self.distance_table[(row,col)][d_row, d_col] = \
                            # cython_ext2.euclidean_distance2(row, col, d_row, d_col, self.rows, self.cols)

    def update(self, data):
        'parse engine input and update the game state'
        # start timer
        self.turn_start_time = time.time()

        # reset vision
        self.vision = None

        # hill is slightly different, we do want to remember
        # where hills are, so we know where to attack
        #self.hill_list = {(row, col):self.hill_list[(row, col)] for (row, col) in self.hill_list
        #                if self.map[row][col] == HILL}

        # clear ant and food data
        for row, col in self.ant_list.keys():
            self.map[row][col] = LAND
        self.ant_list = {}

        for row, col in self.dead_list.keys():
            self.map[row][col] = LAND
        self.dead_list = defaultdict(list)

        for row, col in self.food_list:
            self.map[row][col] = LAND
        self.food_list = []

        # update map and create new ant and food lists
        for line in data.split('\n'):
            line = line.strip().lower()
            if len(line) > 0:
                tokens = line.split()
                if len(tokens) == 2:
                    # log current turn
                    self.current_turn = tokens[1]
                elif len(tokens) >= 3 and len(tokens[0]) == 1:
                    row = int(tokens[1])
                    col = int(tokens[2])
                    if tokens[0] == 'w':
                        self.map[row][col] = WATER
                        self.water_list[(row, col)] = 1
                    elif tokens[0] == 'f':
                        self.map[row][col] = FOOD
                        self.food_list.append((row, col))
                    else:
                        owner = int(tokens[3])
                        if tokens[0] == 'a':
                            # a hill got razed
                            if (row,col) in self.hill_list and owner != self.hill_list[(row,col)]:
                                del(self.hill_list[(row,col)])
                            self.map[row][col] = owner
                            self.ant_list[(row, col)] = (owner, False)
                        elif tokens[0] == 'd':
                            # food could spawn on a spot where an ant just died
                            # don't overwrite the space unless it is land
                            if self.map[row][col] == LAND:
                                self.map[row][col] = DEAD
                            # but always add to the dead list
                            self.dead_list[(row, col)].append(owner)
                        elif tokens[0] == 'h':
                            owner = int(tokens[3])
                            self.map[row][col] = HILL
                            self.hill_list[(row, col)] = owner
        # update explored region
        for loc in [(row, col) for row in range(self.region_map.shape[0])
                            for col in range(self.region_map.shape[1])]:
            if self.region_map[loc] == 0:
                real_loc = (loc[0] * EXPLORE_GAP, loc[1] * EXPLORE_GAP)
                # TODO: further optimize this stuff is needed?
                if real_loc in self.ant_list:
                    self.region_map[loc] = 1

    def time_remaining(self):
        return self.turntime - self.time_elapsed()

    def time_elapsed(self):
        return int(1000 * (time.time() - self.turn_start_time))

    def issue_order_by_location(self, ant, dest_loc):
        if self.is_passable(dest_loc):
            self.move_table[dest_loc] = ant
            self.ant_list[ant] = (MY_ANT, True)
        else:
            debug_logger.debug('ERROR: invalid move - destination %s for ant %s' % (str(dest_loc), str(ant)))

    def execute_orders(self):
        'issue an order by writing the proper ant location and direction'
        for dest_loc, ant in self.move_table.items():
            directions = self.direction(ant, dest_loc)
            row, col = ant
            if len(directions) > 0:
                sys.stdout.write('o %s %s %s\n' % (row, col, directions[0]))
                sys.stdout.flush()
        self.move_table = {}

    def finish_turn(self):
        'finish the turn by writing out the orders and go line'
        self.execute_orders()
        sys.stdout.write('go\n')
        sys.stdout.flush()

    def my_hills(self):
        return [loc for loc, owner in self.hill_list.items()
                    if owner == MY_ANT]

    def enemy_hills(self):
        return [(loc, owner) for loc, owner in self.hill_list.items()
                    if owner != MY_ANT]

    def my_ants(self):
        'return a list of all my ants'
        return [(row, col) for (row, col), (owner, moved) in self.ant_list.items()
                    if owner == MY_ANT]

    def my_unmoved_ants(self):
        'return a list of un-moved ants'
        return [(row, col) for (row, col), (owner, moved) in self.ant_list.items()
                    if owner == MY_ANT and not moved]

    def enemy_ants(self):
        'return a list of all visible enemy ants'
        return [((row, col), owner)
                    for (row, col), (owner, moved) in self.ant_list.items()
                    if owner != MY_ANT]

    def food(self):
        'return a list of all food locations'
        return self.food_list[:]

    def is_water(self, loc):
        (row, col) = loc
        return self.map[row][col] == WATER

    def is_passable(self, loc):
        ' un-passable tiles: water, food, enemy_ant, move_table'
        ' enemy ants'
        ' move_table destination (key) '
        return self.map[loc] not in (WATER, FOOD) and \
            (loc not in self.ant_list or self.ant_list[loc][0] == MY_ANT) and \
            loc not in self.move_table

    def is_passable_override(self, loc, unpassable_override, passable_override):
        'instead of simple passable, override with additional unpassable and passable locations'
        'note that unpassable_override takes precedence over passable_override'
        if loc in unpassable_override:
            return False
        elif loc in passable_override:
            return True
        else:
            return self.is_passable(loc)

    def all_moves(self, loc):
        return [l for l in [loc] + self.neighbour_table[loc]]

    def passable_moves(self, loc):
        return [l for l in [loc] + self.neighbour_table[loc] if self.is_passable(l)]

    def destination(self, loc, direction):
        'calculate a new location given the direction and wrap correctly'
        row, col = loc
        d_row, d_col = AIM[direction]
        return ((row + d_row) % self.rows, (col + d_col) % self.cols)

    def direction_row(self, loc, direction, distance):
        'get all tiles in given direction for given distance'
        row, col = loc
        d_row, d_col = AIM[direction]
        return [((row + d_row * i) % self.rows, (col + d_col*i) % self.cols) for i in xrange(distance)]

    def manhattan_distance(self, loc1, loc2):
        'calculate the manhattan distance between to locations'
        row1, col1 = loc1
        row2, col2 = loc2
        d_col = min(abs(col1 - col2), self.cols - abs(col1 - col2))
        d_row = min(abs(row1 - row2), self.rows - abs(row1 - row2))
        return d_row + d_col

    def euclidean_distance2_lookup(self, loc1, loc2):
        return self.distance_table[loc1][loc2]

    def euclidean_distance2(self, loc1, loc2):
        row1, col1 = loc1
        row2, col2 = loc2
        return cython_ext2.euclidean_distance2(row1, col1, row2, col2, self.rows, self.cols)

    def euclidean_distance_add(self, distance2, addition):
        'do euclidean math.add'
        distance = self.get_sqrt(distance2)
        return (distance+addition)**2

    def get_sqrt(self, num):
        if num not in self.sqrt_table:
            self.sqrt_table[num] = sqrt(num)
        return self.sqrt_table[num]

    def direction(self, loc1, loc2):
        'determine the 1 or 2 fastest (closest) directions to reach a location'
        row1, col1 = loc1
        row2, col2 = loc2
        height2 = self.rows//2
        width2 = self.cols//2
        d = []
        if row1 < row2:
            if row2 - row1 >= height2:
                d.append('n')
            if row2 - row1 <= height2:
                d.append('s')
        if row2 < row1:
            if row1 - row2 >= height2:
                d.append('s')
            if row1 - row2 <= height2:
                d.append('n')
        if col1 < col2:
            if col2 - col1 >= width2:
                d.append('w')
            if col2 - col1 <= width2:
                d.append('e')
        if col2 < col1:
            if col1 - col2 >= width2:
                d.append('e')
            if col1 - col2 <= width2:
                d.append('w')
        return d

    def visible(self, loc):
        ' determine which squares are visible to the given player '

        if self.vision == None:
            # set all spaces as not visible
            # loop through ants and set all squares around ant as visible
            self.vision = [[False]*self.cols for row in range(self.rows)]
            for ant in self.my_ants():
                a_row, a_col = ant
                for v_row, v_col in self.vision_offsets_2:
                    self.vision[a_row+v_row][a_col+v_col] = True
        row, col = loc
        return self.vision[row][col]

    def render_text_map(self):
        'return a pretty string representing the map'
        tmp = ''
        for row in self.map:
            tmp += '# %s\n' % ''.join([MAP_RENDER[col] for col in row])
        return tmp
