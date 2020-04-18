"""
    Tests related generic pipeline stages.
"""

import pytest

from analyzer.pipeline.stage import PipelineStageResult


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
