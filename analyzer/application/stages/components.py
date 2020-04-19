"""
    This module contains component related
    log processsing stages.
"""

from analyzer.logs.record import LogRecord
from analyzer.pipeline.stage import PipelineStage, PipelineStageResult

COMPONENT_NAMESPACE = 'hu.analyzer.component'
COMPONENT_ID_PATTERN = r'component\sreference:\s(?P<component_id>\d+)'
COMPONENT_TYPE_PATTERN = r'type:\s(?P<component_type>[\w\d]+(?:\.[\w\d]+))'


class TagComponentIDs(PipelineStage):
    def process(self,
                record: LogRecord,
                state: PipelineStageResult) -> PipelineStageResult:
        from re import search, I, X
        if search(COMPONENT_ID_PATTERN, record.content, I | X):
            return PipelineStageResult(tags=[COMPONENT_NAMESPACE])
        return PipelineStageResult()


class ExtractComponentIDs(PipelineStage):
    def process(self,
                record: LogRecord,
                state: PipelineStageResult) -> PipelineStageResult:
        from re import search, I, X
        if COMPONENT_NAMESPACE not in state.tags:
            return PipelineStageResult()

        cap = {
            **search(COMPONENT_ID_PATTERN, record.content, I | X).groupdict(),
            **search(COMPONENT_TYPE_PATTERN, record.content, I | X).groupdict()
        }
        return PipelineStageResult(structured={
            COMPONENT_NAMESPACE: {
                'type': cap['component_type'],
                'id': cap['component_id']
            }
        })
