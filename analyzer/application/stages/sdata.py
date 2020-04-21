from typing import Union, Tuple

from analyzer.pipeline.stage import PipelineStage, PipelineStageResult
from analyzer.logs.record import LogRecord

import string

STRUCTURED_DATA_PATTERN = r"(?P<sdata>\{(?:.|\n)*:=(?:.|\n)*\})"
STRUCTURED_DATA_NAMESPACE = 'hu.analyzer.sdata'
STRUCTURED_DATA_AS_STRING = 'hu.analyzer.sdata.string'
STRUCTURED_DATA_AS_JSON = 'hu.analyzer.sdata.json'
STRUCTURED_DATA = 'hu.analyzer.sdata.data'


class SegregateSdata(PipelineStage):
    def process(self,
                record: LogRecord,
                state: PipelineStageResult) -> PipelineStageResult:
        from re import search, I, X
        match = search(STRUCTURED_DATA_PATTERN, record.content, I | X)
        if match:
            return PipelineStageResult(structured={
                STRUCTURED_DATA_AS_STRING: match.groupdict()['sdata']
            })
        return PipelineStageResult()


class ParseSdata(PipelineStage):
    def process(self,
                record: LogRecord,
                state: PipelineStageResult) -> PipelineStageResult:
        if not type(state.structured[STRUCTURED_DATA_AS_STRING]) == str:
            return PipelineStageResult()

        sdata_str = state.structured[STRUCTURED_DATA_AS_STRING]
        sdata = self.parse_object(sdata_str)

        return PipelineStageResult(structured={
            STRUCTURED_DATA: sdata
        })

    def parse_object(self, from_str: str):
        for c in from_str[1:]:
            if c in string.whitespace:
                next

            if c in string.digits:
                from re import match
                num_match = match(r'\d+(?:\.\d+)?', from_str[1:])
                return float(num_match.group(0)), ''

            # TODO: This is probably the spot where our next bug lies.
            if c in '"':
                from re import match
                str_ = match(r'"(?:\"|.)"')
                return str_.match(0), ''

            if c == '{':
                return self.parse_list(from_str), ''

            if c == '}':
                return [], ''

            return self.parse_dict(from_str)
        return {}, ''

    def parse_list(self, from_str: str):
        parsed = []
        curr = from_str[1:]

        while curr:
            for i, c in enumerate(curr):
                if c == ',':
                    next

                if c not in string.whitespace:
                    p, rem = self.parse_object(curr[i:])
                    parsed.append(p)
                    curr = rem

                if c == '}':
                    return parsed, curr[i:]

    def parse_dict(self, from_str: str):
        parsed = {}
        curr = from_str[1:]

        while curr:
            for i, c in enumerate(curr):
                if c in string.whitespace:
                    next

                if c == ',':
                    next

                if c in string.ascii_letters:
                    pieces = curr[i:].split(maxsplit=2)
                    try:
                        key, rem = pieces[0], pieces[-1]
                    except:
                        print(f'~~~~{from_str}')
                        assert False
                    val, rem = self.parse_object(rem)
                    parsed[key] = val
                    curr = rem

                if c == '}':
                    return parsed, curr[i:]
