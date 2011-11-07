from matplotlib import mpl,pyplot
import numpy as np
import pickle

import os, sys
cmd_folder = os.path.dirname(os.path.abspath('.'))
if cmd_folder not in sys.path:
    sys.path.insert(0, cmd_folder)

turn = sys.argv[1]
    
pickle_file = open('profiler_inf' + turn + '.influence', 'r')
inf = pickle.load(pickle_file)
pickle_file.close()
map_data = [[0 for col in range(inf.gamestate.cols)]
            for row in range(inf.gamestate.rows)]                    
for (row, col) in inf.map:
    map_data[row][col] = inf.map[(row, col)]

print(min(min(map_data)))
    
fig = pyplot.figure(2)

cmap2 = mpl.colors.LinearSegmentedColormap.from_list('my_colormap',
                                           ['blue','black','red'],
                                           256)
zvals = np.random.rand(100,100)*10-5
#print(zvals)
img2 = pyplot.imshow(map_data,interpolation='nearest',
                    vmin=-2, vmax=2,
                    cmap = cmap2,
                    origin='upper')

pyplot.colorbar(img2,cmap=cmap2)

pyplot.show()