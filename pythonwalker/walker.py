"""A walker method tells walk_object how to walk into other objects.

It should be a callable, which when called on an object returns either
an iterator over (name, value) pairs of its 'contents', or None if it
is not applicable.

There is a fallback list of walkers which is used if nothing else is
provided, and a list of default walkers which can be used to
initialise new lists.  Nothing should ever refer to these lists
directly.

make_walker_method_list will fabricate a new list, optionally copying
an existing one and populating it with defaults.  This list is always
fresh.

get_fallback_walker_method_list will get the fallback list,
set_fallback_walker_method_list will make fallback list be the list it
is given.  Neither of these functions makes a copy: if you modify the
list you get from or hand to them you modify the fallback list.

walker_method is a decorator which defines a walker method.  It has
two optional (keyword) arguments: the class this method applies to and
the list to put it on, with the default being the fallback list.

So

 @walker_method(for_class=t)
 def walk_t(it):
     ...

wraps walk_t in a conditional which checks that its argument is an
instance of t, and only calls it in that case and puts it onto the
fallback list.

 @walker_method()
 def walk_anything(it):
     ...

will cause walk_anything to be called on all objects visited, on the
fallback list.

 @walker_method(method_list=my_methods)
 def ...

will install the walker on my_methods.

This module currently adds a single entry to the fallback list itself,
which will walk the __dict__ slot of objects which have one (modules,
for instance): adding a default walker is, perhaps, wrong (but without
it you would not need the default walkers list at all).

"""

__all__ = ['walker_method', 'make_walker_method_list',
           'get_fallback_walker_method_list',
           'set_fallback_walker_method_list']

fallback_walker_method_list = []

# get and set the fallback list: this is a crappy API but, well.
#

def get_fallback_walker_method_list():
    return fallback_walker_method_list

def set_fallback_walker_method_list(l):
    global fallback_walker_method_list # Bloody Python
    fallback_walker_method_list = l

def make_walker_method_list(defaults=False, source=[]):
    # Return a fresh walker method list, copying source if given, and
    # adding defaults, uniquely, if given (even to a provided list).
    #
    l = [m for m in source]
    if defaults:
        if len(l) == 0:
            return [m for m in default_walker_method_list]
        else:
            for m in default_walker_method_list:
                # I know this is quadratic: walker method lists are short.
                if m not in l:
                    l.append(m)
            return l
    else:
        return l

def walker_method(for_class=object, methods_list=None):
    """A decorator to add something to the default walker methods,
    selecting on class
    """
    if methods_list is None:    # handle early binding of defaults
        methods_list = fallback_walker_method_list
    def wrap(walker):
        # wrap a walker with a function which checks the type of the
        # thing to be walked against for_class, and calls the walker
        # if it is an instance.
        methods_list.append((lambda thing:
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

# This is the standard set
default_walker_method_list = [m for m in fallback_walker_method_list]

