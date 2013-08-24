import os
import ctypes
import random
from ctypes import Structure, c_int, byref
here = os.path.dirname(os.path.realpath(__file__))
_lib = ctypes.CDLL(os.path.join(here, '_lib.so'))

class Point(Structure):
    _pt_fields = ['r', 'g', 'b', 'cluster', 'weight']
    _fields_ = [ (f, c_int) for f in _pt_fields]
    def __str__(self):
        fmt = "Point(r={}, g={}, b={}, cluster={}, weight={})"
        args = self.r, self.g, self.b, self.cluster, self.weight
        return fmt.format(*args)

def kmeans(points, k, seed=None):
    '''
    points is a list of (r, g, b, count) tuples, where each tuple is a color
        and the number of occurances of that color
    k is an integer

    example:
        points = [
            ( 91, 150, 200,   1),
            ( 31,  43, 253,   3),
            ( 63,  72, 106,  20),
            (243,  74, 115, 740),
        ]
        k = 5
        means = kmeans(points, k)
    '''
    if seed is not None:
        random.seed(seed)

    # Generate centers
    centers = random.sample(points, k)
    kpoints_array = Point * k
    lib_centers = kpoints_array()
    for i, center in enumerate(centers):
        r, g, b, count = center
        lib_centers[i] = Point(r=r, g=g, b=b, cluster=i, weight=count)
    pcenters = byref(lib_centers)

    # Generate points
    npoints = len(points)
    npoints_array = Point * npoints
    lib_points = npoints_array()
    for i, point in enumerate(points):
        r, g, b, count = point
        lib_points[i] = Point(r=r, g=g, b=b, cluster=-1, weight=count)
    ppoints = byref(lib_points)

    # Compute means
    _lib.kmeans(ppoints, npoints, pcenters, k)

    # Translate
    means = []
    for center in lib_centers:
        means.append([center.r, center.g, center.b])
    return means
