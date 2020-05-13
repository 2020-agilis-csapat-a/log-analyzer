from analyzer.pipeline.stage import PipelineStage, PipelineStageResult
from analyzer.logs.record import LogRecord

STRUCTURED_DATA_PATTERN_ID = 'id\s+(?P<object_id>\d+)$'
MSG_ID = 'message_id'


class IdentifyMessage(PipelineStage):
    def process(self,
                record: LogRecord,
                state: PipelineStageResult) -> PipelineStageResult:

        from re import search, I, X
        match = search(STRUCTURED_DATA_PATTERN_ID, record.content, I | X)
        if match:
            return PipelineStageResult(structured={
                MSG_ID: match.groupdict()['object_id']
            })
        return PipelineStageResult()
