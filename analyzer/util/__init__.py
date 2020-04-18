"""
    Various utility functions and classes that encompass
    the accidental complexity of our implementation.
"""

from collections import defaultdict
from typing import Callable, Iterable


class AutovivifiedDict(dict):
    """
        Autovivification means that this dict will,
        instead of raising an Exception,
        return another, also autovivifying dict,
        so one can use it as a tree without having to care
        about any intermediate keys that may not be set.
    """

    def __missing__(self, key):
        v = AutovivifiedDict()
        self[key] = v
        return v


def topological_sort(input_range: Iterable[object],
                     callback_branches: Callable[[object], Iterable[object]]
                     ) -> Iterable[object]:
    """
        Topological sort for establishing initialization
        or execution order between dependent objects.

        Dependency loops are not supported.

        :param input_range: Objects to be sorted.

        :param callback_branches: A function or delegate that
        takes a dependent object (`d`) as input,
        and returns a range of objects that `d` depends on.

        :returns: A range that yields :input_range:,
        topologically sorted based on
        the relation function `callback_branches`.
    """
    state = {}

    def update(obj, depth):
        if depth >= state.get(obj, 0):
            state[obj] = depth

    def recurse(to_obj, depth=1):
        if depth > 128:
            raise RecursionError('Maximum recursion limit exceeded.')

        update(to_obj, depth)

        for dependency in callback_branches(to_obj):
            recurse(dependency, depth + 1)

    for root in input_range:
        update(root, 0)
        for branch in callback_branches(root):
            recurse(branch)

    layers = defaultdict(list)
    for obj, maxdepth in state.items():
        layers[-maxdepth].append(obj)

    from itertools import chain
    return [*chain(*[
        layers[i]
        for i
        in sorted(layers.keys())
    ])]


def import_from(stage_module: str, stage_class: str) -> type:
    from importlib import __import__ as _import
    imported = _import(stage_module, globals(), locals(), [stage_class], 0)
    return imported.__dict__[stage_class]
