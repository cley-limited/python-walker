"""Module dependency graphs
"""

from types import ModuleType
import sys
from warnings import warn
from . import walk_modules, walker_method

__all__ = ['compute_mdgi', 'compute_mdg']

@walker_method()
def walk__module__(thing):
    # a walker for things with '__module__' attributes.
    if hasattr(thing, '__module__'):
        name = thing.__module__
        if name in sys.modules and sys.modules[name] is not None:
            return ((name, sys.modules[name]),) # Oh, Python
        else:
            return None
    else:
        return None

def compute_mdgi(modules=None, maxdepth=100, check=True):
    # Walk modules and return a tuple (id2m, id2deps) where id2m maps
    # ids to module instances, and id2deps maps module ids to (frozen)
    # sets of dependency ids.

    if modules is None:
        modules = sys.modules
    
    # Everything has to work in terms of ids, as Python's hash tables
    # are as deficient as you would expect: lots of things are not
    # hashable even though they have ids which never change and which
    # are hashable (yes, I know, the id can be reused).  See the CLHS
    # for how to do this right.
    #
    id2module = {}              # maps ids to module instances
    id2deps = {}                # maps ids to dependency sets
    
    def fabricate(thing):
        # by default, a thing depends on nothing.  Using frozen sets
        # helps avoid mutability problems: once we have a set of
        # dependencies we can safely stash it without worrying that
        # someone else might modify it.
        #
        return frozenset()

    def combine(s1, s2):
        # Combine two dependency sets: just take the union
        assert s1 is not None and s2 is not None, "None to combine?"
        return s1.union(s2)

    def visit(thing, deps, parent, name):
        # The visitor.  This is only interested in modules (I wish I
        # had defmethod).  The aim is to stash the dependencies of a
        # module, making sure it does not include the module itself
        # which it may do (because ts.x.__module__ is often ts), and
        # return the set of dependencies of things which depend on
        # this module, which is the same set but with the module
        # added.
        #
        assert deps is not None, "no dependencies?"
        if isinstance(thing, ModuleType):
            i = id(thing)
            # (This does 0 or 1 lookups in id2deps and 1 store.
            # Without mydeps it would do 1 or 2 lookups and 1 store.
            # I know: who cares?)
            if i in id2module:
                # seen before: our dependencies are the union of our
                # existing ones and any new ones, less us
                mydeps = id2deps[i].union(deps).difference([i])
            else:

                # first time: we need to seed the id map and our
                # dependencies is deps less us
                id2module[i] = thing
                mydeps = deps.difference([i])
            # stash dependencies and return them with us added
            id2deps[i] = mydeps
            return mydeps.union([i])
        else:
            # not a module, just return unchanged
            return deps
    
    walk_modules(modules=modules,
                 visitor=visit, fabricator=fabricate, combiner=combine,
                 maxdepth=maxdepth)
    
    if check:
        # every module's id should be in the maps, and every entry in
        # a dependency set should be in the id map (which is complete
        # because we are checking it here!)
        for (n, m) in modules.iteritems():
            if m:
                i = id(m)
                assert i in id2module, "{} missing in id map".format(m.__name__)
                assert i in id2deps, "{} missing in dep map".format(m.__name__)
                for d in id2deps[i]:
                    # yes, a backslash continuation line
                    assert d in id2module, \
                        "{} missing in deps of {}".format(d, m.__name__)
    
    return (id2module, id2deps)

def compute_mdg(modules=None, id2module=None, id2deps=None):
    assert ((id2module and id2deps)
            or (id2module is None
                and id2deps is None)), "neither or both, not one"
    if id2module is None or id2deps is None:
        (id2module, id2deps) = compute_mdgi(modules=modules)
    return tuple(((id2module[i], tuple((id2module[d] for d in ds)))
                 for (i, ds) in id2deps.iteritems()))
