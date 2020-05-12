"""
    Convenience modul to allow importing common stages
    with a single import statement.
"""
from analyzer.application.stages.components import TagComponentIDs  # noqa F401
from analyzer.application.stages.components import ExtractComponentIDs  # noqa F401

from analyzer.pipeline.stage import PipelineStage
from analyzer.pipeline.stage import PipelineStageResult


# For debugging/example.
class EmitResultToStdoutJsonL(PipelineStage):
    def process(self, record, state):
        import json
        from sys import stdout
        print(json.dumps({
            'record': record.__dict__,
            'results': state.__dict__
        }), file=stdout)
        return PipelineStageResult()

