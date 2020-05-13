from analyzer.pipeline.stage import PipelineStage, PipelineStageResult
from analyzer.logs.record import LogRecord
from analyzer.application.stages.sdata import STRUCTURED_DATA as STRUCT_D

CONN_KEY = 'connections'


class IdentifyConnectionsByPort(PipelineStage):
    def process(self,
                record: LogRecord,
                state: PipelineStageResult) -> PipelineStageResult:

        if not type(state.structured[STRUCT_D]) == list:
            state = state.structured[STRUCT_D]
            conn = {}
            if 'connOpened' in state:

                conn = {}
                conn['rem_name'] = state['connOpened']['remName']
                conn['rem_port'] = state['connOpened']['remPort']
                conn['loc_name'] = state['connOpened']['locName']
                conn['loc_port'] = state['connOpened']['locPort']
                CONN_RESULT = PipelineStageResult(structured={CONN_KEY: conn})

                return CONN_RESULT

            elif state and 'remName' in state and 'locName' in state:

                conn = {}
                conn['rem_name'] = state['remName']
                conn['rem_port'] = state['remPort']
                conn['loc_name'] = state['locName']
                conn['loc_port'] = state['locPort']
                CONN_RESULT = PipelineStageResult(structured={CONN_KEY: conn})
                return CONN_RESULT

        return PipelineStageResult()
