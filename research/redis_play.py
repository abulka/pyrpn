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
    id = attrib(default=0)
    key_base = attrib(default='pyrpn.examplez')

    def __attrs_post_init__(self):
        self.key_base += ':' + self.__class__.__name__.lower()

# UserDb = make_class("UserDb", ["x", "y"], bases=(CheapDb,))
User = make_class("User",
                    bases=(CheapDb,),
                    attrs={
                        "x": attrib(default=0),
                        "y": attrib(default=0)
                    })


u1 = User(x=1, y=2)
print(u1)
print(asdict(u1))

