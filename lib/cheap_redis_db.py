"""
CheapRecord is a cheap, quick and easy redis db system.

It creates a single integer redis object with a key called 'blah:id' which allocates id numbers.
For each record it creates a redis hash object under a key 'blah:1' or 'blah:2' etc
Note 'blah' is the namespace.
For our purposes id's are integers 1..n and keys are the actual redis keys (which will be the namespace : id).

The key insight here is that whilst all redis keys live in the one root namespace we can simulate namespaces.
All keys for a record are name-spaced under some name, simply by prefixing them with colon viz:
    - KEY      VAL
    - user:id  integer counter being incremented
    - user:0   hash
    - user:1   hash
where 'user' is the namespace (which by convention is the CheapRecord classname in lower case).  We then use the :id
key as an integer id, which we increment when allocating id numbers for all 'records' in the e.g. 'user' namespace.
In reality the keys are flat in the main root of redis, but appear as if they are in directories using redis commandser UI.

All the name spacing is done automatically by CheapRecord, by pulling out the name of the class and using that as the
namespace.  Plus you can prepend addition namespacing when you register your class with _CheapRecordManager.  So you
can end up with keys like 'my.silly.user:id'

Only works with decode_responses=True at the moment.

# db = redis.StrictRedis()
db = redis.StrictRedis('localhost', 6379, charset="utf-8", decode_responses=True)

Usage:
    See research/redis_cheap_db_play.py

"""

from attr import attrs, attrib, asdict
import logging
from logger import config_log

log = logging.getLogger(__name__)
config_log(log)


class _CheapRecordManager:
    def __init__(self):
        self.redis_conn = None
        self.class_to_namespace = {}
        self.initial_id = 0

    def set_connection(self, r):
        self.redis_conn = r

    def register_class(self, cls, namespace=''):
        """
        Registers the full namespace key prefix to store records for 'cls' under.

        :param cls: reference to a class, derived from CheapRecord
        :param namespace: can be any '.' separated set of names e.g. myapp.stuff.blah or blank to live in root key system
        :return: -
        """
        key = cls.__name__.lower()
        namespace = namespace + f'.{key}' if namespace else key
        self.class_to_namespace[cls.__name__] = namespace

    def get_namespace(self, cls):
        cls_name = cls.__name__
        if cls_name not in self.class_to_namespace:
            raise RuntimeError(f'CheapRecord detected unregistered class {cls_name}, please call register_class({cls_name}, [optional namespace])')
        return self.class_to_namespace[cls_name]


config = _CheapRecordManager()


@attrs
class CheapRecord:
    id = attrib(default=None)  # id will be auto allocated

    def __attrs_post_init__(self):
        self._ensure_id_allocator_created()
        if self.id:
            self.id = int(self.id)  # just in case we get an id as string, force it to be an int always
        self.save()

    @classmethod
    def _get_namespace(cls):
        return config.get_namespace(cls)

    @classmethod
    def _get_id_allocator_key(cls):
        return f'{cls._get_namespace()}:id'

    @classmethod
    def _keys(cls):
        r = config.redis_conn
        namespace = cls._get_namespace()
        # return [key.decode('utf8') for key in r.keys(f'{namespace}:*')]
        keys = r.keys(f'{namespace}:*')
        if f'{namespace}:id' in keys:
            keys.remove(f'{namespace}:id')
        return keys

    @classmethod
    def ids(cls):
        ids = [int(key.split(':')[1]) for key in cls._keys()]
        ids.sort()
        return ids

    @classmethod
    def get_data(cls, id):
        # returns dict of data only
        r = config.redis_conn
        namespace = config.get_namespace(cls)
        key = f'{cls._get_namespace()}:{id}'
        data = r.hgetall(key)  # looks like you don't need to encode a key to utf8 to use it - otherwise would need to: r.hgetall(key.encode('utf8'))
        return data

    @classmethod
    def get(cls, id):
        # returns actual instance
        data = cls.get_data(id)
        if data:
            instance = cls(**data)
            return instance
        else:
            return None

    @classmethod
    def delete_id(cls, id):
        """
        """
        r = config.redis_conn
        key = f'{cls._get_namespace()}:{id}'
        if r.exists(key):
            r.delete(key)
            log.debug(f'deleted {key}')
            assert not r.exists(key)

    def delete(self):
        self.delete_id(self.id)

    @classmethod
    def _ensure_id_allocator_created(cls):
        r = config.redis_conn
        key = cls._get_id_allocator_key()  # represents the next ID to allocate, stores last value allocated
        if r.exists(key):
            id = r.get(key)
            # log.debug(f'redis key {key} already there has val of {id}')
        else:
            cls._reset_id_allocator()

    @property
    def asdict(self):
        # return asdict(self, filter=lambda attr, value: attr.name not in ('xxx',))  # filter unused, kept for future use
        return asdict(self)

    def save(self):
        """
        The first save will allocate the id and create the record, subsequent saves will update the existing record.
        :return: -
        """
        r = config.redis_conn
        if self.id == None:
            self.id = r.incr(self._get_id_allocator_key())
        key = f'{self._get_namespace()}:{self.id}'
        dic = self.asdict
        r.hmset(key, dic) # set the hash in redis, creating it if it isn't there

    @classmethod
    def purge_all_records(cls, dry_run=False):
        # clears entire db
        r = config.redis_conn
        to_delete = cls._keys()
        if dry_run:
            log.debug(cls.__name__, 'would delete', *to_delete)
            return
        if to_delete:
            r.delete(*to_delete)
        cls._reset_id_allocator()

    @classmethod
    def _reset_id_allocator(cls):
        r = config.redis_conn
        key = cls._get_id_allocator_key()
        r.set(key, config.initial_id)  # reset the id counter
        log.debug(f'id_allocator {key} reset')

    """
    Important: true or false is not supported in redis - only strings are.  
    CheapDB convention is to use 'yes' or '' strings to indicate boolean.
    Even integers are just strings
    
    When creating wtforms which require booleans, use the utility methods below 
    to convert from our convention into what wtforms need.
    
    Note: the resulting wtform object may have a rendered output of value='y' 
    but this has nothing to do with our yes/'' - the true indicator is the presence
    of 'checked' in the html of the <input type='checkbox'...> which means true,
    its absence means html input is unchecked. 
    """

    @staticmethod
    def redis_bool_to_bool(redis_val):
        # hack to convert redis bool of 'y'/'' into real bool
        return redis_val == 'yes'

    @staticmethod
    def bool_to_redis_bool(val):
        # hack to convert bool into redis bool of 'y'/''.  Returns the value to store into redis
        return 'yes' if val else ''

