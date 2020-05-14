from analyzer.pipeline.stage import PipelineStage, PipelineStageResult
from analyzer.logs.record import LogRecord

from analyzer.application.stages.sdata import STRUCTURED_DATA
from analyzer.application.stages.msg_id import MSG_ID


MESSAGE_TYPE = 'message_type'


class IdentifyMessageType(PipelineStage):
    def process(self,
                record: LogRecord,
                state: PipelineStageResult) -> PipelineStageResult:
        if MSG_ID in state.structured and STRUCTURED_DATA in state.structured:
            sdata = state.structured[STRUCTURED_DATA]
            # FIXME: assumes exactly zero or one instances in the list.
            for asp in sdata.get('aspsSip', []):
                if 'aspRequest' not in asp:
                    return PipelineStageResult()

                req = asp['aspRequest']
                if not req or not sdata['internalMessage']:
                    return PipelineStageResult()

                type_ = sdata['internalMessage']['description']
                return PipelineStageResult(structured={
                    MESSAGE_TYPE: type_
                })

        return PipelineStageResult()
