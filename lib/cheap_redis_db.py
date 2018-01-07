import redis
from attr import attrs, attrib, Factory, make_class, asdict

config = {
    'redis_db': None,
}

def set_connection(r):
    config['redis_db'] = r

def find_keys(redis_dir=''):
    r = config['redis_db']
    return [key.decode('utf8') for key in r.keys(f'{redis_dir}:*')]


@attrs
class CheapRecord:
    redis_dir = attrib(default='') # this can be any set of folders e.g. myapp.stuff.blah or blank to live in root key system
    id = attrib(default=0)

    def __attrs_post_init__(self):
        self.adjust_dir_key()
        self.ensure_id_allocator()
        self.save()

    def adjust_dir_key(self):
        if self.redis_dir:
            self.redis_dir += '.'
        self.redis_dir += self.__class__.__name__.lower()

    @property
    def counter_key(self):
        return f'{self.redis_dir}:id'

    @property
    def asdict(self):
        return asdict(self, filter=lambda attr, value: attr.name not in ('redis_db','redis_dir'))

    def ensure_id_allocator(self):
        r = config['redis_db']
        key = self.counter_key
        if r.exists(self.counter_key):
            id = r.get(key).decode('utf-8')
            print(f'redis key {key} already there has val of {id}')
        else:
            r.set(key, self.id)
            print(f'key {key} created', self.id)

    def save(self):
        r = config['redis_db']
        next_key = r.incr(self.counter_key)
        print('id incrmented to', next_key)
        key = f'{self.redis_dir}:{next_key}'
        dic = self.asdict
        dic['id'] = key  # for reference
        r.hmset(key, dic)

    def keys(self):
        # only works on an instance - see the global find_keys() for a more useful version of this
        r = config['redis_db']
        return [key.decode('utf8') for key in r.keys(f'{self.redis_dir}:*')]

    @classmethod
    def purge_all_records(cls, redis_dir='', skip=('id', 'meta')):
        # clears entire db
        if redis_dir:
            redis_dir += f'.{cls.__name__.lower()}'
        else:
            redis_dir = cls.__name__.lower()
        to_delete = []
        for key in find_keys(redis_dir):
            id = key.split(':')[1]
            if id in skip:
                continue
            to_delete.append(key)

        r = config['redis_db']
        print(cls.__name__, 'deleting', *to_delete)
        return

        r.delete(*to_delete)
        keys = find_keys(redis_dir)
        print('done, keys left', keys)

        # reset the counter
        counter_key = f'{redis_dir}:id'
        r.set(counter_key, 0)

