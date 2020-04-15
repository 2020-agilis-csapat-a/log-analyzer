"""
Unit tests for LogRecord
"""

import pytest
from analyzer.logs.record import LogRecord, line_begins_with_record_header


@pytest.fixture
def sample_singleline_record():
    sample_source_file = 'ExampleComponentTest.ttcn'
    sample_source_line = '313'
    sample_source_scope = 'function:ExampleTestedFunction'
    sample_context = (
        f'{sample_source_file}:{sample_source_line}({sample_source_scope})'
    )
    sample_content = 'open(0x7F323232) = -1'
    header_fields = {
        'date': '2014/Oct/24',
        'time': '19:16:48.062933',
        'application': '111',
        'event_type': 'SYSCALL'
    }

    return {
        'header_fields': header_fields,

        'sample_source_file': sample_source_file,
        'sample_source_line': sample_source_line,
        'sample_source_scope': sample_source_scope,

        'sample_context': sample_context,
        'sample_content': sample_content,

        'sample': ' '.join([
            *header_fields.values(),
            sample_context,
            sample_content
        ])
    }


@pytest.fixture
def sample_multiline_record(sample_singleline_record):
    additional_line = f'\nHello there!'
    template = {**sample_singleline_record}
    template['sample_content'] += additional_line
    template['sample'] += additional_line
    return template


class TestRecordParsing:
    def test_parameterless_constructor_works(self):
        assert LogRecord()

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

        assert e.match('Could not parse log record.')

    def test_parse_not_enough_fields_fails(self):
        for i in range(5):
            with pytest.raises(AssertionError) as e:
                LogRecord.parse_string(' '.join([f'field{i}'] * i))

            assert e.match('Could not parse log record.')

    def test_source_indicator_raises_on_error(self):
        with pytest.raises(AssertionError) as e:
            LogRecord.parse_scope('Does not match')

        assert e.match('Could not parse source indicator.')

    def test_source_indicator_example_success(self):
        file = 'ExampleComponentTest.ttcn'
        line = '313'
        scope = 'function:ExampleTestedFunction'
        result = LogRecord.parse_scope(
            f'{file}:{line}({scope})'
        )
        assert result['source_file'] == file
        assert result['source_line'] == line
        assert result['source_scope'] == scope

    def assert_record_matches_sample(self, sample_dict):
        header_fields = sample_dict['header_fields']
        sample_source_file = sample_dict['sample_source_file']
        sample_source_line = sample_dict['sample_source_line']
        sample_source_scope = sample_dict['sample_source_scope']
        sample_content = sample_dict['sample_content']
        sample = sample_dict['sample']

        output = LogRecord(sample)

        assert output.date == header_fields['date']
        assert output.time == header_fields['time']
        assert output.application == header_fields['application']
        assert output.event_type == header_fields['event_type']

        assert output.source['file'] == sample_source_file
        assert output.source['line'] == sample_source_line
        assert output.source['scope'] == sample_source_scope

        assert output.content == sample_content

    def test_parse_singleline_sample_success(self, sample_singleline_record):
        self.assert_record_matches_sample(sample_singleline_record)

    def test_parse_multiline_sample_success(self, sample_multiline_record):
        self.assert_record_matches_sample(sample_multiline_record)


class TestRecordStringHeuristics:

    def test_header_detection_positive(self, sample_singleline_record):
        sample = sample_singleline_record['sample']
        assert line_begins_with_record_header(sample)

    def test_header_detection_negative(self, sample_singleline_record):
        sample = 'Once upon a time, in a galaxy far, far away...'
        assert not line_begins_with_record_header(sample)
