"""Walk functions for the Python walker.
"""

import sys
from . import walker

__all__ = ['TooDeep', 'walk_object', 'walk_modules']

class TooDeep(Exception):
    def __init__(self, what, depth=None):
        self.depth = depth
        self.what = what

    def __str__(self):
        return ("{0} (depth {1})".format(self.what, self.depth) if self.depth
                else self.what)


def walk_object(root, visitor=lambda o, d, p, n: d,
                fabricator=lambda o: None, combiner=lambda d1, d2: None,
                walkers=None, seen=None, maxdepth=100,
                root_parent=None, root_name=None):
    # Walk an object and its children.
    #
    # For an object which has not been seen already, each function in
    # walkers is called, and should return either an iterator over
    # (name, value) tuples, or None.  Each element of all the
    # iterators is walked recursively, with the results of the walk
    # being merged pairwise by the combiner function.  If the object
    # has already been seen, or there were no children (all of the
    # walkers return None), then some data is fabricated by calling
    # fabricator on the object.  Finally the visitor is called with
    # the object, the data from the children or the fabricator, the
    # parent object and the name in the parent, and its retuirn value
    # is the value of walk.
    #
    # For the root object the root_parent and root_name variables are
    # used as the parent and name-in-parent arguments.
    #
    # the seen argument is a set containing the id()s of object which
    # should be considered to have already been seen, or None.
    #
    # maxdepth says how deep to go before raising a TooDeep exception.
    #
    # There are defaults for the visitor, combiner and fabricator
    # which are uninteresting but mean you can call walk(thing) and it
    # will work to exercise the walkers.
    #
    # Note that this is a post-order walk: the object is visited after
    # its children.
    #
    # Note that objects which have already been visited are visited
    # again if they appear as children of other nodes, but their
    # children are then *not* visited.  This allows the graph of
    # dependencies to be stitched together without following loops
    # forever.
    #
    if walkers is None:
        walkers = walker.walker_methods

    if seen is None:
        seen = set()

    def walk_into(it, parent, name, depth):
        if depth >= maxdepth:
            raise TooDeep("too deep", depth)

        hashable = id(it)
        data = None
        seenp = False
        walked_children_p = False

        if hashable in seen:
            seenp = True
        else:
            seen.add(hashable)
            
        if not seenp:
            for walker in walkers:
                iterator = walker(it)
                if iterator:
                    for (n, v) in iterator:
                        walked_children_p = True
                        result = walk_into(v, it, n, depth + 1)
                        data = combiner(data, result) if data else result

        return visitor(it, data if walked_children_p else fabricator(it),
                       parent, name)

    return walk_into(root, root_parent, root_name, 0)

def walk_modules(visitor=lambda o, d, p, n: d,
                 fabricator=lambda o: None, combiner=lambda d1, d2: None,
                 walkers=None, seen=None, maxdepth=100,
                 root_parent=None, root_name=None, for_side_effect=False):
    seen = set() if not seen else seen
    def wlk(name, mod):
        return walk_object(mod, visitor=visitor,
                           fabricator=fabricator, combiner=combiner,
                           walkers=walkers, seen=seen, maxdepth=maxdepth,
                           root_parent=None, root_name=name)
    if for_side_effect:
        for (name, mod) in sys.modules.iteritems():
            wlk(name, mod)
        return None
    else:
        return [wlk(name, mod)
                for (name, mod) in sys.modules.iteritems()
                if mod]
