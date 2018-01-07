import redis
from attr import attrs, attrib
from lib.cheap_redis_db import CheapRecord, set_connection, find_keys, purge_all_records

r = redis.StrictRedis()
set_connection(r)


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


# Create some records

e1 = Eg(redis_dir='pyrpn', code='def blah():\n    pass')  # in 'pyrpn' namespace
f1 = Fred(x=1, y=2)  # in root namespace

print(e1.asdict)
print(f1.asdict)


# listing keys

print(find_keys('fred'))  # static use
print(e1.keys())  # if you have an instance, this is easier

# Delete all records

purge_all_records('pyrpn.eg')

