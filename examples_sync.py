import json
import os
from attr import attrs, attrib, evolve, Factory
from examples import example_01
from example_model import Example
import logging
from logger import config_log
import pprint

log = logging.getLogger(__name__)
config_log(log)


@attrs
class MappingInfo():
    filename = attrib(default='')
    redis_id = attrib(default='')
    fingerprint = attrib(default='')

    @property
    def get_has_filename(self):
        return self.filename != ''

    @property
    def get_has_redis(self):
        return self.redis_id != ''

@attrs
class ExamplesSync():
    examples_dir = attrib(default='')
    is_production = attrib(default=False)
    mappings = attrib(default=Factory(list))

    @classmethod
    def create(cls, app_dir, is_production):  # factory, cos no __init__
        examples_dir = os.path.join(app_dir, 'examples_json')
        return ExamplesSync(examples_dir, is_production)

    def __attrs_post_init__(self):
        self.build_mappings()

    def data_from_file(self, filename):
        with open(os.path.join(self.examples_dir, filename), 'r') as f:
            s = f.read()
            data = json.loads(s)
        return data

    def build_mappings(self):
        self.mappings = []

        # Scan the files
        files = os.listdir(self.examples_dir)
        for filename in files:
            info = MappingInfo(filename=filename)
            data = self.data_from_file(filename)
            info.has_filename = True
            info.fingerprint = data['fingerprint']
            self.mappings.append(info)

        # Scan redis
        for redis_id in Example.ids():
            example = Example.get(redis_id)
            found = False
            for info in self.mappings:
                if example.fingerprint and info.fingerprint == example.fingerprint:
                    found = True
                    break
            if not found:
                # ex was not created by a file - create an ex
                info = MappingInfo()
                info.has_filename = False
                info.fingerprint = example.fingerprint
                self.mappings.append(info)
            info.has_redis = True
            info.redis_id = redis_id

        # pprint.pprint(self.mappings)

    def save_to_file(self, example):
        if self.is_production:
            return
        if example.fingerprint:
            filename = f'example_{example.fingerprint}.json'
            dic = example.asdict
            with open(os.path.join(self.examples_dir, filename), 'w') as f:
                f.write(json.dumps(dic, sort_keys=True, indent=4))
            log.info(f'wrote example {filename} to disk')

    def ls(self):
        return os.listdir(self.examples_dir)

    def redis_to_files(self):
        if self.is_production:
            return
        for info in self.mappings:
            if info.redis_id and info.fingerprint:
                example = Example.get(info.redis_id)
                self.save_to_file(example)
        self.build_mappings()

    def files_to_redis(self, delete_redis_extras=False):
        for info in self.mappings:
            if info.has_filename and info.fingerprint and not info.redis_id:
                data = self.data_from_file(info.filename)
                example = Example(**data)
        self.build_mappings()
