"""
    Tests for the topological sort function.
"""

import pytest
from typing import Iterable

from util import topological_sort


class Dependable:
    def __init__(self, name: str, dependencies: Iterable[str]):
        self.name = name
        self.dependencies = dependencies

    def __repr__(self) -> str:
        return self.name

    def __hash__(self) -> int:
        return self.name.__hash__()

    def __eq__(self, other) -> bool:
        return (
            self.name == other.name and
            self.dependencies == other.dependencies
        )


class TestTopologicalSort:
    @staticmethod
    def object_graph():
        return {
            'roman_empire': ['army', 'economy'],
            'army': ['economy', 'food', 'tools', 'people'],
            'economy': ['people'],
            'tools': ['people', 'raw_materials'],
            'raw_materials': ['economy', 'people'],
            'food': ['people'],
            'something_unrelated': []
        }

    @staticmethod
    def objects():
        from itertools import chain
        graph = TestTopologicalSort.object_graph()
        deps = chain(*graph.values())
        objects = set([*graph.keys(), *deps])
        return [
            Dependable(name=o, dependencies=graph.get(o, []))
            for o
            in objects
        ]

    @staticmethod
    def dependency_function(obj: Dependable) -> Iterable[Dependable]:
        objs = TestTopologicalSort.objects()
        return [
            dep
            for dep
            in objs
            if dep.name in obj.dependencies
        ]

    def test_sort_empty_yields_empty(self):
        res = topological_sort(
            [], TestTopologicalSort.dependency_function
        )
        assert [*res] == []

    def test_sort_example_graph(self):
        objs = TestTopologicalSort.objects()
        res = topological_sort(
            objs, TestTopologicalSort.dependency_function
        )
        # For all objects on the output
        for i, obj in enumerate(res):
            # For any of its dependencies
            for dep in obj.dependencies:
                # It must preceed the object in the sorted output
                found = False
                for preceeding in res[:i]:
                    if preceeding.name == dep:
                        found = True
                        break
                assert found

    def test_loop_does_not_cause_sort_to_hang(self):
        one = Dependable(name='one', dependencies=['other'])
        other = Dependable(name='other', dependencies=['other'])

        def dependency_function(obj: Dependable) -> Dependable:
            if obj == one:
                yield other
            else:
                yield one

        with pytest.raises(RecursionError) as e:
            topological_sort([one, other], dependency_function)

        assert e.match('Maximum recursion limit exceeded')
