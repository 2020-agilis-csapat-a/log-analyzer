import string
from typing import Dict, List, Tuple, Union
from sys import stderr

from analyzer.pipeline.stage import PipelineStage, PipelineStageResult
from analyzer.logs.record import LogRecord


STRUCTURED_DATA_PATTERN = r"(?P<sdata>\{(?:.|\n)*:=(?:.|\n)*\})"
STRUCTURED_DATA_NAMESPACE = 'hu.analyzer.sdata'
STRUCTURED_DATA_AS_STRING = f'{STRUCTURED_DATA_NAMESPACE}.string'
STRUCTURED_DATA = f'{STRUCTURED_DATA_NAMESPACE}.data'

SDATA_QUOTES = ('\"', '\'')


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
        sdata, _ = self.parse_object(sdata_str)

        return PipelineStageResult(structured={
            STRUCTURED_DATA: sdata
        })

    def parse_object(self, from_str: str) -> Tuple[object, str]:
        some_object = False
        for i, c in enumerate(from_str):

            # Empty map.
            # (Well, empty object, we have no schema.)
            if c == '}':
                return {}, from_str[i+1:]

            skippable = string.whitespace + '\r\n,'
            if c in skippable:
                continue

            if some_object:
                # Unqouted string => key
                # We are inside a map.
                if c in string.ascii_letters:
                    return self.parse_dict(from_str)
            else:
                # Booleans
                # Keys are unqouted,
                # and nothing says you can't have a key named 'true'!
                # So only parse these if we are not in an aggregate.
                if c in 'fF' and from_str[i:].lower().startswith('false'):
                    return False, from_str[i+len('false'):]
                if c in 'tT' and from_str[i:].lower().startswith('true'):
                    return True, from_str[i+len('true'):]

                # So, there are some serialized 'named values', too.
                if c in string.ascii_letters:
                    return self.parse_enum(from_str)

            # Parsing a number
            if c in ('-', *string.digits):
                from re import match
                num_match = match(r'(-?\d+)(?:\.\d+)?', from_str[i:])
                assert num_match
                num_str = num_match.group(0)

                if '.' in num_str:
                    # Real number
                    num = float(num_str)
                else:
                    # Integer
                    num = int(num_str)

                return num, from_str[i+len(num_str):]

            # Quotes found => string!
            # Well, almost.
            # Judging by the syntax,
            # it should be possible to do this:
            #   { "list", "of", "strings" }
            # We have to check the first char in
            # the object to see if we are in a list,
            # or we are just parsing a string literal
            # on its own.
            # There are also 'stringlike' objects.
            if c in SDATA_QUOTES:
                if some_object:
                    # List of stringlikes.
                    return self.parse_list(from_str)
                else:
                    # Actual stringlike.
                    obj, rem = self.parse_stringlike(from_str[i:])
                    return obj, rem

            # We are a list, because we found an object without key.
            if c == '{' and i == 0:
                some_object = True
                continue
            else:
                return self.parse_list(from_str)

            # Fail early and hard on unhandled input,
            # so we know we have to fix the parser!
            # Not having any coverage on these lines
            # for valid test inputs is a *GOOD* thing!
            assert False, from_str
        assert False, from_str

    def parse_list(self, from_str: str) -> Tuple[List[object], str]:
        parsed: List[object] = []
        curr = from_str[1:]

        while curr:
            cont = False
            for i, c in enumerate(curr):
                if c == '}':
                    return parsed, curr[i+1:]

                if c == ',':
                    continue

                if c not in (*string.whitespace, '\r', '\n'):
                    p, rem = self.parse_object(curr[i:])
                    parsed.append(p)
                    curr = rem
                    cont = True
                    break

            if not cont:
                break

        return parsed, curr

    def parse_dict(self,
                   from_str: str) -> Tuple[Dict[str, object], str]:
        parsed: Dict[str, object] = {}
        curr = from_str

        while curr:
            cont = False
            for i, c in enumerate(curr):
                if c == '}':
                    return parsed, curr[i+1:]

                if c in string.ascii_letters:
                    pieces = curr[i:].split(maxsplit=2)
                    key, rem = pieces[0], pieces[2]
                    nil, nil_len = self.is_nil(rem)
                    if nil:
                        val, rem = None, rem[nil_len:]
                    else:
                        val, rem = self.parse_object(rem)
                    parsed[key] = val
                    curr = rem
                    cont = True
                    break

                cont = True

            if not cont:
                break

        return parsed, curr

    def parse_stringlike(self,
                         from_str: str
                         ) -> Tuple[Union[str, Dict[str, str]], str]:
        str_, rem = self.parse_string(from_str)
        if rem.startswith('O'):
            hex_ = str_
            rem = rem[1:].lstrip()
            str_, rem = self.parse_parens(rem)
            return {
                'hex': hex_,
                'plain': str_
            }, rem

        return str_, rem

    def parse_parens(self, from_str: str) -> Tuple[str, str]:
        pars = 1
        seek = 1
        while pars > 0:
            if from_str[seek] == '\\':
                seek += 2
                continue

            if from_str[seek] == ')':
                pars -= 1
            elif from_str[seek] == '(':
                pars += 1

            seek += 1
        str_ = from_str[1:seek-1:]
        return str_, from_str[seek:]

    def parse_string(self, from_str: str) -> Tuple[str, str]:
        quote_stack = [from_str[0]]
        seek = 1
        while quote_stack:
            if from_str[seek] == '\\':
                seek += 2
                continue

            if from_str[seek] == quote_stack[-1]:
                quote_stack = quote_stack[:-1]
            elif from_str[seek] in SDATA_QUOTES:
                quote_stack.append(from_str[seek])

            seek += 1
        str_ = from_str[1:seek-1]
        return str_, from_str[seek:]

    def is_nil(self, from_str: str) -> Tuple[bool, int]:
        nils = ('omit', '<unbound>')
        for nil in nils:
            if from_str.startswith(nil):
                return True, len(nil)
        return False, 0

    def parse_enum(self, from_str: str) -> Tuple[dict, str]:
        pieces = from_str.split(maxsplit=1)
        name, rem = pieces[0], pieces[1]
        value, rem = self.parse_parens(rem)
        return {
            'name': name,
            'value': value
        }, rem
