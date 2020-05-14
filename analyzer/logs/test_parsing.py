"""
Tests for parsing utilities.
"""

import pytest
from analyzer.logs.parsing import gather_records


@pytest.fixture
def sample_line() -> str:
    return ' '.join([
        '2014/Oct/24',
        '19:16:48.062933',
        '111',
        'SYSCALL',
        'ExampleComponentTest.ttcn:313(function:ExampleTestedFunction)',
        'open(0x7F323232) = -1'
    ])


@pytest.fixture
def sample_line_without_scope() -> str:
    return ' '.join([
        '2014/Oct/24',
        '19:16:48.062933',
        '111',
        'SYSCALL',
        '-',
        'open(0x7F323232) = -1'
    ])


class TestRecordSeparation:

    def test_garbage_yields_no_records(self):
        counterexamples = [*gather_records("""
            This does not quite
            look anything like
            a log record to parse.
        """)]

        assert not counterexamples

    def test_yields_valid_single_line_record(self, sample_line):
        lines = [sample_line]
        lines_by_record = [*gather_records(lines)]

        assert len(lines_by_record) == 1
        assert lines_by_record[0] == lines

    def test_yields_valid_scopeless(self, sample_line_without_scope):
        lines = [sample_line_without_scope] * 2
        lines_by_record = [*gather_records(lines)]

        assert len(lines_by_record) == 2
        assert lines_by_record[0] == [sample_line_without_scope]
        assert lines_by_record[1] == [sample_line_without_scope]

    def test_yields_valid_multiple_singleline_records(self, sample_line):
        record_lines = [sample_line]
        lines_by_record = [*gather_records(record_lines * 3)]

        assert len(lines_by_record) == 3
        for lines in lines_by_record:
            assert lines == record_lines

    def test_yields_valid_single_multiline_record(self, sample_line):
        record_lines = [
            sample_line,
            '/me glares at python with malicious intent.'
        ]
        lines_by_record = [*gather_records(record_lines)]

        assert len(lines_by_record) == 1
        assert lines_by_record[0] == record_lines
