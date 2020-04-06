#!/usr/bin/env python3

from sys import stdin, stdout, stderr
from analyzer.logs.record import LogRecord
from analyzer.logs.parsing import gather_records

if __name__ != '__main__':
    print(
        'This file was meant to be called from the command line.',
        file=stderr
    )
    exit(1)


for record_lines in gather_records(stdin):
    from json import dumps
    record = LogRecord('\n'.join(record_lines))
    ser = dumps(record.__dict__)
    print(ser, file=stdout)
