# diffuse_c.pyx: diffusion implemented in Cython
#
# AI bot written for AI Challenge 2011 - Ants
# Author: Bill Y
# License: all your base are belong to us
#
# cython: profile=True

import numpy as np
cimport numpy as np
from core import WATER

DTYPEF = np.float
ctypedef np.float_t DTYPEF_t
DTYPEI = np.int
ctypedef np.int_t DTYPEI_t

ALL_DIRECTIONS = ['n', 'e', 's', 'w']
AIM = {'n': (-1, 0),
       'e': (0, 1),
       's': (1, 0),
       'w': (0, -1)}

def diffuse_once(np.ndarray[DTYPEF_t, ndim=2] inf_map, np.ndarray[DTYPEI_t, ndim=2] gs_map, float cutoff):
    'diffuse inf_map'
    assert inf_map.dtype == DTYPEF and gs_map.dtype == DTYPEI
    cdef int rows = inf_map.shape[0]
    cdef int cols = inf_map.shape[1]
    cdef int row = 0
    cdef int col = 0
    cdef int d_row = 0
    cdef int d_col = 0
    cdef DTYPEF_t diffuse_value
    cdef int neighbour_count = 0
    cdef np.ndarray[DTYPEF_t, ndim=2] buffer = np.zeros([rows, cols], dtype=DTYPEF)
    #cdef char* direction
    #buffer = np.zeros([rows,cols])

    # find surrounding non-water nodes and diffuse to them
    for row in range(rows):
        for col in range(cols):
            if gs_map[row,col] != WATER and (inf_map[row,col] > cutoff or inf_map[row,col] < -cutoff):
                diffuse_value = inf_map[row,col] * 0.15
                neighbour_count = 0
                for direction in ALL_DIRECTIONS:
                    d_row, d_col = destination(row, col, direction, rows, cols)
                    if gs_map[d_row,d_col] != WATER:
                        #print('%d,%d, gs_map = %s' % (d_row, d_col, str(gs_map[d_row,d_col])))
                        buffer[d_row,d_col] += diffuse_value
                        neighbour_count += 1

                if diffuse_value < 0:
                    # negative influences do not accumulate near water
                    buffer[row, col] += inf_map[row,col] - diffuse_value * 4
                else:
                    # positive influence accumulate near water, so ants are naturally repelled from edges
                    buffer[row, col] += inf_map[row,col] - diffuse_value * neighbour_count

    return buffer

cdef inline destination(int row, int col, char* direction, int rows, int cols):
    'calculate a new location given the direction and wrap correctly'
    cdef int d_row = 0
    cdef int d_col = 0
    d_row, d_col = AIM[direction]

    return (row + d_row) % rows, (col + d_col) % cols

def merge_linear_map(np.ndarray[DTYPEI_t, ndim=3] np_temp_maps, np.ndarray[DTYPEF_t, ndim=2] inf_map):
    cdef int rows = inf_map.shape[0]
    cdef int cols = inf_map.shape[1]
    cdef int row = 0
    cdef int col = 0
    cdef int i = 0
    cdef float min_val
    # magical large number
    cdef float magical_number = 99999
    for row in range(rows):
        for col in range(cols):
            loc_values = []
            min_val = magical_number
            for i in range(np_temp_maps.shape[0]):
                if np_temp_maps[i,row,col] < 0:
                    loc_values.append(np_temp_maps[i,row,col])
                    if loc_values[-1] < min_val:
                        min_val = loc_values[-1]
            if min_val < magical_number:
                inf_map[row,col] = min_val + 0.001 * sum(loc_values)

def euclidean_distance2(int row1, int col1, int row2, int col2, rows, cols):
    'calculate the euclidean distance between to locations'

    d_col = min(abs(col1 - col2), cols - abs(col1 - col2))
    d_row = min(abs(row1 - row2), rows - abs(row1 - row2))
    return d_row**2 + d_col**2
