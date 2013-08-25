import os
import time
import webbrowser
from kmeans import kmeans
from contextlib import contextmanager
from PIL import Image

@contextmanager
def timer(msg=None):
    msg = msg or "Completed in {} seconds."
    start = time.clock()
    yield
    stop = time.clock()
    print msg.format(stop - start)

def full_render(src, dst, k):
    '''
    k is number of colors
    min_diff is termination point for clustering algorithm
    speed is inverse of quality - resolution is cut by speed ^ 2
    '''
    src = os.path.expanduser(src)
    dst = os.path.expanduser(dst)
    with timer("Full render: {}"):
        colors = dominant_colors(src, k)
        render_colors(colors, src, dst)

def dominant_colors(path, k):
    with timer("Image loaded: {}"):
        image = Image.open(path)
    with timer("Transform points: {}"):
        pts = points(image)
    with timer("Calculate centers: {}"):
        centers = kmeans(pts, k)
    return centers

def points(image):
    w, h = image.size
    points = [(rgb, count) for count, rgb in image.getcolors(w * h)]
    print "{} unique colors".format(len(points))
    return points

def clamp(x):
    return max(0, min(x, 255))

def rgb_to_hex(rgb):
    return "#{0:02x}{1:02x}{2:02x}".format(*rgb)

def render_colors(colors, src, dst):
    with timer("Save Image: {}"):
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
