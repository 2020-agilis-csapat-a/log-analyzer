"""
    This module contains the implementations of
    a single-pass log processing pipeline,
    that may be used in a streaming manner.
"""

from analyzer.logs.record import LogRecord
from analyzer.pipeline.configuration import PipelineConfiguration
from analyzer.pipeline.stage import PipelineStageResult


class Pipeline:
    def __init__(self, config: PipelineConfiguration):
        from analyzer.util import import_from
        self._configuration = config
        stages = []

        for stage_def in self._configuration.stages_in_order():
            stage = import_from(stage_def.module, stage_def.klass)
            stages.append((stage_def.name, stage()))

        self._stages = stages

    def process(self, record: LogRecord) -> PipelineStageResult:
        results_so_far = PipelineStageResult()
        for (name, stage) in self._stages:
            try:
                stage_results = stage.process(record, results_so_far)
                results_so_far = PipelineStageResult(
                    tags=[*results_so_far.tags, *stage_results.tags],
                    structured={
                        **results_so_far.structured,
                        **stage_results.structured
                    }
                )
            except Exception as e:
                raise Exception(f'stage {name}: {str(e)}')

        return results_so_far
