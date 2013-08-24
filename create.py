"""Dropper.

Usage:
  create.py <src> <dst> [--colors=<COLORS>] [--seed=<SEED>]

Options:
  -h --help                    Show this screen.
  -c COLORS --colors=<COLORS>  Number of generated colors.  [default: 5]
  -s SEED --seed=<SEED>        Seed for initial mean selection. [default: 12345]
"""
from dropper import full_render
from docopt import docopt

if __name__ == '__main__':
    arguments = docopt(__doc__)
    src = arguments['<src>']
    dst = arguments['<dst>']
    k = max(1, int(arguments['--colors']))
    seed = int(arguments['--seed'])
    full_render(src, dst, k, seed)
