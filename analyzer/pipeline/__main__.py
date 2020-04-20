'''
Main file for module
'''

from sys import argv, stdin, stderr
from analyzer.pipeline.configuration import PipelineConfiguration
from analyzer.pipeline.pipeline import Pipeline
from analyzer.logs.record import LogRecord


if len(argv) != 2:
    print(f'\nUsage: {argv[0]} <pipeline.yml>', file=stderr)
    exit(1)

import yaml
from analyzer.logs.parsing import gather_records

config_yml = yaml.safe_load(open(argv[1], 'rb').read())
config = PipelineConfiguration(config_yml)
pipeline = Pipeline(config)

for record_lines in gather_records(stdin):
    record = LogRecord('\n'.join(record_lines))
    pipeline.process(record)
