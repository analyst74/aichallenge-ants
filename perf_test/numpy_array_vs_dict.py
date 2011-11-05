import timeit

if __name__ == '__main__':
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
