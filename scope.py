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

    def push(self):
        self.stack.append(Scope())

    def add_mapping(self, var, register):
        scope = self.stack[-1]
        scope.var_to_registers[var] = register

    def get_register(self, var):
        scope = self.stack[-1]
        return scope.var_to_registers[var]

@attrs
class Scope(object):
    var_to_registers = attrib(default=Factory(dict))
