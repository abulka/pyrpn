import json
import os
from attr import attrs, attrib, evolve
from examples import example_01
from example_model import Example
import logging
from logger import config_log

log = logging.getLogger(__name__)
config_log(log)


@attrs
class ExamplesSync():
    examples_dir = attrib(default='')
    is_production = attrib(default=False)

    @classmethod
    def create(cls, app_dir, is_production):  # factory, cos no __init__
        examples_dir = os.path.join(app_dir, 'examples_json')
        return ExamplesSync(examples_dir, is_production)

    def save_to_file(self, example):
        if self.is_production:
            return
        if example.fingerprint:
            filename = f'example_{example.fingerprint}.json'
            dic = example.asdict
            with open(os.path.join(self.examples_dir, filename), 'w') as f:
                f.write(json.dumps(dic, sort_keys=True, indent=4))
            log.info(f'wrote example {filename} to disk')

    def redis_to_files(self):
        if self.is_production:
            return
        for id in Example.ids():
            example = Example.get(id)
            self.save_to_file(example)
        files = '\n'.join(os.listdir(self.examples_dir))
        return files

    def files_to_redis(self, delete_redis_extras=False):
        files = os.listdir(self.examples_dir)
        report = ''
        for filename in files:
            with open(os.path.join(self.examples_dir, filename), 'r') as f:
                s = f.read()
                dic = json.loads(s)
                fingerprint = dic['fingerprint']
                report += f'File {filename} - found fingerprint "{fingerprint}" in this file\n'

                """
                scan to see if redis has an example with this fingerprint
                if yes - update it
                if no - create it 
                """
                for id in Example.ids():
                    example = Example.get(id)
                    if example.fingerprint == fingerprint:
                        report += f'  found corresponding redis record {example.id}\n'

                return report

