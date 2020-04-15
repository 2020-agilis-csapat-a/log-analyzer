"""
    Tests related generic pipeline stages.
"""

import pytest

from analyzer.util import AutovivifiedDict
from analyzer.pipeline.stage import PipelineStage, PipelineStageResult


def test_stage_needs_a_name():
    with pytest.raises(AssertionError) as e:
        stage = PipelineStage(name=None)

    assert e.match("Stage must be given a name")


def test_stage_has_immutable_name():
    stage = PipelineStage(name='ReadMe')

    with pytest.raises(AttributeError) as e:
        stage.name = 'fail!'

    assert e.match("can't set attribute")
    assert stage.name == 'ReadMe'


def test_stage_has_immutable_dependencies():
    deps = ['nothing_really']
    stage = PipelineStage(name='ReadMe', depends_on=deps)

    with pytest.raises(AttributeError) as e:
        stage.dependencies = []

    assert e.match("can't set attribute")
    assert stage.dependencies == deps


def test_stage_result_tags_are_immutable():
    tags = ['actual-results']
    res = PipelineStageResult(tags=tags)

    with pytest.raises(AttributeError) as e:
        res.tags = ['falsified-results']

    assert e.match("can't set attribute")
    assert res.tags == tags

    res.tags.append('another')

    assert res.tags == tags


def test_stage_result_structured_data_are_immutable():
    sdata = {'component': {'id': 'SomethingSomethingComponent'}}
    res = PipelineStageResult(structured=sdata)

    with pytest.raises(AttributeError) as e:
        res.structured = {}

    assert e.match("can't set attribute")
    assert res.structured == sdata

    res.structured['another'] = 'key'
    res.structured['component']['another'] = 'key'

    assert res.structured == sdata


def test_stage_result_can_check_presence_with_if_stmt():
    assert not PipelineStageResult()
    assert not PipelineStageResult(tags=[])
    assert not PipelineStageResult(structured={})

    assert PipelineStageResult(tags=['any'])
    assert PipelineStageResult(structured={'any': 'value'})
