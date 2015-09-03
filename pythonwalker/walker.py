"""A walker method tells walk_object how to walk into other objects.

It should be a callable, which when called on an object returns either
an iterator over (name, value) pairs of its 'contents', or None if it
is not applicable.

There is a default list, walker_methods and this can be added to by
using the @walker_method decorator, which supports dispatcing on type:

 @walker_method(t)
 def walk_t(it):
     ...

wraps walk_t in a conditional which checks that its argument is an instance of t, and only calls it in that case.  By default t is object:

 @walker_method()
 def walk_anything(it):
     ...

will cause walk_anything to be called on all objects visited.

This module currently adds a single entry to walker_methods itself, which
will walk the __dict__ slot of objects which have one (modules, for
instance): adding a default walker is, perhaps, wrong.

Indeed it's not really clear that the whole notion of a default list
of walker methods is right.
"""

__all__ = ['walker_method', 'walker_methods']

walker_methods = []

def walker_method(for_class=object):
    """A decorator to add something to the default walker methods,
    selecting on class
    """
    def wrap(walker):
        # wrap a walker with a function which checks the type of the
        # thing to be walked against for_class, and calls the walker
        # if it is an instance.
        walker_methods.append((lambda thing:
                                   (walker(thing)
                                    if isinstance(thing, for_class)
                                    else None)))
        return walker
    return wrap

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

@walker_method()
def walk_dict(thing):
    if hasattr(thing, '__dict__'):
        return thing.__dict__.iteritems()
    else:
        return None
