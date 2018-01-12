import json
import os
from attr import attrs, attrib, evolve, Factory
from example_model import Example
import logging
from logger import config_log
import pprint

log = logging.getLogger(__name__)
config_log(log)


@attrs
class MappingInfo():
    redis_id = attrib(default=0)
    has_file = attrib(default=False)
    filename = attrib(default='')
    title = attrib(default='')
    sortnum = attrib(default=0)

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
        examples_dir = os.path.join(app_dir, 'examples')
        return ExamplesSync(examples_dir, is_production)

    def __attrs_post_init__(self):
        self.build_mappings()

    def filename_strip_ext(self, filename):
        return os.path.splitext(filename)[0]

    def filename_add_ext(self, filename):
        return f'{filename}.json'

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
            info.filename = self.filename_strip_ext(filename)
            info.has_file = True  # by definition
            info.sortnum = data['sortnum']
            info.title = data['title']
            mappings.append(info)

        # Scan redis
        for redis_id in Example.ids():
            example = Example.get(redis_id)
            found = False
            for info in mappings:
                if example.filename and info.filename == example.filename:
                    found = True
                    break
            if not found:
                # ex was not created by a file - create an ex
                info = MappingInfo()
                info.filename = example.filename
                info.sortnum = int(example.sortnum)
                info.title = example.title
                mappings.append(info)
            info.redis_id = redis_id

        self.mappings = sorted(mappings, key=lambda mp: (mp.sortnum, mp.filename, mp.redis_id), reverse=True)
        self._ensure_no_duplicate_filenames()
        # pprint.pprint(self.mappings)

    def _ensure_no_duplicate_filenames(self):
        filenames = [info.filename for info in self.mappings if info.filename]
        if len(list(set(filenames))) != len(filenames):
            raise RuntimeError("multiple occurrences of the same filename %s" % filenames)

    def save_to_file(self, example):
        if self.is_production:
            return
        if example.filename:
            filename = self.filename_add_ext(example.filename)
            dic = example.asdict
            dic['sortnum'] = int(example.sortnum)  # TODO this should be automatic? when create example obj from redis - but how does example obj know since redis fields are all strings!
            del dic['id']  # don't persist the key
            del dic['filename']  # don't persist the filename in the file because we know the filename
            with open(os.path.join(self.examples_dir, filename), 'w') as f:
                f.write(json.dumps(dic, sort_keys=True, indent=4))
            log.info(f'wrote example {filename} to disk')

    def ls(self):
        return os.listdir(self.examples_dir)

    def redis_to_files(self):
        if self.is_production:
            return
        for info in self.mappings:
            if info.redis_id and info.filename:
                example = Example.get(info.redis_id)
                self.save_to_file(example)
        self.build_mappings()

    def files_to_redis(self, delete_redis_extras=False):
        for info in self.mappings:
            if info.has_file and info.filename and not info.redis_id:
                data = self.data_from_file(self.filename_add_ext(info.filename))
                data['filename'] = info.filename
                example = Example(**data)
        self.build_mappings()

    def purge_redis(self):
        Example.purge_all_records()
        log.info('redis db purged of all Example records.')

    def repopulate_redis(self):
        self.build_mappings()
        self.files_to_redis()
        self.redis_to_files()
        log.info('redis db repopulated from example files on disk.')
