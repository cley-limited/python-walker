"""Python walker low-level
"""

__all__ = ['Badness', 'Bug', 'Limitation']

class Badness(Exception):
    """Something wrong outwith our control"""

class Bug (Exception):
    """A bug in this code.

    Do not carry on after this.
    """

class Limitation(Exception):
    """A limitation.
    
    This might be a limitation in the code or something else: for
    instance there are recursion-depth limits which could potentially
    be due to implementation problems but also by external problems
    such as buggy walkers.

    There are cases where it could make sense to try again after this
    is raised (for instance with a greater recursion depth).
    """

if not __debug__:
    raise Badness("assertions are disabled: don't do that")
