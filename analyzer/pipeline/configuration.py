"""
    Configuration definition used for instantiating
    a log processing pipeline.
"""

from typing import Dict, Iterable

from analyzer.logs.record import LogRecord
from analyzer.pipeline.stage import PipelineStage, PipelineStageResult

from util import topological_sort


# We are not reusing PipelineStage,
# because we call toposort before stage instantiation.
# Otherwise we could be calling 3rd party before config validation!
class PipelineStageDefiniton:
    def __init__(self,
                 module: str,
                 klass: str,
                 name: str,
                 dependencies: Iterable[str]):

        self.module = module
        self.klass = klass
        self.name = name
        self.dependencies = dependencies


class PipelineConfiguration:
    """
        This class represents a parsed and validated pipeline configuration.
    """
    EXPECTED_STAGE_KEYS = ('module', 'class', 'depends_on')

    def __init__(self, stages: Dict[str, dict]):
        from pprint import pformat
        assert stages, 'A pipeline must have at least one stage'

        all_names = stages.keys()
        unique_names = set(all_names)
        assert all_names == unique_names, 'All stages must have unique names'

        errors = []
        validated = []
        for stage, config in stages.items():
            err = PipelineConfiguration.is_stage_config_valid(config)
            if err:
                errors.append(f'{stage}: {err}')
                continue
            validated.append(PipelineStageDefiniton(
                module=config['module'],
                klass=config['class'],
                name=stage,
                dependencies=config.get('depends_on', [])
            ))

        assert not errors, pformat(errors)
        self._stages = validated

    @property
    def stages(self) -> Dict[str, PipelineStage]:
        from copy import deepcopy
        return deepcopy(self._stages)

    @staticmethod
    def is_stage_config_valid(c: Dict[str, dict]) -> Iterable[str]:
        def ensure_target_is_stage() -> Iterable[str]:
            mod = c['module']
            cls = c['class']

            for config_key in c:
                assert config_key in PipelineConfiguration.EXPECTED_STAGE_KEYS

            try:
                from util import import_from
                stage_t = import_from(mod, cls)
                stage = stage_t()
                stage_result = stage.process(record=None, state=None)

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

    def stages_in_order(self):
        def get_dependencies(stage):
            return [
                dep
                for dep
                in self._stages
                if dep.name in stage.dependencies
            ]

        return topological_sort(self._stages, get_dependencies)
