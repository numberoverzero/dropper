import os
import time
import random
import webbrowser
from collections import namedtuple
from contextlib import contextmanager
from PIL import Image

Point = namedtuple("Point", ("coords", "count"))
Cluster = namedtuple("Cluster", ("points", "center"))

def full_render(src, dst, k, min_diff, speed):
    '''
    k is number of colors
    min_diff is termination point for clustering algorithm
    speed is inverse of quality - resolution is cut by speed ^ 2
    '''
    with timer():
        print "dst is: <{}>".format(dst)
        print "Getting colors"
        colors = dominant_colors(src, k, min_diff, speed)
        print "Rendering"
        render_colors(colors, dst)

@contextmanager
def timer():
    start = time.clock()
    yield
    stop = time.clock()
    print "Completed in {} seconds".format(stop - start)

def dominant_colors(path, k, min_diff, speed):
    print "Loading image"
    image = open_image(path, speed)
    print "Calculating points"
    p = points(image)
    print "Calculating clusters"
    clusters = kmeans(p, k, min_diff)
    print "Stepping values"
    return [map(int, c.center.coords) for c in clusters]

def open_image(path, speed):
    image = Image.open(os.path.expanduser(path))
    w, h = image.size
    speed = float(speed)
    size = int(w / speed), int(h / speed)
    image.thumbnail(size)
    return image


def points(image):
    w, h = image.size
    print "Sampling {} points".format(w * h)
    return [Point(color, count) for (count, color) in image.getcolors(w * h)]

def kmeans(points, k, min_diff):
    clusters = [Cluster([p], p) for p in random.sample(points, k)]
    while True:
        plists = [[] for i in xrange(k)]
        for p in points:
            min_dist = float("Inf")
            for i in range(k):
                dist = distance2(p, clusters[i].center)
                if dist < min_dist:
                    min_dist = dist
                    idx = i
            plists[idx].append(p)
        diff = 0
        for i in xrange(k):
            old = clusters[i]
            c = center(plists[i])
            new = Cluster(plists[i], c)
            clusters[i] = new
            diff = max(diff, distance2(old.center, new.center))
        if diff <= min_diff:
            break
    return clusters

def distance2(p1, p2):
    return sum((p1.coords[i] - p2.coords[i]) ** 2 for i in xrange(3))

def center(points):
   vals = [0.0 for i in range(3)]
   plen = 0
   for p in points:
           plen += p.count
           for i in range(3):
               vals[i] += (p.coords[i] * p.count)
   return Point([(v / plen) for v in vals], 1)

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
    k = 6
    min_diff = 1
    speed = 4
    full_render(src, dst, k, min_diff, speed)
