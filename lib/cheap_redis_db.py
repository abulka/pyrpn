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

config = {
    'redis_db': None,
}

def set_connection(r):
    config['redis_db'] = r

def find_keys(namespace=''):
    r = config['redis_db']
    return [key.decode('utf8') for key in r.keys(f'{namespace}:*')]


@attrs
class CheapRecord:
    namespace = attrib(default='') # this can be any '.' separated set of names e.g. myapp.stuff.blah or blank to live in root key system
    id = attrib(default=0)  # auto allocated

    def __attrs_post_init__(self):
        self.adjust_dir_key()
        self.ensure_id_allocator()
        self.save()

    def adjust_dir_key(self):
        if self.namespace:
            self.namespace += '.'
        self.namespace += self.__class__.__name__.lower()

    @property
    def id_allocator_key(self):
        return f'{self.namespace}:id'

    @property
    def asdict(self):
        return asdict(self, filter=lambda attr, value: attr.name not in ('redis_db','namespace'))

    def ensure_id_allocator(self):
        r = config['redis_db']
        key = self.id_allocator_key
        if r.exists(self.id_allocator_key):
            id = r.get(key).decode('utf-8')
            print(f'redis key {key} already there has val of {id}')
        else:
            r.set(key, self.id)
            print(f'key {key} created', self.id)

    def save(self):
        r = config['redis_db']
        next_key = r.incr(self.id_allocator_key)
        print('id incrmented to', next_key)
        key = f'{self.namespace}:{next_key}'
        dic = self.asdict
        dic['id'] = key  # for reference
        r.hmset(key, dic)

    def keys(self):
        # only works on an instance - see the global find_keys() for a more useful version of this
        r = config['redis_db']
        return [key.decode('utf8') for key in r.keys(f'{self.namespace}:*')]

    @classmethod
    def purge_all_records(cls, namespace='', skip=('id', 'meta')):
        # clears entire db
        if namespace:
            namespace += f'.{cls.__name__.lower()}'
        else:
            namespace = cls.__name__.lower()
        to_delete = []
        for key in find_keys(namespace):
            id = key.split(':')[1]
            if id in skip:
                continue
            to_delete.append(key)

        r = config['redis_db']
        print(cls.__name__, 'deleting', *to_delete)
        return

        r.delete(*to_delete)
        keys = find_keys(namespace)
        print('done, keys left', keys)

        # reset the counter
        counter_key = f'{namespace}:id'
        r.set(counter_key, 0)

