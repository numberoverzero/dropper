import os
import time
import webbrowser
from contextlib import contextmanager
from dropper import lib
from PIL import Image

@contextmanager
def timer(msg=None):
    msg = msg or "Completed in {} seconds."
    start = time.clock()
    yield
    stop = time.clock()
    print msg.format(stop - start)

def full_render(src, dst, k, seed):
    '''
    k is number of colors
    min_diff is termination point for clustering algorithm
    speed is inverse of quality - resolution is cut by speed ^ 2
    '''
    src = os.path.expanduser(src)
    dst = os.path.expanduser(dst)
    with timer("Full render: {}"):
        colors = dominant_colors(src, k, seed)
        render_colors(colors, src, dst)

def dominant_colors(path, k, seed):
    print "Loading image"
    image = Image.open(path)
    print "Calculating points"
    pts = points(image)
    print "Calculating centers"
    centers = lib.kmeans(pts, k, seed)
    return centers

def points(image):
    points = []
    w, h = image.size
    for count, colors in image.getcolors(w * h):
        rgbc = list(colors)
        rgbc.append(count)
        points.append(rgbc)
    return points

def clamp(x):
    return max(0, min(x, 255))

def rgb_to_hex(rgb):
    return "#{0:02x}{1:02x}{2:02x}".format(*rgb)

def render_colors(colors, src, dst):
    print "Saving Image"
    base = os.path.join(here(), 'base.html')
    with open(base) as f:
        template = f.read()
    row = "<div class='box' style='background-color: {}'></div>"
    src_row = "<div class='box src'><img src='{}'></div>"
    colors = value_sort(colors)
    colors = map(rgb_to_hex, colors)
    rows = [row.format(c) for c in colors]
    rows.append(src_row.format(src))
    pre, post = template.split("{{content}}")
    render = pre + '\n'.join(rows) + post
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
