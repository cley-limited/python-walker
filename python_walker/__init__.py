"""The Python walker.
"""

# This package is essentially a conduit for a couple of submodules, so
# it imports them and then reimports * from them.  The only reason for
# importing them in fact is so that the full names of things exist.
#
# The dotty imports ensure that things come from here:
#
#  from . import x
#
# is a sure way of making sure we get x.py from the directory of this
# package, and similarly
#
#  from .x import *
#
# makes sure we are importing everything that x.py exports (I think
# that, once you've said 'from . import x' you could just say 'from x
# import *', but NumPy does this more explicit thing and perhaps has
# good reason to do so).
#
# (this is pretty much what my CL conduits thing did: import a bunch
# of stuff and then reexport it, although this is at object level not
# symbol level:
#
#  (eq 'python_walker.walk_object 'python_walker.walk.walk_object)
#
# would be false if this was Lisp)
#
# Note that mdg and mt are *not* imported
#
from . import low
from .low import *
from . import walker
from .walker import *
from . import walk
from .walk import *
