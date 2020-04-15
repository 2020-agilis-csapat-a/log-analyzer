"""
    This module contains definitions related to
    a single stage in a log processing pipeline.
"""

from analyzer.logs.record import LogRecord
from analyzer.util import AutovivifiedDict

from abc import abstractmethod
from typing import Dict, Iterable


class PipelineStageResult:
    """
        Results of a pipeline stage can be one or more of:
         * A set of tags that later stages may rely on
           to identify interesting log records.
         * Some sort of structured data, expressed as a tree of dicts.
         * Nothing at all - not all stages have to yield a result all the time.

        This class ensures that results passed into it can be retrieved
        unmodified regardless of what callers may attempt to do.
    """

    def __init__(
                    self, *,
                    tags: Iterable[str] = None,
                    structured: Dict[str, dict] = None):

        from copy import deepcopy

        if tags:
            self._tags = deepcopy(tags)
        else:
            self._tags = []

        if structured:
            self._structured = AutovivifiedDict(deepcopy(structured))
        else:
            self._structured = AutovivifiedDict()

    def __bool__(self):
        return bool(self.tags or self.structured)

    @property
    def tags(self):
        from copy import deepcopy
        return deepcopy(self._tags)

    @property
    def structured(self):
        from copy import deepcopy
        return AutovivifiedDict(deepcopy(self._structured))


class PipelineStage:
    """
        This function serves as a common base class for all
        stages of a log processing pipeline.

        It provides some common properties related
        to the building of a pipeline and prevents
        certain accidents from happening through immutability.
    """

    def __init__(self, name: str, depends_on: Iterable[str] = []):
        assert name, 'Stage must be given a name'

        self._name = name
        self._dependencies = [*depends_on]

    @property
    def name(self) -> str:
        return self._name

    @property
    def dependencies(self) -> Iterable[str]:
        from copy import deepcopy
        return deepcopy(self._dependencies)

    @abstractmethod
    def process(self, record: LogRecord) -> PipelineStageResult:
        """
            This method *MUST* be overriden by descendants.
            This is the entry point where the pipeline calls into a stage.

            :param record: A log record to process.
            :returns: A PipelineStageResult that may contain tags or data.
        """
