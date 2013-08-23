"""Dropper.

Usage:
  create.py <src> <dst> [--colors=<COLORS>] [--speed=<SPEED>] [--min-delta=<DELTA>]

Options:
  -h --help                    Show this screen.
  -c COLORS --colors=<COLORS>  Number of generated colors.  [default: 5]
  -s SPEED --speed=<SPEED>     Inverse scale factor.  1 is no scaling, 2 cuts dimensions in half, etc. [default: 2]
  --min-delta=<DELTA>          Center drift cutoff to terminate k-mean algorithm.  Small numbers are slower, less variance.  [default: 1]
"""
from dropper import full_render
from docopt import docopt

if __name__ == '__main__':
    arguments = docopt(__doc__)

    src = arguments['<src>']
    dst = arguments['<dst>']
    k = max(1, int(arguments['--colors']))
    min_diff = max(0, float(arguments['--min-delta']))
    speed = max(1, int(arguments['--speed']))

    full_render(src, dst, k, speed, min_diff)
