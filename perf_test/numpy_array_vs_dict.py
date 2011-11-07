import timeit


def dict_v_numpy_copy():
    setup = """
import numpy
src1 = {(x,y):0.0 for x in xrange(100) for y in xrange(100)}
src2 = numpy.zeros((100, 100))    
    """
    s1 = """
dest = {}
for key in src1:
    dest[key] = src1[key]
    """
    s2 = 'dest = numpy.copy(src2)'
    t1 = timeit.Timer(s1, setup)
    t2 = timeit.Timer(s2, setup)
    runtime = 100
    print "%.2f usec/%d pass" % (runtime * t1.timeit(number=runtime), runtime)
    print "%.2f usec/%d pass" % (runtime * t2.timeit(number=runtime), runtime)

def dict_v_numpy_access():
    setup = """
import numpy
src1 = {(x,y):0.0 for x in xrange(100) for y in xrange(100)}
src2 = numpy.zeros((100, 100))    
    """
    s1 = 'src1[(5,20)]'
    s2 = 'src2[(5,20)]'
    t1 = timeit.Timer(s1, setup)
    t2 = timeit.Timer(s2, setup)
    runtime = 10000
    print "%.2f usec/%d pass" % (runtime * t1.timeit(number=runtime), runtime)
    print "%.2f usec/%d pass" % (runtime * t2.timeit(number=runtime), runtime)

def addition():
    setup = """\
import numpy
def list_test(list, x, y):
    for i in xrange(x):
        for j in xrange(y):
            list[x][y] += 1
def numpy_test(arr, x, y):
    for i in xrange(x):
        for j in xrange(y):
            arr[x,y] +=  1
            
def dict_test(dict, x, y):
    for i in xrange(x):
        for j in xrange(y):
            dict[(x,y)] += 1
x = 1000
y = x + 1
list = [[0]*y]*y
arr = numpy.zeros((y,y))
dict = {(i,j): 0 for i in xrange(y) for j in xrange(y)}
    """
    runtime = 10
    t0 = timeit.Timer("list_test(list, x, x)", setup)
    print "%.2f usec/pass" % (runtime * t0.timeit(number=runtime)/runtime)
    #1.64 usec/pass
    t1 = timeit.Timer("numpy_test(arr, x, x)", setup)
    print "%.2f usec/pass" % (runtime * t1.timeit(number=runtime)/runtime)
    #18.13 usec/pass
    t2 = timeit.Timer("dict_test(dict, x, x)", setup)
    print "%.2f usec/pass" % (runtime * t2.timeit(number=runtime)/runtime)
    #4.51 usec/pass

    
if __name__ == '__main__':
    dict_v_numpy_copy()