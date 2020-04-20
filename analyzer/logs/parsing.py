"""
Functions for the purpose of parsing a log file.
"""

from analyzer.logs.record import line_begins_with_record_header

from typing import Iterable, List


def gather_records(input_lines: Iterable[str]) -> List[str]:
    """
    This function extracts log records from a range of lines.
    It will skip any and all content before the first record header.

    Once it has detected a log record, it'll buffer all lines
    up until the end of the input range or until a new record header is found.
    When that happens, the function yields the lines
    belonging to the buffered log record,
    and begins buffering the newly encountered one.
    """
    assert input_lines

    record_buffer = []

    for line in input_lines:
        record_start = line_begins_with_record_header(line)
        if record_start:
            if len(record_buffer) > 0:
                yield record_buffer
                record_buffer = []

        if record_start or len(record_buffer) > 0:
            record_buffer.append(line.rstrip())

    if len(record_buffer) > 0:
        yield record_buffer
