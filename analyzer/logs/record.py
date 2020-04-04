"""
Model for the log format we have to work with.
"""

from typing import Dict, List


class LogRecord:

    # NOTE: This pattern is meant to be used with the 'x' flag.
    SCOPE_PATTERN = r"""
        (?P<source_file> [^:]+)
        :
        (?P<source_line> \d+)
        \( (?P<source_scope>\S+) \)
    """

    # NOTE: This pattern is meant to be used with the 'x' flag.
    HEADER_PATTERN = r"""
        (?P<date>
            (?:{year_format})/(?:{month_format})/(?:{day_format})
        )
        \s
        (?P<time>
            # Hours, 2 digits, ASCII
            (?:\d\d?):

            # Minutes, 2 digits, ASCII
            (?:\d\d?):

            # Seconds, 2 digits, ASCII
            (?:\d\d?).

            # Subsecond units - Looks microseconds in the sample,
            # but no one specified whether the number of decimals is fixed.
            # I'll just accept whatever digits happen to be there.
            (?:\d+)
        )
        \s
        (?P<application>
            {application_format}
        )
        \s
        (?P<event_type>
            {event_format}
        )
        \s
        (?:  # Scope, see SCOPE_PATTERN for details.
             # Not a named capture, because the included pattern
             # already contains all named capture groups.
            {scope_pattern}
        )
    """.format(**{
        # 4 digits, ASCII
        'year_format': r'\d{4}',

        # English, abbreviated to three characters as in old school UNIX
        'month_format': r'Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec',

        # Not doing too much validation, but disallow funny things the 40th
        # NOTE: Does not validate specifically for months shorter than 31 days,
        # so it does not reject February 30, for example.
        'day_format': '(?:[0-2][0-9])|(?:3[0-1])',

        # Application, either a process name or a PID.
        # NOTE:
        # Leaving a note here because no one made constraints on this field.
        # On a modern *NIX like Linux,
        # process names can contain a lot of things, including whitespace.
        # It'd be a lot of trouble to try and match process names
        # that contain whitespace,
        # so unless that my assumption is proven invalid,
        # I'll treat whatever we see until the next word boundary
        # as the application id.
        'application_format': r'\S*',

        # Event type.
        # NOTE:
        # I suspect there exists a finite, enumerable set of these,
        # but again no one made anything about it explicit.
        'event_format': r'\S*',

        'scope_pattern': SCOPE_PATTERN
    })

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
    def parse_scope(content: str) -> Dict[str, str]:
        from re import match, X

        indicator_pattern = f'^{LogRecord.SCOPE_PATTERN}$'
        matched = match(indicator_pattern, content, X)
        assert matched, 'Could not parse source indicator.'

        fields = matched.groupdict()
        assert len(fields) == 3, 'Could not parse source indicator.'

        return matched.groupdict()

    @staticmethod
    def parse_string(content: str) -> List[str]:
        from re import match, X, M, S
        assert content is not None, 'Must pass record to be parsed.'
        assert type(content) == str, 'Record must be string.'

        m = match(f"""
            \\A
            {LogRecord.HEADER_PATTERN}
            (?:\\s  # No one specified whether messages without body exist.
                (?P<content> .*)
            )?
            \\Z
        """, content, X | M | S)
        assert m, 'Could not parse log record.'

        return m.groupdict()


def line_begins_with_record_header(string: str) -> bool:
    from re import match, X
    return match(f'\\A{LogRecord.HEADER_PATTERN}', string, X)
