"""
    Tests for pipeline and stage configuration validation.
"""

import pytest

from analyzer.logs.record import LogRecord

from analyzer.pipeline.configuration import PipelineConfiguration
from analyzer.pipeline.stage import PipelineStage, PipelineStageResult


class MockPipelineStage(PipelineStage):
    def process(self,
                record: LogRecord,
                state: PipelineStageResult) -> PipelineStageResult:
        return PipelineStageResult()


class MockNotStage:
    def process(self, *args, **kwargs):
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
        stages = config.stages

        assert len(stages) == 1
        assert stages[0].name == 'mock_stage'
        assert stages[0].module == 'analyzer.pipeline.test_configuration'
        assert stages[0].klass == 'MockPipelineStage'

    def test_not_stage_is_not_accepted(self):
        mock_config = {
            'not_valid_stage': {
                'module': 'analyzer.pipeline.test_configuration',
                'class': 'MockNotStage'
            }
        }

        with pytest.raises(Exception) as e:
            PipelineConfiguration(mock_config)

        e.match('Not a PipelineStage')

    def test_sorts_example_pipeline_successfully(self):
        mock_config = {
            'mock_stage_x2': {
                'module': 'analyzer.pipeline.test_configuration',
                'class': 'MockPipelineStage',
                'depends_on': 'mock_stage_z1'
            },
            'mock_stage_y0': {
                'module': 'analyzer.pipeline.test_configuration',
                'class': 'MockPipelineStage'
            },
            'mock_stage_z1': {
                'module': 'analyzer.pipeline.test_configuration',
                'class': 'MockPipelineStage',
                'depends_on': 'mock_stage_y0'
            }
        }

        config = PipelineConfiguration(mock_config)
        assert len(config.stages) == 3

        ordered = config.stages_in_order()

        assert len(ordered) == 3
        assert ordered[0].name == 'mock_stage_y0'
        assert ordered[1].name == 'mock_stage_z1'
        assert ordered[2].name == 'mock_stage_x2'
