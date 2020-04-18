"""
    Tests for the log processing pipeline.
"""

from analyzer.logs.record import LogRecord
from analyzer.pipeline.configuration import PipelineConfiguration
from analyzer.pipeline.pipeline import Pipeline
from analyzer.pipeline.stage import PipelineStage, PipelineStageResult


INTRODUCTION_PATTERN = (
    "(?:name is|i'm|je suis|ich bin) (?P<name>\\S+)"
)

TAG_INTRO = 'com.example.introduction'


class TagIntroduction(PipelineStage):
    def process(self, record, state):
        if not record:
            return PipelineStageResult()
        from re import search, I
        matches = search(
            INTRODUCTION_PATTERN, record.content, I
        )

        tags = []
        if matches:
            tags.append(TAG_INTRO)

        return PipelineStageResult(tags=tags)


class ExtractIntroducedNames(PipelineStage):
    def process(self, record, state):
        if not record:
            return PipelineStageResult()

        if TAG_INTRO not in state.tags:
            return PipelineStageResult()

        from re import search, I
        matches = search(
            INTRODUCTION_PATTERN, record.content, I
        )

        if matches:
            caps = matches.groupdict()
            return PipelineStageResult(structured={
                TAG_INTRO: {
                    'name': caps['name']
                }
            })

        return PipelineStageResult()


class TestPipeline:
    def test_instantiate_mock_pipeline(self):
        test_pipeline_definition = {
            'tag_records_of_people_introducing_themselves': {
                'module': 'analyzer.pipeline.test_pipeline',
                'class': 'TagIntroduction',
            },
            'extract_names_of_people_introducing_themselves': {
                'module': 'analyzer.pipeline.test_pipeline',
                'class': 'ExtractIntroducedNames',
                'depends_on': 'tag_records_of_people_introducing_themselves'
            }
        }

        config = PipelineConfiguration(test_pipeline_definition)
        pipeline = Pipeline(config)
        header = (
            '2014/Oct/24 19:16:48.062933 111 SYSCALL ' +
            'ExampleComponentTest.ttcn:313(function:ExampleTestedFunction)'
        )
        logs = [
            LogRecord(message)
            for message
            in [
                f"{header} Hi, my name is Sally",
                f"{header} I'm Anne",
                f"{header} I do not introduce myself - ignore me",
                f"{header} Je suis Marianne",
                f"{header} Ich bin Angela"
            ]
        ]
        results = [pipeline.process(r) for r in logs]

        assert len(results) == 5
        assert TAG_INTRO not in results[2].tags
        assert TAG_INTRO not in results[2].structured

        introduced = [r for r in results if TAG_INTRO in r.tags]
        assert len(introduced) == 4
        names = [
            r.structured[TAG_INTRO]['name']
            for r
            in introduced
        ]

        assert names == ['Sally', 'Anne', 'Marianne', 'Angela']
