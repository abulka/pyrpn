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

"""Retreiving info - it all comes out as utf8"""

def utf8_decode_all(data):
    """strips out the utf8 - https://stackoverflow.com/questions/33137741/fastest-way-to-convert-a-dicts-keys-values-from-bytes-to-str-in-python3"""
    data_type = type(data)

    if data_type == bytes: return data.decode()
    if data_type in (str, int): return str(data)

    if data_type == dict: data = data.items()
    return data_type(map(utf8_decode_all, data))

keys = utf8_decode_all(keys)
print('keys stripped of utf8 are', keys)

datas = []
for key in keys:
    if ':id' in key:
        continue
    print('about to retrieve', key)
    data = r.hgetall(key)  # looks like you don't need to encode a key to utf8 to use it - r.hgetall(key.encode('utf8'))
    datas.append(data)

print('users', datas)
print('users as str', utf8_decode_all(datas))
exit(0)

to_delete = []
for key in keys:
    key = key.decode('utf8')
    id = key.split(':')[1]
    if id in ('id', 'meta'):
        continue
    to_delete.append(key)
print('would delete', *to_delete)
r.delete(*to_delete)




"""Cool techniques to auto make attr based classes"""

# UserDb = make_class("UserDb", ["x", "y"], bases=(CheapDb,))

# User = make_class("User",
#                     bases=(CheapDb,),
#                     attrs={
#                         "x": attrib(default=0),
#                         "y": attrib(default=0)
#                     })

