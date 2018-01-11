from attr import attrs, attrib, evolve
from lib import cheap_redis_db

@attrs
class Example(cheap_redis_db.CheapRecord):
    title = attrib(default='Untitled')
    source = attrib(default='python source code goes here')
    description = attrib(default='Description here')
    public = attrib(default='')  # true or false is not supported in redis - only strings are.  Use 'yes' or ''.  Even integers are just strings
    fingerprint = attrib(default='')  # unique uuid/other, independent of the redis id

cheap_redis_db.config.register_class(Example, namespace='pyrpn')

