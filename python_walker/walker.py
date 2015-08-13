"""A walker method tells walk_object how to walk into other objects.

It should be a callable, which when called on an object returns either
an iterator over (name, value) pairs of its 'contents', or None if it
is not applicable.

There is a default list, walker_methods and this can be added to by
using the @walker_method decorator.

This module currenttly adds a single entry to walker_methods itself, which
will walk the __dict__ slot of objects which have one (modules, for
instance): adding a default walker is, perhaps, wrong.
"""

__all__ = ['walker_method', 'walker_methods']

walker_methods = []

def walker_method(thing):
    """A decorator to add something to the default walker methods."""
    walker_methods.append(thing)
    return thing

# The default walker method
#
# (I am not sure there should be one.)
#
# It is tempting to think that walking the dir() of an object is the
# right answer rather than this hack: it isn't.  If you walk dir() you
# end up with a vast stack of objects which I think Python is
# inventing on the fly (method wrappers), so without some
# type-specific hack ('only walk types we are interested in') you end
# up doomed.
#
# walking only particular types might be the right answer though.
#

@walker_method
def walk_dict(thing):
    if hasattr(thing, '__dict__'):
        return thing.__dict__.iteritems()
    else:
        return None
