"""Module dependency graphs
"""

from types import ModuleType
import sys
from warnings import warn
from . import walk_modules, walker_method, make_walker_method_list

__all__ = ['compute_mdg']

# It was surprising to me that modules are hashable, so let's check
# that assertion in case it stops being true and breaks all this code.
#
assert hasattr(sys, '__hash__'), "Modules need to be hashable"

mdg_methods = make_walker_method_list(defaults=True)

@walker_method(methods_list=mdg_methods)
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

def compute_mdg(modules=sys.modules, maxdepth=100, check=True):
    # Walk modules and return a dict which maps from modules to
    # (frozen) sets of dependencies of them.

    # Modules are hashable, surprisingly, and we have checked this
    # above.  So we don't need id-related hair
    # 
    mdeps = {}                  # module -> dependency set
    
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
            # (this probes mdeps once or twice, and stores once.
            # Without the temporary variable it would probe two or
            # three times and store once.  I know: who cares?)
            if thing in mdeps:
                # seen before: our dependencies are the union of our
                # existing ones and any new ones, less us
                mydeps = mdeps[thing].union(deps).difference([thing])
            else:
                # first time: our dependencies are those we got, less
                # us.
                mydeps = deps.difference([thing])
            mdeps[thing] = mydeps
            return mydeps.union([thing])
        else:
            # not a module, just return unchanged
            return deps
    
    walk_modules(modules=modules, walkers=mdg_methods,
                 visitor=visit, fabricator=fabricate, combiner=combine,
                 maxdepth=maxdepth)
    
    if check:
        # Do some sanity checks: every module should be on the LHS of
        # a set, and no module should depend on itself.
        for (n, m) in modules.iteritems():
            if isinstance(m, ModuleType):
                assert m in mdeps, "{} missing from map".format(m.__name__)
        for (m, d) in mdeps.iteritems():
            assert m not in d, "{} has a dependency loop".format(m.__name__)
    
    return mdeps
