from attr import attrs, attrib, Factory
import logging
from logger import config_log

log = logging.getLogger(__name__)
config_log(log)

"""
Scope is a dictionary and can contain name value pairs which map variables to register values
Whenever we go nested, we create another scope which gets added to a scope stack, perhaps.

The stack can be empty.
"""

@attrs
class Scopes(object):
    stack = attrib(default=Factory(list))

    def __attrs_post_init__(self):
        self.stack.append(Scope(next_reg=0))  # permanent initial scope

    @property
    def length(self):
        return len(self.stack)

    @property
    def current(self):
        return self.stack[-1]

    @property
    def current_empty(self):
        return len(self.current.data) == 0

    @property
    def next_reg(self):
        return self.stack[-1].next_reg

    @next_reg.setter
    def next_reg(self, val):
        self.stack[-1].next_reg = val

    def push(self):
        self.stack.append(Scope(next_reg=self.next_reg))

    def pop(self):
        if len(self.stack) > 1:  # always leave first permanent scope
            self.stack.pop()

    def add_mapping(self, var, register=None):
        if register == None:
            register = f'{self.next_reg:02d}'
            self.next_reg += 1
        scope = self.stack[-1]
        scope.data[var] = register

    def has_mapping(self, var):
        if len(self.stack) == 0:
            return False
        scope = self.stack[-1]
        return var in scope.data

    def get_register(self, var):
        scope = self.stack[-1]
        return scope.data[var]


@attrs
class Scope(object):
    data = attrib(default=Factory(dict))  # var name to register name
    next_reg = attrib(default=0)
