from matplotlib import mpl,pyplot
import numpy as np
import pickle

import os, sys

cmd_folder = os.path.abspath('../../src')
if cmd_folder not in sys.path:
    sys.path.insert(0, cmd_folder)

turn = sys.argv[1]
if len(sys.argv) == 3:
    edge = float(sys.argv[2])
else:
    edge = 2
    
pickle_file = open('../../src/pickle/turn_' + turn + '.influence', 'r')
inf = pickle.load(pickle_file)
pickle_file.close()
map_data = [[0 for col in range(inf.gamestate.cols)]
            for row in range(inf.gamestate.rows)]                    
for row in range(inf.map.shape[0]):
    for col in range(inf.map.shape[1]):
        map_data[row][col] = inf.map[row, col]

print(min(sum(map_data, [])))
print(max(sum(map_data, [])))
    
fig = pyplot.figure(2)

cmap2 = mpl.colors.LinearSegmentedColormap.from_list('my_colormap',
                                           ['blue','black','red'],
                                           256)

img2 = pyplot.imshow(map_data,interpolation='nearest',
                    vmin=-edge, vmax=edge,
                    cmap = cmap2,
                    origin='upper')

pyplot.colorbar(img2,cmap=cmap2)

pyplot.show()