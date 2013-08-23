import os
import time
import random
import webbrowser
from itertools import izip
from contextlib import contextmanager
from PIL import Image

INFINITY = float("Inf")

def full_render(src, dst, k, min_diff, speed):
    '''
    k is number of colors
    min_diff is termination point for clustering algorithm
    speed is inverse of quality - resolution is cut by speed ^ 2
    '''
    with timer("Full render: {}"):
        print "Getting colors"
        colors = dominant_colors(src, k, min_diff, speed)
        print "Rendering"
        render_colors(colors, dst)

@contextmanager
def timer(msg=None):
    msg = msg or "Completed in {} seconds."
    start = time.clock()
    yield
    stop = time.clock()
    print msg.format(stop - start)

def dominant_colors(path, k, min_diff, speed):
    path = os.path.expanduser(path)
    print "Loading image"
    image = open_image(path, speed)
    print "Calculating points"
    p = points(image)
    print "Calculating centers"
    centers = kmeans(p, k, min_diff)
    print "Stepping values"
    return [map(int, center[1]) for center in centers]

def open_image(path, speed):
    image = Image.open(path)
    w, h = image.size
    speed = float(speed)
    size = int(w / speed), int(h / speed)
    image.thumbnail(size)
    return image


def points(image):
    w, h = image.size
    print "{} pixels".format(w * h)
    pts = list(image.getcolors(w * h))
    print "{} unique colors".format(len(pts))
    return pts

def kmeans(points, k, min_diff):
    '''Only returns centers, not clustered points'''
    n = len(points)
    centers = list(random.sample(points, k))
    # Instead of appending lists all the time, just update which cluster a point is in
    cluster_point_map = [-1] * n
    iterations = 0
    while True:
        iterations += 1
        # Assignment step
        for point_index, p in enumerate(points):
            min_dist = INFINITY
            for cluster_index, cluster in enumerate(centers):
                dist = distance2(p, cluster)
                if dist < min_dist:
                    min_dist = dist
                    cluster_point_map[point_index] = cluster_index
        # Update step
        diff = 0
        for i in xrange(k):
            old = centers[i]
            #Generator
            i_points = [points[j] for j in xrange(n) if cluster_point_map[j] == i]
            new = center(i_points)
            centers[i] = new
            diff = max(diff, distance2(old, new))
        if diff <= min_diff:
            break
    print "{} assign/update iterations".format(iterations)
    return centers

def distance2(p1, p2):
    return sum((p1[1][i] - p2[1][i]) ** 2 for i in xrange(3))

def center(points):
   plen = sum(p[0] for p in points)
   point_colors = list([count*color[0], count*color[1], count*color[2]] for (count, color) in points)
   vals = map(sum, izip(*point_colors))
   vals = [v / plen for v in vals]
   return 1, vals

def clamp(x):
    return max(0, min(x, 255))

def rgb_to_hex(rgb):
    return "#{0:02x}{1:02x}{2:02x}".format(*rgb)


def render_colors(colors, dst):
    print "Loading template"
    src = os.path.join(here(), 'base.html')
    with open(src) as f:
        template = f.read()
    print "Creating divs"
    row = "<div class='box' style='background-color: {}'></div>"
    print "Sorting by value"
    colors = value_sort(colors)
    print "Mapping to hex"
    colors = map(rgb_to_hex, colors)
    rows = [row.format(c) for c in colors]
    pre, post = template.split("{{content}}")
    render = pre + '\n'.join(rows) + post
    print "Saving to file"
    dst = os.path.expanduser(dst)
    with open(dst, 'w') as f:
        f.write(render)
    webbrowser.open(dst)

def value_sort(colors):
    def score(color):
        color = map(clamp, color)
        s = sum(ch**2 for ch in color)
        return s, color
    scored = map(score, colors)
    scored.sort()
    return [s[1] for s in scored]

def here():
    return os.path.dirname(os.path.realpath(__file__))

if __name__ == "__main__":
    sample = "~/Downloads/rainforest.jpg"
    src = sample
    dst = "~/out.html"
    k = 4
    min_diff = 1
    speed = 1
    full_render(src, dst, k, min_diff, speed)
