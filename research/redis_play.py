import redis
import copy

r = redis.StrictRedis()

example = {
    'id': -1,
    'title': 'this is a title',
    'description': 'this is a description',
    'code': 'code goes here',
    'public': 1,  # true or false I suppose - is this supported?
}

# r.delete('user:id')
# r.delete('user:207', 'user:209')
TEST = False
if TEST:
    if r.exists('user:id'):
        id = r.get('user:id').decode('utf-8')
        print('key user:id already there has val of', id)
    else:
        id = '200'
        r.set('user:id', 200)
        print('key user:id created', id)

    rez = r.incr('user:id')
    print('id incrmented to', rez)

    key = f'user:{rez}'
    dic = copy.copy(example)
    dic['id'] = key  # for reference
    r.hmset(key, dic)

    keys = r.keys('user:*')
    print(keys)

    to_delete = []
    for key in keys:
        key = key.decode('utf8')
        id = key.split(':')[1]
        if id in ('id', 'meta'):
            continue
        to_delete.append(key)
    print('would delete', *to_delete)
    r.delete(*to_delete)


from attr import attrs, attrib, Factory, make_class, asdict

@attrs
class CheapDb:
    redis_db = attrib()  # connection
    redis_dir = attrib(default='') # this can be any set of folders e.g. myapp.stuff.blah or blank to live in root key system
    id = attrib(default=0)

    def __attrs_post_init__(self):
        if self.redis_dir:
            self.redis_dir += '.'
        self.redis_dir += self.__class__.__name__.lower()

        self.make_id_allocator()

    @property
    def counter_key(self):
        return f'{self.redis_dir}:id'

    @property
    def asdict(self):
        return asdict(self, filter=lambda attr, value: attr.name not in ('redis_db','redis_dir'))

    def make_id_allocator(self):
        r = self.redis_db
        key = self.counter_key
        if r.exists(self.counter_key):
            id = r.get(key).decode('utf-8')
            print(f'redis key {key} already there has val of {id}')
        else:
            r.set(key, self.id)
            print(f'key {key} created', self.id)

    def append(self):
        rez = r.incr('user:id')
        print('id incrmented to', rez)

        key = f'user:{rez}'
        dic = copy.copy(example)
        dic['id'] = key  # for reference
        r.hmset(key, dic)


        # self.redis_db.
        asdict(e1)

"""Cool techniques to auto make attr based classes"""

# UserDb = make_class("UserDb", ["x", "y"], bases=(CheapDb,))

# User = make_class("User",
#                     bases=(CheapDb,),
#                     attrs={
#                         "x": attrib(default=0),
#                         "y": attrib(default=0)
#                     })

@attrs
class Eg(CheapDb):
    x = attrib(default=0)
    y = attrib(default=0)


e1 = Eg(redis_db=r, redis_dir='pyrpn', x=1, y=2)
# print(e1, '\n', e1.asdict)
print(e1.asdict)


@attrs
class Fred(CheapDb):
    x = attrib(default=0)
    y = attrib(default=0)

f1 = Fred(redis_db=r, x=1, y=2)
# print(f1, '\n', f1.asdict)
print(f1.asdict)
