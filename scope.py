from attr import attrs, attrib, Factory
import logging
from logger import config_log
from rpn_exceptions import RpnError

log = logging.getLogger(__name__)
config_log(log)

"""
Scope is a dictionary and can contain name value pairs which map variables to register values
Whenever we go nested, we create another scope which gets added to a scope stack.

The stack cannot be empty, there is always one permanent scope which is our global scope.
"""


@attrs
class Scopes(object):
    stack = attrib(default=Factory(list))
    next_reg = attrib(default=0)

    def __attrs_post_init__(self):
        self.stack.append(Scope())  # permanent initial scope

    def __len__(self):
        return len(self.stack)

    @property
    def current(self):
        return self.stack[-1]

    @property
    def current_empty(self):
        return len(self.current.data) == 0

    def push(self):
        self.stack.append(Scope())

    def pop(self):
        if len(self.stack) > 1:  # always leave first permanent scope
            self.stack.pop()

    def var_to_reg(self, var_name, force_reg_name=None, is_range_index=False, is_dict_var=False, is_list_var=False):
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

                # Track variables which are used in range() for loops
                if is_range_index and var_name not in self.current.range_vars:
                    self.current.range_vars.append(var_name)

                # Track dictionary vars
                if is_dict_var and var_name not in self.current.dict_vars:
                    self.current.dict_vars.append(var_name)

                # Track list vars
                if is_list_var and var_name not in self.current.list_vars:
                    self.current.list_vars.append(var_name)

        if force_reg_name:
            register = force_reg_name
            map_it(var_name, register)
        elif var_name.isupper():
            register = f'"{var_name.upper()[-7:]}"'
            map_it(var_name, register)
        elif is_list_var or is_dict_var:  # must be a named register, case doesn't matter
            register = f'"{var_name[-7:]}"'
            map_it(var_name, register)
        else:
            map_it(var_name)
            register = self.get_register(var_name)  # look up what register was allocated e.g. "00"
        # log.debug(f'var_name {var_name} mapped to register {register}')
        return register

    def _add_mapping(self, var, register=None):
        if register == None:
            register = f'{self.next_reg:02d}'
            self.next_reg += 1
        self.current.data[var] = register

    def _has_mapping(self, var):
        if len(self.stack) == 0:
            return False
        return var in self.current.data

    def get_register(self, var):
        return self.current.data[var]

    def ensure_is_named_matrix_register(self, var_name):
        assert self._has_mapping(var_name)
        register_name = self.current.data[var_name]
        if not '"' in register_name:  # presence of " means its a named register - good
            raise RpnError(f'Can only assign lists and dictionaries to variable mapped to RPN named variables/register - perhaps "{var_name}" has been previously used to store a normal number/string so has a previous mapping to a numbered register.  Consider using a unique variable name for this list/dict and never store anything into it except lists or dictionaries.')

    def is_range_index(self, var_name):
        return var_name in self.current.range_vars

    def is_dictionary(self, var_name):
        return var_name in self.current.dict_vars

    def is_list(self, var_name):
        return var_name in self.current.list_vars

    # Util

    def dump(self):
        result_scopes_list = ['-' if scope.empty else str(scope.data) for scope in self.stack]
        return '[' + ', '.join(result_scopes_list) + ']'

@attrs
class Scope(object):
    data = attrib(default=Factory(dict))  # var name to register name
    range_vars = attrib(default=Factory(list))  # keep track of var names which are used in for loop ranges
    dict_vars = attrib(default=Factory(list))  # keep track of var names which are dictionaries
    list_vars = attrib(default=Factory(list))  # keep track of var names which are lists

    @property
    def empty(self):
        return len(self.data) == 0