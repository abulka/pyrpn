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
    public = attrib(default='1')  # true or false is not supported in redis - only strings are.  Even integers are just strings


@attrs
class Fred(CheapRecord):
    x = attrib(default=0)
    y = attrib(default=0)


config.register_class(Eg, namespace='pyrpn')
config.register_class(Fred)

# ensure nothing in there - needed for the asserts below to work

Eg.purge_all_records()
Fred.purge_all_records()

# Create some records

e1 = Eg(code='def blah(): pass')
e2 = Eg(code='x = 100')
e3 = Eg(code='y = 6100')
assert len(Eg._keys()) == 3

f1 = Fred(x=1, y=2)  # since we didn't register with any namespace, this record will be created under 'fred' in root namespace
f1.x = 2000
f1.save()
assert len(Fred.ids()) == 1

print(e1.asdict)
print(f1.asdict)

# listing keys and ids (static calls)

print(Eg._keys(), Eg.ids())
print(Fred._keys(), Fred.ids())

# get data, as a dict

print(Eg.get_data(1))

# get actual instance

e = Eg.get(1)
assert e == e1

# delete

Eg.delete_id(e1.id)
e3.delete()
assert len(Eg.ids()) == 1

# Delete all records (static method calls)

dry_run=False
Eg.purge_all_records(dry_run)
Fred.purge_all_records(dry_run)

assert len(Eg.ids()) == 0
assert len(Fred.ids()) == 0
