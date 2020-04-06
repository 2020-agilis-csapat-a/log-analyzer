#!/usr/bin/env python3

from collections import defaultdict
from json import dumps
from sys import stdin, stderr

from analyzer.logs.record import LogRecord
from analyzer.logs.parsing import gather_records

if __name__ != '__main__':
    print(
        'This file was meant to be called from the command line.',
        file=stderr
    )
    exit(1)


def is_structured_class(record: LogRecord):
    from re import search, I, S, X
    return search(
        r"""
            \{
                (?:
                    .*[:,].*
                ) | (?:\s*)
            \}
        """,
        record.content,
        I | S | X
    )


def is_component_class(record: LogRecord):
    from re import search, I
    return search(
        r'component type (?P<component_type>[^\s\.]+(?:\.[^.]+)?)',
        record.content,
        I
    )


def identify_class(record: LogRecord) -> str:
    if is_component_class(record):
        return 'component'
    elif is_structured_class(record):
        return 'structured'

    return 'other'


records_by_class = defaultdict(list)


for record_lines in gather_records(stdin):
    record = LogRecord('\n'.join(record_lines))
    record_class = identify_class(record)

    records_by_class[record_class].append(record.__dict__)

print(dumps(records_by_class))
