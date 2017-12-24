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

    def push(self):
        self.stack.append(Scope())

    def pop(self):
        self.stack.pop()

    def add_mapping(self, var, register):
        if self._allow_mappings:
            log.debug('scope mappings allowed')
            scope = self.stack[-1]
            scope.var_to_registers[var] = register
        else:
            log.debug('scope mappings NOT allowed')

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
