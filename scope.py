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

    def push(self):
        self.stack.append(Scope(next_reg=self.current.next_reg))

    def pop(self):
        if len(self.stack) > 1:  # always leave first permanent scope
            self.stack.pop()

    def var_to_reg(self, var_name):
        """
        Figure out the register to use to store/recall 'var_name' e.g. "x" via our scope system
        Rules:
            if its uppercase - assign to named uppercase register of the same name e.g. "X"
                (if that name is already used in a previous scope, append __n to the register name e.g. X__2, starting at n=2)
            Otherwise if its a lowercase var name, map to a numbered register e.g. 00

        :param var_name: python identifier e.g. 'x'
        :param use_stack_register: don't use named registers, use the stack. 1 means map to ST X, 2 means map to ST Y etc.
        :return: register name as a string e.g. "X" or 00 - depending on rules
        """
        def map_it(var_name, register=None):
            if not self._has_mapping(var_name):
                self._add_mapping(var_name, register=register)

        if var_name.isupper():
            register = f'"{var_name.upper()[-7:]}"'
            map_it(var_name, register)
        else:
            map_it(var_name)
            register = self.get_register(var_name)  # look up what register was allocated e.g. "00"
        # log.debug(f'var_name {var_name} mapped to register {register}')
        return register

    def _add_mapping(self, var, register=None):
        if register == None:
            register = f'{self.current.next_reg:02d}'
            self.current.next_reg += 1
        self.current.data[var] = register

    def _has_mapping(self, var):
        if len(self.stack) == 0:
            return False
        return var in self.current.data

    def get_register(self, var):
        return self.current.data[var]

    # Util

    def dump(self):
        result_scopes_list = ['-' if scope.empty else str(scope.data) for scope in self.stack]
        return '[' + ', '.join(result_scopes_list) + ']'

@attrs
class Scope(object):
    data = attrib(default=Factory(dict))  # var name to register name
    next_reg = attrib(default=0)

    @property
    def empty(self):
        return len(self.data) == 0