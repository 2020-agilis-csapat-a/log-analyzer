"""
    Various utility functions and classes that encompass
    the accidental complexity of our implementation.
"""


class AutovivifiedDict(dict):
    def __missing__(self, key):
        v = AutovivifiedDict()
        self[key] = v
        return v
