# module level import
from analyzer.pipeline.configuration import PipelineConfiguration
from analyzer.pipeline.pipeline import Pipeline
from analyzer.logs.record import LogRecord
from analyzer.logs.parsing import gather_records

from sys import argv, stdin, stderr
import yaml

'''
Main file for module
'''


if len(argv) != 2:
    print(f'\nUsage: {argv[0]} <pipeline.yml>', file=stderr)
    exit(1)

config_yml = yaml.safe_load(open(argv[1], 'rb').read())
for stage in config_yml.keys():
    s = config_yml[stage]
    if 'depends_on' in s:
        if type(s['depends_on']) == str:
            config_yml[stage]['depends_on'] = [s['depends_on']]

config = PipelineConfiguration(config_yml)
pipeline = Pipeline(config)

for record_lines in gather_records(stdin):
    record = LogRecord('\n'.join(record_lines))
    pipeline.process(record)
