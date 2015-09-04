"""Python walker module tools
"""

import imp
import sys
from os.path import splitext, isabs, abspath
from types import ModuleType
from .low import Badness

__all__ = ['find_module_recursively',
           'module_attributions',
           'module_attributions_ok_p',
           'report_module_attributions',
           'clean_modules']

builtins = frozenset(sys.builtin_module_names)

def find_module_recursively(n, path=None):
    # find a dotty module using imp.find_module (which see), returning
    # a tuple of a path or name and the kind of module, or None.
    # Raise an exception if something really mutant happens (this
    # includes bogus arguments).
    #
    cpts = n.split(".")
    cptc = len(cpts)
    assert cptc > 0, "nothing in '{}'?".format(n)

    def loop(i, path):
        c = cpts[i]
        if i < cptc - 1:
            # this is not the last component: what we're looking for
            # is a package into which we can recurse
            try:
                # Look along the path we were given ...
                (f, p, (s, m, t)) = imp.find_module(c, path)
            except:
                # ... failing back to sys.path, which I think is safe.
                # if this fails then just fail (should this be an
                # error?)
                try:
                    (f, p, (s, m, t)) = imp.find_module(c, sys.path)
                except:
                    return None
            if p is not None and t == imp.PKG_DIRECTORY:
                # got a package, this is good (p is "", which is not
                # None, for a builtin, which we don't want)
                assert f is None, "horror"
                return loop(i + 1, [p]) # the package is now the path
            elif f is not None:
                # got a file: this should not happen as we are not at
                # the end
                f.close()
                raise Badness("got a file before the end")
            else:
                # got a builtin or something bad
                raise Badness("got a builtin before the end")
        else:
            # this is the last component: it might be a builtin: we
            # have to check for this since imp.find_module does not
            # seem to find them itself
            if c not in builtins:
                try:
                    # Look along the path we were given ...
                    (f, p, (s, m, t)) = imp.find_module(c, path)
                except:
                    # ... failing back to sys.path, which I think is safe.  If
                    # this fails there is no module
                    try:
                        (f, p, (s, m, t)) = imp.find_module(c, sys.path)
                    except:
                        return None
                if f is not None:
                    # module from a file, we win
                    f.close()
                    return (p, t)
                elif p is not None and t == imp.PKG_DIRECTORY:
                    # package (see above for why we test for t)
                    assert f is None, "horror"
                    return (p, t)
                else:
                    # something odd, but not an error
                    return (None, t)
            else:
                # c is in builtins: we'll just lie and pretend
                # imp.find_module did find it.
                return (c, imp.C_BUILTIN)

    return loop(0, path if path is not None else sys.path)


def module_attributions(modules=None):
    # sort out attributions for modules
    #
    # Return a tuple of 6 objects:
    # - a map from name to base (see below) for loaded modules
    #   this can be many to one (modules can have multiple names)
    # - a map from name to package dir for packages (also many to one)
    # - a list of names of weird modules: these don't have files and
    #   are typically built-in modules like sys
    # - a list of names of bogons: things which aren't modules at all
    # - a map of name to base (below) for unknown modules: they have files,
    #   but we can't find a module object.
    # - a list of names of modules we can't find anything about at all.
    #
    # If the last two elements of the tuple have anything in them then
    # there's probably trouble.  The bogon list often does have things
    # in it because, well, who would expect something called
    # sys.modules to have only modules in it?
    #
    # modules needs to implement iteritems() and agree with the
    # semantics of a dict for it (so the 0th elts of the tuples must
    # be unique, which this fn quietly assumes)
    #
    if modules is None:
        modules = sys.modules

    def pathbase(path):
        # the base of a path is an absolute version of it, without the
        # extension.  This is a hack to avoid having to worry about
        # whether x.py and x.pyc are the same (they are, but other
        # similar things might not be), by considering x.a to be the
        # same as x.b for all a and b.
        #
        return splitext(path if isabs(path) else abspath(path))[0]

    # Classify modules: they're either normal (have a base), weird
    # (exist but have no base) or missing altogether (there's a name,
    # but no module).
    #
    lmap = {}                   # name to base for loaded modules
    pmap = {}                   # name to base for packages
    umap = {}                   # name to base for unloaded modules
    bases = set()               # bases we have seen
    hopeless = []               # hopeless cases
    weird = []                  # names of weird modules
    bogus = []                  # names of bogons

    missed = []                # modules missed in first pass

    for (name, mod) in modules.iteritems():
        if mod:
            # There is something there
            if isinstance(mod, ModuleType):
                # it's a module
                if hasattr(mod, '__file__'):
                    # normal module
                    base = pathbase(mod.__file__)
                    bases.add(base)
                    lmap[name] = base
                else:
                    # a weird module
                    weird.append(name)
            else:
                # not a module at all (yes, this can happen)
                bogus.append(name)
        else:
            # missed on first pass
            missed.append(name)

    # Now have a look at the missed modules
    for name in missed:
        found = find_module_recursively(name)
        if found:
            # we got something, anyway
            (p, t) = found
            if t == imp.C_BUILTIN:
                # a weird thing
                weird.append(name)
            elif t == imp.PKG_DIRECTORY:
                # a package
                pmap[name] = p
            else:
                # check whether we've seen the base
                base = pathbase(p)
                if base in bases:
                    # it is something we have seen
                    lmap[name] = base
                else:
                    # it's not (this is unexpected)
                    umap[name] = p
        else:
            # got nothing at all
            hopeless.append(name)
    return (lmap, pmap, weird, bogus, umap, hopeless)

def module_attributions_ok_p(modules=None):
    # are the module attributuons OK?
    (lmap, pmap, weird, umap, hopeless) = module_attributions(modules)
    if len(umap) == 0 and len(hopeless) == 0:
        return True
    else:
        return False

def report_module_attributions(modules=None, out=sys.stdout):
    # Just print the results of the module_attributions
    #

    def lem(m):
        # little-endian module name: sorting using this as a key puts
        # things which are probably related near each other without
        # the work of checking bases
        cpts = m.split(".")
        cpts.reverse()
        return ".".join(cpts)

    (lmap, pmap, weird, bogus, umap, hopeless) = module_attributions(modules)

    print("* Known modules")
    for n in sorted(lmap.keys(), key=lem):
        print("  {} -> {}".format(n, lmap[n]))
    print("* Known packages")
    for n in sorted(pmap.keys(), key=lem):
        print("  {} -> {}".format(n, pmap[n]))
    print("* Builtin modules")
    for n in sorted(weird, key=lem):
        print("  {}".format(n))
    if len(umap) > 0:
        print("* Unloaded modules")
        for n in sorted(umap.keys(), key=lem):
            print("  {} -> {}".format(n, umap[n]))
    if len(bogus) > 0:
        print("* Bogus modules")
        for n in sorted(bogus, key=lem):
            print("  {}".format(n))
    if len(hopeless) > 0:
        print("* Unfound modules")
        for n in sorted(hopeless, key=lem):
            print("  {}".format(n))
    if (len(umap) > 0 or len(hopeless) > 0):
        print("Trouble")

def clean_modules(modules=sys.modules):
    # Return a clean dict of modules: a dict mapping from names to
    # things which are modules.
    #
    return {n: m for (n, m) in modules.iteritems()
            if m and isinstance(m, ModuleType)}
