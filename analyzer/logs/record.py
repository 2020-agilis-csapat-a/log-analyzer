"""
Model for the log format we have to work with.
"""

from typing import Dict, List


class LogRecord:
    def __init__(self, content: str):
        fields = LogRecord.parse_string(content)

        self.date = fields['date']
        self.time = fields['time']
        self.application = fields['application']
        self.event_type = fields['event_type']
        self.source = {
            'file': fields['source_file'],
            'line': fields['source_line'],
            'scope': fields['source_scope'],
        }
        self.content = fields['content']

    @staticmethod
    def parse_source_indicator(content: str) -> Dict[str, str]:
        from re import match, X

        indicator_pattern = r"""
            ^
            (?P<source_file>[^:]+):(?P<source_line>\d+)
            \( (?P<source_scope>.+) \)
            $
        """
        matched = match(indicator_pattern, content, X)
        assert matched, 'Could not parse source indicator.'

        fields = matched.groupdict()
        assert len(fields) == 3, 'Could not parse source indicator.'

        return matched.groupdict()

    @staticmethod
    def parse_string(content: str) -> List[str]:
        def separate_major_fields(content: str) -> List[str]:
            assert content is not None, 'Must pass record to be parsed.'
            assert type(content) == str, 'Record must be string.'

            fields = content.split(maxsplit=5)
            assert len(fields) == 6, 'Not enough fields in string.'

            return fields


        major_fields = separate_major_fields(content)
        return {
            'date': major_fields[0],
            'time': major_fields[1],
            'application': major_fields[2],
            'event_type': major_fields[3],
            'content': major_fields[5],
            **LogRecord.parse_source_indicator(major_fields[4])
        }
