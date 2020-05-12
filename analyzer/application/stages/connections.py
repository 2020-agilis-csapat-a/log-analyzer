from analyzer.pipeline.stage import PipelineStage, PipelineStageResult
from analyzer.logs.record import LogRecord


STRUCTURED_DATA_NAMESPACE = 'hu.analyzer.sdata'
STRUCTURED_DATA_AS_STRING = f'{STRUCTURED_DATA_NAMESPACE}.string'
STRUCT_D = f'{STRUCTURED_DATA_NAMESPACE}.data'
ID_CONN = 'conn'
CONN = {}


class IdentifyConnectionsByPort(PipelineStage):
    def process(self,
                record: LogRecord,
                state: PipelineStageResult) -> PipelineStageResult:

        if not type(state.structured[STRUCT_D]) == list:
            state = state.structured[STRUCT_D]
            if 'connOpened' in state:

                CONN[ID_CONN] = {}
                CONN[ID_CONN]['rem_name'] = state['connOpened']['remName']
                CONN[ID_CONN]['rem_port'] = state['connOpened']['remPort']
                CONN[ID_CONN]['loc_name'] = state['connOpened']['locName']
                CONN[ID_CONN]['loc_port'] = state['connOpened']['locPort']
                CONN_RESULT = PipelineStageResult(structured=CONN)
                print(CONN_RESULT)
                return CONN_RESULT

            elif state and 'remName' in state and 'locName' in state:

                CONN[ID_CONN] = {}
                CONN[ID_CONN]['rem_name'] = state['remName']
                CONN[ID_CONN]['rem_port'] = state['remPort']
                CONN[ID_CONN]['loc_name'] = state['locName']
                CONN[ID_CONN]['loc_port'] = state['locPort']
                CONN_RESULT = PipelineStageResult(structured=CONN)
                print(CONN_RESULT)
                return CONN_RESULT

        return PipelineStageResult()
