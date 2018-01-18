import inspect
from attr import attrs, attrib, Factory, fields

class SelfReport:
    @classmethod
    def get_class_attrs(cls):
        _attrs_all = inspect.getmembers(cls, lambda a: not (inspect.isroutine(a)))
        _attrs_public = [a for a in _attrs_all if not (a[0].startswith('__') and a[0].endswith('__'))]
        names = [tup[0] for tup in _attrs_public]  # we just want the names not the tuples of (name, value)
        return names

@attrs
class A(SelfReport):
    fred = attrib(default=None)

    x = """some string"""
    y = """some string again"""

names = [attr_.name for attr_ in fields(A)]  # use attrs library to find its own special attrib fields
print(names)
print(A.get_class_attrs())  # get just class attributes


# back to regular python

class B(SelfReport):
    m = """some string"""
    n = """some string again"""

print(B.get_class_attrs())  # get just class attributes

