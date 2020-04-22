from pytest import fixture

from analyzer.logs.record import LogRecord
from analyzer.application.stages.sdata import ParseSdata
from analyzer.application.stages.sdata import STRUCTURED_DATA_AS_STRING
from analyzer.application.stages.sdata import STRUCTURED_DATA
from analyzer.pipeline.stage import PipelineStageResult


@fixture
def mapstr():
    return """{
        true := true,
        false := false,
        string := "Read me",
        empty_object := {}
        integer := 42,
        real := 42.0,
        list := {
            "we are now",
            "getting",
            "lispy"
        }
        a_nested := {
            map := "this one is"
        }
        weirdo_data := '4865786C696679206D65'O (Hexlify me)
        undefined := <unbound>,
        also_undefined := omit,
    }"""


def test_parse_map(mapstr):
    header = (
        '2014/Oct/24 19:16:48.062933 111 SYSCALL ' +
        'ExampleComponentTest.ttcn:313(function:ExampleTestedFunction)'
    )
    stage = ParseSdata()
    record = LogRecord(f'{header} asdf')
    result = stage.process(record, PipelineStageResult(structured={
        STRUCTURED_DATA_AS_STRING: mapstr
    }))

    sdata = result.structured[STRUCTURED_DATA]

    expected = {
        'true': True,
        'false': False,
        'string': 'Read me',
        'integer': 42,
        'real': 42.0,
        'list': [
            'we are now',
            'getting',
            'lispy'
        ],
        'empty_object': {},
        'a_nested': {
            'map': 'this one is'
        },
        'weirdo_data': {
            'hex': '4865786C696679206D65',
            'plain': 'Hexlify me'
        },
        'undefined': None,
        'also_undefined': None
    }

    assert sdata == expected
