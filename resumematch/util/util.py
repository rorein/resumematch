from sys import stderr
from functools import partial

eprint = partial(print, file=stderr)
