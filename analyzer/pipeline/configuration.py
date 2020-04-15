"""
    Configuration definition used for instantiating
    a log processing pipeline.
"""

from typing import Dict, Iterable

from analyzer.logs.record import LogRecord
from analyzer.pipeline.stage import PipelineStage, PipelineStageResult


class PipelineConfiguration:
    def __init__(self, stages: Dict[str, dict]):
        from pprint import pformat
        assert stages, 'A pipeline must have at least one stage'

        errors = []
        for stage, config in stages.items():
            err = PipelineConfiguration.is_stage_config_valid(config)
            if err:
                errors.append(f'{stage}: {err}')
                continue

        assert not errors, pformat(errors)
        self._stages = stages

    @property
    def stages(self) -> Dict[str, PipelineStage]:
        from copy import deepcopy
        return deepcopy(self._stages)

    @staticmethod
    def is_stage_config_valid(c: Dict[str, dict]) -> Iterable[str]:
        # TODO: Where in the python3 stdlib is the module type defined?
        # Add a type hint if possible, or remove this comment if it is not.
        def import_stage(mod: str, cls: str):
            from importlib import __import__ as _import
            imported = _import(mod, globals(), locals(), [cls], 0)
            return imported.__dict__[cls]

        def ensure_target_is_stage() -> Iterable[str]:
            mod = c['module']
            cls = c['class']

            try:
                stage_t = import_stage(mod, cls)
                stage = stage_t()
                stage_result = stage.process(LogRecord())

                assert isinstance(stage_result, PipelineStageResult), (
                    'Does not return a PipelineStageResult'
                )
            except Exception as e:
                return [f'{mod}.{cls}: Not a PipelineStage: {str(e)}']

            return []

        return [
            error_message
            for error_message
            in (
                *ensure_target_is_stage(),
            )
            if error_message is not None
        ]
