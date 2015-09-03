"""Python walker low-level
"""

__all__ = ['Badness', 'Bug']

class Badness (Exception):
    # not our problem
    pass

class Bug (Exception):
    # our problem
    pass

if not __debug__:
    raise Badness("assertions are disabled: don't do that")
