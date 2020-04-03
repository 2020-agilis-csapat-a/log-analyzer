"""
Unit tests for the calculator library
"""

import pytest
from analyzer.logs.record import LogRecord


class TestRecordParsing:

    def test_parse_none_fails(self):
        with pytest.raises(AssertionError) as e:
            LogRecord.parse_string(None)

        assert e.match('Must pass record to be parsed.')

    def test_parse_type_fails(self):
        with pytest.raises(AssertionError) as e:
            LogRecord.parse_string(0)

        assert e.match('Record must be string.')

    def test_parse_empty_fails(self):
        with pytest.raises(AssertionError) as e:
            LogRecord.parse_string("")

        assert e.match('Not enough fields in string.')

    def test_parse_not_enough_fields_fails(self):
        for i in range(5):
            with pytest.raises(AssertionError) as e:
                LogRecord.parse_string(' '.join([f'field{i}'] * i))

            assert e.match('Not enough fields in string.')

    def test_source_indicator_raises_on_error(self):
        with pytest.raises(AssertionError) as e:
            LogRecord.parse_source_indicator('Does not match')

        assert e.match('Could not parse source indicator.')

    def test_source_indicator_example_success(self):
        file = 'ExampleComponentTest.ttcn'
        line = '313'
        scope = 'function:ExampleTestedFunction'
        result = LogRecord.parse_source_indicator(
            f'{file}:{line}({scope})'
        )
        assert result['source_file'] == file
        assert result['source_line'] == line
        assert result['source_scope'] == scope

    def test_parse_example_success(self):
        header_fields = {
            'date': '2014/Oct/24',
            'time': '19:16:48.062933',
            'application': '111',
            'event_type': 'SYSCALL'
        }

        sample_source_file = 'ExampleComponentTest.ttcn'
        sample_source_line = '313'
        sample_source_scope = 'function:ExampleTestedFunction'
        sample_context = (
            f'{sample_source_file}:{sample_source_line}({sample_source_scope})'
        )

        sample_content = 'open(0x7F323232) = -1'
        sample = ' '.join([
            *header_fields.values(),
            sample_context,
            sample_content
        ])

        output = LogRecord(sample)

        assert output.date == header_fields['date']
        assert output.time == header_fields['time']
        assert output.application == header_fields['application']
        assert output.event_type == header_fields['event_type']

        assert output.source['file'] == sample_source_file
        assert output.source['line'] == sample_source_line
        assert output.source['scope'] == sample_source_scope

        assert output.content == sample_content
