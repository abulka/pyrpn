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
class ScopeStack(object):
    stack = attrib(default=Factory(list))
    _allow_mappings = attrib(default=False)

    @property
    def next_reg(self):
        if len(self.stack) == 0:
            return 0
        else:
            return self.stack[-1].next_reg

    @next_reg.setter
    def next_reg(self, val):
        if len(self.stack):
            self.stack[-1].next_reg = val

    def push(self):
        self.stack.append(Scope(next_reg=self.next_reg))

    def pop(self):
        self.stack.pop()

    def add_mapping(self, var, register=None):
        if not self._allow_mappings:
            log.debug(f'scope mapping "{var}" to register "{register}" NOT allowed!!')
        else:
            if register == None:
                register = f'{self.next_reg:02d}'
                self.next_reg += 1
            log.debug(f'scope mapping "{var}" to register "{register}" allowed')

            scope = self.stack[-1]
            scope.var_to_registers[var] = register

    def get_register(self, var):
        scope = self.stack[-1]
        return scope.var_to_registers[var]

    @property
    def allow_mappings(self):
        return self._allow_mappings

    @allow_mappings.setter
    def allow_mappings(self, flag):
        self._allow_mappings = flag

@attrs
class Scope(object):
    var_to_registers = attrib(default=Factory(dict))
    next_reg = attrib(default=0)
