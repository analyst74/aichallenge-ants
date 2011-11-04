# gamestate.py: stuff related to game state management, including I/O with game engine
#
# AI bot written for AI Challenge 2011 - Ants
# Author: Bill Y
# License: all your base are belong to us

import sys
import traceback
import random
import time
from core import *

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
        self.beaten_path = None
        self.hill_list = {}
        self.ant_list = {}
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
        # formation permutation counter, to be removed after profiling
        self.counter = 0

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
        self.map = [[LAND for col in range(self.cols)]
                    for row in range(self.rows)]
        self.beaten_path = [[0 for col in range(self.cols)]
                            for row in range(self.rows)]
                            
    def update(self, data):
        'parse engine input and update the game state'
        self.counter = 0
        
        # start timer
        self.turn_start_time = time.clock()
        
        # reset vision
        self.vision = None
        
        # reduce beaten path
        self.beaten_path = [[int(max(0, x-max(x/10,1))) for x in y] for y in self.beaten_path]
        
        # hill is slightly different, we do want to remember 
        # where hills are, so we know where to attack
        hills_to_remove = []
        for row, col in self.hill_list.keys():
            if self.map[row][col] != HILL:
                hills_to_remove.append((row,col))
        for loc in hills_to_remove:
            del self.hill_list[loc]

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
                    elif tokens[0] == 'f':
                        self.map[row][col] = FOOD
                        self.food_list.append((row, col))
                    else:
                        owner = int(tokens[3])
                        if tokens[0] == 'a':
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

    def time_remaining(self):
        return self.turntime - self.time_elapsed()
    
    def time_elapsed(self):
        return int(1000 * (time.clock() - self.turn_start_time))
    
    def issue_order(self, order):
        'issue an order by writing the proper ant location and direction'
        (row, col), direction = order
        #early exit
        if direction is None:
            self.ant_list[(row,col)] = (MY_ANT, True)
            logging.debug('moving %s -- stationary' % str((row, col)))
            return
        
        (newrow, newcol) = self.destination((row, col), direction)
        if self.is_passable((newrow, newcol)):
            sys.stdout.write('o %s %s %s\n' % (row, col, direction))
            sys.stdout.flush()
            logging.debug('moving %s to %s' % (str((row, col)), str((newrow, newcol))))
            # update ant moved flag
            del self.ant_list[(row,col)]
            self.ant_list[(newrow, newcol)] = (MY_ANT, True)
            # update map info (to avoid to ants moving into the same spot)
            self.map[newrow][newcol] = MY_ANT
            self.map[row][col] = LAND
            # set level of beaten path
            self.beaten_path[row][col] += 10
            # increase adjacent ones too
            for d in self.passable_directions((row, col)):
                (adj_row, adj_col) = self.destination((row, col), d)
                self.beaten_path[adj_row][adj_col] += 5
    
    def finish_turn(self):
        'finish the turn by writing the go line'
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
        
    def is_unoccupied(self, loc):
        'true if no ants are at the location'
        row, col = loc
        return self.map[row][col] in (LAND, DEAD)

    def is_my_unmoved_ant(self, loc):
        'true if is my ant, and is not moved'
        return loc in self.ant_list and self.ant_list[loc][0] == MY_ANT and self.ant_list[loc][1] == False
    
    def is_passable(self, loc):
        'true if not water or ant or food'
        row, col = loc
        return self.map[row][col] in (LAND, DEAD, HILL)
        
    def passable_directions(self, loc):
        'finds valid move from given location, based on passable'
        passable_directions = []
        for direction in ALL_DIRECTIONS:
            new_loc = self.destination(loc, direction)
            if (self.is_passable(new_loc)):
                passable_directions.append(direction)
                
        return passable_directions

    def destination(self, loc, direction):
        'calculate a new location given the direction and wrap correctly'
        row, col = loc
        d_row, d_col = AIM[direction]
        return ((row + d_row) % self.rows, (col + d_col) % self.cols)        

    def manhattan_distance(self, loc1, loc2):
        'calculate the manhattan distance between to locations'
        row1, col1 = loc1
        row2, col2 = loc2
        d_col = min(abs(col1 - col2), self.cols - abs(col1 - col2))
        d_row = min(abs(row1 - row2), self.rows - abs(row1 - row2))
        return d_row + d_col

    def euclidean_distance2(self, loc1, loc2):
        'calculate the euclidean distance between to locations'
        row1, col1 = loc1
        row2, col2 = loc2
        d_col = min(abs(col1 - col2), self.cols - abs(col1 - col2))
        d_row = min(abs(row1 - row2), self.rows - abs(row1 - row2))
        return d_row**2 + d_col**2
        
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

    # TODO: to be decomissioned after proper influence mapping is implemented
    def move_to_spot(self, loc, max_ant, max_search = 100):
        'find closet ant that belongs to self to a particular location'
        # return location of the first ant (after its move)
        first_ant_loc = None
        moved_ant_count = 0
        
        # http://en.wikipedia.org/wiki/Breadth-first_search#Pseudocode
        # create a queue Q
        list_q = deque()
        # enqueue (source, level) onto Q
        list_q.append(loc)
        # mark source
        marked_dict = { loc: True }
        
        search_count = 0
        while len(list_q) > 0:
            # limit max search depth and max ant moved
            if search_count > max_search or moved_ant_count > max_ant:
                break
            search_count += 1
            # dequeue an item from Q into v
            v = list_q.popleft()
            # for each edge e incident on v in Graph:
            for e in ALL_DIRECTIONS:
                # let w be the other end of e
                w = self.destination(v, e)
                # if w is not marked
                if w not in marked_dict:
                    # w must not be water
                    (w_row, w_col) = w
                    if self.map[w_row][w_col] != WATER:
                        # mark w
                        marked_dict[w] = True
                        # enqueue w onto Q
                        list_q.append(w)       
                        # break out if we find our own ant
                        if w in self.my_ants():
                            (owner, moved) = self.ant_list[w]
                            # if ant has not moved yet, use it
                            if not moved:
                                # only move in if target spot is move-in-able
                                # there is only one case where v is not passable
                                #   when it is the starting spot (i.e. hill raze leader)
                                if self.is_passable(v):
                                    self.issue_order((w, BEHIND[e]))
                                else:
                                    # stay stationary otherwise
                                    self.issue_order((w, None))
                                # set first ant
                                if first_ant_loc is None:
                                    first_ant_loc = w
                                # increment ant count
                                moved_ant_count += 1
                        
        return first_ant_loc  
    
    def visible(self, loc):
        ' determine which squares are visible to the given player '

        if self.vision == None:
            if not hasattr(self, 'vision_offsets_2'):
                # precalculate squares around an ant to set as visible
                self.vision_offsets_2 = []
                mx = int(sqrt(self.viewradius2))
                for d_row in range(-mx,mx+1):
                    for d_col in range(-mx,mx+1):
                        d = d_row**2 + d_col**2
                        if d <= self.viewradius2:
                            self.vision_offsets_2.append((
                                d_row%self.rows-self.rows,
                                d_col%self.cols-self.cols
                            ))
            # set all spaces as not visible
            # loop through ants and set all squares around ant as visible
            self.vision = [[False]*self.cols for row in range(self.rows)]
            for ant in self.my_ants():
                a_row, a_col = ant.loc
                for v_row, v_col in self.vision_offsets_2:
                    self.vision[a_row+v_row][a_col+v_col] = True
        row, col = loc
        return self.vision[row][col]
        
    def get_neighbour_locs(self, loc):
        'get all neighbour locations'
        return [self.destination(loc, direction) for direction in ALL_DIRECTIONS]
 
    def render_text_map(self):
        'return a pretty string representing the map'
        tmp = ''
        for row in self.map:
            tmp += '# %s\n' % ''.join([MAP_RENDER[col] for col in row])
        return tmp

    # static methods are not tied to a class and don't have self passed in
    # this is a python decorator
    @staticmethod
    def run(bot):
        'parse input, update game state and call the bot classes do_turn method'
        ants = GameState()
        map_data = ''
        while(True):
            try:
                current_line = sys.stdin.readline().rstrip('\r\n') # string new line char
                if current_line.lower() == 'ready':
                    ants.setup(map_data)
                    bot.do_setup(ants)
                    ants.finish_turn()
                    map_data = ''
                elif current_line.lower() == 'go':
                    ants.update(map_data)
                    # call the do_turn method of the class passed in
                    bot.do_turn(ants)
                    ants.finish_turn()
                    map_data = ''
                else:
                    map_data += current_line + '\n'
            except EOFError:
                break
            except KeyboardInterrupt:
                raise
            except:
                # don't raise error or return so that bot attempts to stay alive
                traceback.print_exc(file=sys.stderr)
                sys.stderr.flush()