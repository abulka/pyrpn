import redis
from attr import attrs, attrib
from lib.cheap_redis_db import CheapRecord, config

# r = redis.StrictRedis()
r = redis.StrictRedis(charset="utf-8", decode_responses=True)
# r = redis.StrictRedis('localhost', 6379, charset="utf-8", decode_responses=True)

config.set_connection(r)


@attrs
class Eg(CheapRecord):
    title = attrib(default='Untitled')
    description = attrib(default='this is a title')
    code = attrib(default='code goes here')
    public = attrib(default=True)  # true or false I suppose - is this supported?


@attrs
class Fred(CheapRecord):
    x = attrib(default=0)
    y = attrib(default=0)


config.register_class(Eg, namespace='pyrpn')
config.register_class(Fred)

# Create some records

e1 = Eg(code='def blah(): pass')
e2 = Eg(code='x = 100')
f1 = Fred(x=1, y=2)  # since we didn't register with any namespace, this record will be created under 'fred' in root namespace

print(e1.asdict)
print(f1.asdict)

# listing keys (static calls)

print(Eg.keys())
print(Fred.keys())

# Delete all records (static method calls)

Eg.purge_all_records()
Fred.purge_all_records()

