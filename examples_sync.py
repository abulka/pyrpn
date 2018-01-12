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
    # filename = attrib(default='')
    redis_id = attrib(default=0)
    has_file = attrib(default=False)
    fingerprint = attrib(default='')  # TODO same as filename
    title = attrib(default='')
    sortnum = attrib(default=0)

    # @property
    # def has_filename(self):
    #     return self.filename != ''

    @property
    def has_redis(self):
        return self.redis_id != 0

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

    def filename_to_fingerprint(self, filename):
        return os.path.splitext(filename)[0]

    def fingerprint_to_filename(self, fingerprint):
        return f'{fingerprint}.json'

    def data_from_file(self, filename):
        with open(os.path.join(self.examples_dir, filename), 'r') as f:
            s = f.read()
            data = json.loads(s)
        return data

    def build_mappings(self):
        mappings = []

        # Scan the files - cannot have duplicates because all files in a dir are by definition unique
        files = os.listdir(self.examples_dir)
        for filename in files:
            info = MappingInfo()
            data = self.data_from_file(filename)
            # info.filename = filename
            info.fingerprint = self.filename_to_fingerprint(filename)
            info.has_file = True  # by definition
            info.sortnum = data['sortnum']
            info.title = data['title']
            mappings.append(info)

        # Scan redis
        for redis_id in Example.ids():
            example = Example.get(redis_id)
            found = False
            for info in mappings:
                if example.fingerprint and info.fingerprint == example.fingerprint:
                    found = True
                    # print('found existing info', info)
                    break
            if not found:
                # ex was not created by a file - create an ex
                info = MappingInfo()
                info.fingerprint = example.fingerprint
                info.sortnum = int(example.sortnum)
                info.title = example.title
                mappings.append(info)
            info.redis_id = redis_id

        self.mappings = sorted(mappings, key=lambda mp: (mp.sortnum, mp.fingerprint, mp.redis_id), reverse=True)
        self._ensure_fingerprints_unique()
        # pprint.pprint(self.mappings)

    def _ensure_fingerprints_unique(self):
        fingerprints = [info.fingerprint for info in self.mappings if info.fingerprint]
        if len(list(set(fingerprints))) != len(fingerprints):
            raise RuntimeError("multiple occurrences of the same fingerprint %s" % fingerprints)

    def save_to_file(self, example):
        if self.is_production:
            return
        if example.fingerprint:
            filename = self.fingerprint_to_filename(example.fingerprint)
            dic = example.asdict
            dic['sortnum'] = int(example.sortnum)  # TODO this should be automatic? when create example obj from redis - but how does example obj know since redis fields are all strings!
            del dic['id']  # don't persist the key
            del dic['fingerprint']  # don't persist the fingerprint cos that's the filename
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
            if info.has_file and info.fingerprint and not info.redis_id:
                data = self.data_from_file(self.fingerprint_to_filename(info.fingerprint))
                data['fingerprint'] = info.fingerprint
                example = Example(**data)
        self.build_mappings()
