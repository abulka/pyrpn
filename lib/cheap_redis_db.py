"""
CheapRecord is a cheap, quick and easy redis db system.

It creates an integer redis key called 'id' which allocates id numbers
It creates a hash with that id as key
The key insight here is that all keys are name-spaced under some name, simply by prefixing them like:
    - KEY      VAL
    - user:id  integer counter being incremented
    - user:0   hash
    - user:1   hash
where 'user' is the namespace.  You can further namespace like this my.silly.user:id
All the name spacing is done automatically, by pulling out the name of the class and using that as the namespace.

Usage:
  See research/redis_cheap_db_play.py

"""

from attr import attrs, attrib, asdict
import logging
from logger import config_log

log = logging.getLogger(__name__)
config_log(log)



# This config and module methods could all be in a class, actually

config = {
    'redis_db': None,
    'class_to_namespace': {}
}

def set_connection(r):
    config['redis_db'] = r

def register_class(cls, namespace=''):
    """
    Registers the full namespace key prefix to store records for 'cls' under.

    :param cls: reference to a class, derived from CheapRecord
    :param namespace: can be any '.' separated set of names e.g. myapp.stuff.blah or blank to live in root key system
    :return: -
    """
    key = cls.__name__.lower()
    namespace = namespace + f'.{key}' if namespace else key
    config['class_to_namespace'][cls.__name__] = namespace


@attrs
class CheapRecord:
    id = attrib(default=0)  # auto allocated

    def __attrs_post_init__(self):
        self.ensure_id_allocator()
        self.save()

    @property
    def namespace(self):
        cls_name = self.__class__.__name__
        if cls_name not in config['class_to_namespace']:
            raise RuntimeError(f'CheapRecord detected unregistered class {cls_name}, please call register_class({cls_name}, [optional namespace])')
        return config['class_to_namespace'][cls_name]

    @property
    def id_allocator_key(self):
        return f'{self.namespace}:id'

    def ensure_id_allocator(self):
        r = config['redis_db']
        key = self.id_allocator_key
        if r.exists(self.id_allocator_key):
            id = r.get(key).decode('utf-8')
            print(f'redis key {key} already there has val of {id}')
        else:
            r.set(key, self.id)
            print(f'key {key} created', self.id)

    @classmethod
    def keys(cls):
        r = config['redis_db']
        namespace = config['class_to_namespace'][cls.__name__]
        return [key.decode('utf8') for key in r.keys(f'{namespace}:*')]

    @property
    def asdict(self):
        return asdict(self, filter=lambda attr, value: attr.name not in ('xxx',))  # filter unused, kept for future use

    def save(self):
        r = config['redis_db']
        next_key = r.incr(self.id_allocator_key)
        print('id incremented to', next_key)
        key = f'{self.namespace}:{next_key}'
        dic = self.asdict
        dic['id'] = key  # for reference
        r.hmset(key, dic) # create the hash in redis

    @classmethod
    def purge_all_records(cls, skip=('id', 'meta')):
        # clears entire db
        r = config['redis_db']
        to_delete = []
        for key in cls.keys():
            id = key.split(':')[1]
            if id in skip:
                continue
            to_delete.append(key)
        print(cls.__name__, 'about to delete', *to_delete)
        # return

        # delete all records
        r.delete(*to_delete)

        # reset the id counter
        namespace = config['class_to_namespace'][cls.__name__]
        counter_key = f'{namespace}:id'
        r.set(counter_key, 0)

        keys = cls.keys()
        print('done, keys left', keys)

