"""
    Tests for pipeline and stage configuration validation.
"""

import pytest

from analyzer.logs.record import LogRecord

from analyzer.pipeline.configuration import PipelineConfiguration
from analyzer.pipeline.stage import PipelineStage, PipelineStageResult


class MockPipelineStage(PipelineStage):
    def __init__(self):
        super(type(self), self).__init__(self, 'MockStage')

    def process(self, record: LogRecord) -> PipelineStageResult:
        return PipelineStageResult()


class MockNotStage:
    def process(self, *args):
        pass


class TestPipelineConfiguration:
    def test_mock_stage_is_accepted(self):
        mock_config = {
            'mock_stage': {
                'module': 'analyzer.pipeline.test_configuration',
                'class': 'MockPipelineStage'
            }
        }

        config = PipelineConfiguration(mock_config)
        assert [*config.stages.keys()] == ['mock_stage']

    def test_not_stage_is_not_accepted(self):
        mock_config = {
            'not_valid_stage': {
                'module': 'analyzer.pipeline.test_configuration',
                'class': 'MockNotStage'
            }
        }

        with pytest.raises(AssertionError) as e:
            PipelineConfiguration(mock_config)

        e.match('Does not return a PipelineStage')
