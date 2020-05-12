import string
from typing import Dict, List, Tuple, Union

from analyzer.pipeline.stage import PipelineStage, PipelineStageResult
from analyzer.logs.record import LogRecord


STRUCTURED_DATA_NAMESPACE = 'hu.analyzer.sdata'
STRUCTURED_DATA_AS_STRING = f'{STRUCTURED_DATA_NAMESPACE}.string'
STRUCT_D = f'{STRUCTURED_DATA_NAMESPACE}.data'

SDATA_QUOTES = ('\"', '\'')

ID_CONN = 'conn'
CONN = {}

class IdentifyConnectionsByPort(PipelineStage):
    def process(self,
                record: LogRecord,
                state: PipelineStageResult) -> PipelineStageResult:

        if not type(state.structured[STRUCT_D]) == list:
            if 'connOpened' in state.structured[STRUCT_D]:

                CONN[ID_CONN] = {}
                CONN[ID_CONN]['remote_name'] = state.structured[STRUCT_D]['connOpened']['remName']
                CONN[ID_CONN]['remote_port'] = state.structured[STRUCT_D]['connOpened']['remPort']
                CONN[ID_CONN]['local_name'] = state.structured[STRUCT_D]['connOpened']['locName']
                CONN[ID_CONN]['local_port'] = state.structured[STRUCT_D]['connOpened']['locPort']
                CONN_RESULT = PipelineStageResult(structured=CONN)
                print(CONN_RESULT)
                return CONN_RESULT
                
            elif state.structured[STRUCT_D] and 'remName' in state.structured[STRUCT_D] and 'locName' in state.structured[STRUCT_D]:
                
                CONN[ID_CONN] = {}
                CONN[ID_CONN]['remote_name'] = state.structured[STRUCT_D]['remName']
                CONN[ID_CONN]['remote_port'] = state.structured[STRUCT_D]['remPort']
                CONN[ID_CONN]['local_name'] = state.structured[STRUCT_D]['locName']
                CONN[ID_CONN]['local_port'] = state.structured[STRUCT_D]['locPort']
                CONN_RESULT = PipelineStageResult(structured=CONN)
                print(CONN_RESULT)
                return CONN_RESULT
                
        return PipelineStageResult()
