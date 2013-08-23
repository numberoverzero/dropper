import os
import time
import random
import webbrowser
from itertools import izip
from contextlib import contextmanager
from PIL import Image
INFINITY = float("Inf")


class Point(object):
    __slots__ = "rgb", "w", "i"

    def __init__(self, rgb, w, i):
        self.rgb = rgb
        self.w = w
        self.i = i

@contextmanager
def timer(msg=None):
    msg = msg or "Completed in {} seconds."
    start = time.clock()
    yield
    stop = time.clock()
    print msg.format(stop - start)

def full_render(src, dst, k, speed, min_diff):
    '''
    k is number of colors
    min_diff is termination point for clustering algorithm
    speed is inverse of quality - resolution is cut by speed ^ 2
    '''
    src = os.path.expanduser(src)
    dst = os.path.expanduser(dst)
    with timer("Full render: {}"):
        print "Getting colors"
        colors = dominant_colors(src, k, speed, min_diff)
        print "Rendering"
        render_colors(colors, src, dst)

def dominant_colors(path, k, speed, min_diff):
    print "Loading image"
    image = open_image(path, speed)
    print "Calculating points"
    pts = points(image)
    print "Calculating centers"
    centers = kmeans(pts, k, min_diff)
    print "Stepping values"
    return [map(int, center.rgb) for center in centers]

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
    pts = [Point(rgb=colors, w=count, i=-1) for count, colors in image.getcolors(w * h)]
    print "{} unique colors".format(len(pts))
    return pts

def kmeans(points, k, min_diff):
    '''Only returns centers, not clustered points'''
    # Initial centers
    centers = random.sample(points, k)

    iterations = 0
    while True:
        iterations += 1
        # Assignment step
        for point in points:
            min_dist = INFINITY
            for center_index, center in enumerate(centers):
                dist = distance2(point, center)
                if dist < min_dist:
                    min_dist = dist
                    point.i = center_index
        # Update step
        diff = 0
        for center_index in xrange(k):
            old = centers[center_index]
            cluster_points = [point for point in points if point.i == center_index]
            new = cluster_center(cluster_points)
            centers[center_index] = new
            diff = max(diff, distance2(old, new))
        if diff <= min_diff:
            break
    print "{} assign/update iterations".format(iterations)
    return centers

def distance2(p1, p2):
    return sum((p1.rgb[i] - p2.rgb[i]) ** 2 for i in xrange(3))

def cluster_center(points):
   n = sum(p.w for p in points)
   point_colors = list([p.w * p.rgb[0], p.w * p.rgb[1], p.w * p.rgb[2]] for p in points)
   vals = map(sum, izip(*point_colors))
   vals = [v / n for v in vals]
   return Point(rgb=vals, w=1, i=-1)

def clamp(x):
    return max(0, min(x, 255))

def rgb_to_hex(rgb):
    return "#{0:02x}{1:02x}{2:02x}".format(*rgb)


def render_colors(colors, src, dst):
    print "Loading template"
    base = os.path.join(here(), 'base.html')
    with open(base) as f:
        template = f.read()
    print "Creating divs"
    row = "<div class='box' style='background-color: {}'></div>"
    src_row = "<div class='box src'><img src='{}'></div>"
    print "Sorting by value"
    colors = value_sort(colors)
    print "Mapping to hex"
    colors = map(rgb_to_hex, colors)
    rows = [row.format(c) for c in colors]
    rows.append(src_row.format(src))
    pre, post = template.split("{{content}}")
    render = pre + '\n'.join(rows) + post
    print "Saving to file"
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
