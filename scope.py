from attr import attrs, attrib, Factory
import logging
from logger import config_log

log = logging.getLogger(__name__)
config_log(log)

"""
Scope is a dictionary and can contain name value pairs which map variables to register values
Whenever we go nested, we create another scope which gets added to a scope stack, perhaps.
"""

@attrs
class ScopeStack(object):
    stack = attrib(default=Factory(list))
    _allow_mappings = attrib(default=False)
    next_reg = attrib(default=0)

    def push(self):
        self.stack.append(Scope(start_reg=self.next_reg))

    def pop(self):
        self.next_reg = self.stack[-1].start_reg
        self.stack.pop()

    def add_mapping(self, var, register=None):
        if register == None:
            register = f'{self.next_reg:02d}'
            self.next_reg += 1

        if self._allow_mappings:
            log.debug(f'scope mapping "{var}" to register "{register}" allowed')
            scope = self.stack[-1]
            scope.var_to_registers[var] = register
        else:
            log.debug(f'scope mapping "{var}" to register "{register}" NOT allowed!!')

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
    start_reg = attrib(default=0)
