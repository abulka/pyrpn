from attr import attrs, attrib, Factory
import logging
from logger import config_log
from rpn_exceptions import RpnError, source_code_line_info

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

    def var_to_reg(self, var_name,
                   force_reg_name=None,
                   is_range_index=False,
                   is_range_index_el=False,
                   is_dict_var=False,
                   is_list_var=False,
                   by_ref_to_var=''):
        """
        Figure out the register to use to store/recall 'var_name' e.g. 00 or "x" - also taking into account our scope system.

        Rules:
            if variable is lowercase - map to a numbered register e.g. 00
            if variable is uppercase - map to named uppercase register of the same name e.g. "X"
            if variable is_dict_var or is_list_var - map to named register of the same name e.g. "aa" - case unimportant.

        If a named register name is already used in a previous scope, append __n to the register
        name e.g. X__2, starting at n=2)

        Will upgrade a mapping from numeric to named if necessary, if is_dict_var / is_list_var is true

        Now supports 'by reference' for list and dict vars

        :param var_name: python identifier e.g. 'x'
        :param force_reg_name: force the mapping to be to this
        :param is_range_index: record that this is a range loop related var
        :param is_range_index_el: record that this is a list or dict element accessing loop related var
        :param is_dict_var: record that this var is matrix related
        :param is_list_var: record that this var is matrix related
        :param by_ref_to_var: means accessing the variable will instead access the variable 'by_ref_to_var'
        :return: register name as a string
        """
        def map_it(var_name, register=None):
            if self._has_mapping(var_name):
                # Do nothing - mapping already exists

                # Upgrade a mapping from numeric to named
                if (is_list_var and var_name not in self.current.list_vars) or \
                        (is_dict_var and var_name not in self.current.dict_vars): # register exists but is not named
                    del self.current.data[var_name]  # delete the mapping
                    register = f'"{var_name[-7:]}"'
                    map_it(var_name, register)  # call myself!
            else:
                # Create new mapping
                self._add_mapping(var_name, register=register)

                # Track variables which are used in range() for loops
                if is_range_index and var_name not in self.current.for_range_vars:
                    self.current.for_range_vars.append(var_name)

                # Track dictionary vars
                if is_dict_var and var_name not in self.current.dict_vars:
                    self.current.dict_vars.append(var_name)

                # Track list vars
                if is_list_var and var_name not in [matrix_var.var_name for matrix_var in self.current.list_vars]:
                    self.current.list_vars.append(MatrixVar(var_name, by_ref_to_var))

                # Track indexes used to access elements of a list or dictionary
                if is_range_index_el and var_name not in self.current.for_el_vars.keys():
                    # Store matrix var so that we know for whom we are an el ref for
                    self.current.for_el_vars[var_name] = ''

        if force_reg_name:
            register = force_reg_name
            map_it(var_name, register)
        elif var_name.isupper():
            register = f'"{var_name.upper()[-7:]}"'
            map_it(var_name, register)
        elif is_list_var or is_dict_var:  # must be a named register, case doesn't matter
            register = f'"{var_name[-7:]}"'
            map_it(var_name, register)
            register = self.byref_override(var_name, register)
        else:
            map_it(var_name)
            register = self.get_register(var_name)  # look up what register was allocated e.g. "00"
            register = self.byref_override(var_name, register)
        # log.debug(f'var_name {var_name} mapped to register {register}')
        return register

    # By ref

    def byref_override(self, var_name, register):
        # hmmm have to search for it? in self.list_vars
        if self.is_list(var_name):
            matrix_var = [matrix_var for matrix_var in self.current.list_vars if matrix_var.var_name == var_name][0]
            if matrix_var.by_ref_to_var:
                register = self.get_register(matrix_var.by_ref_to_var)  # get the register of the original by ref to variable, not var_name variable
        return register

    def by_ref_to_var(self, var_name):
        to_var = ''
        if self.is_list(var_name):
            matrix_var = [matrix_var for matrix_var in self.current.list_vars if matrix_var.var_name == var_name][0]
            to_var = matrix_var.by_ref_to_var
        # elif self.is_dict(var_name):
        #     FIX...  matrix_var = [matrix_var for matrix_var in self.current.list_vars if matrix_var.var_name == var_name][0]
        return to_var

    # Core

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

    # Is named matrix - has mapping and varname has "

    def is_named_matrix_register(self, var_name):
        assert self._has_mapping(var_name)
        register_name = self.current.data[var_name]
        return '"' in register_name  # presence of " means its a named register - good

    def ensure_is_named_matrix_register(self, var_name, node):
        if not self.is_named_matrix_register(var_name):
            raise RpnError(f'Variable "{var_name}" is not a list or dict type, {source_code_line_info(node)}')

    # Is - extra tracking of ranges, els, lists, dicts

    def is_range_var(self, var_name):
        return var_name in self.current.for_range_vars

    def is_el_var(self, var_name):
        return var_name in self.current.for_el_vars.keys()

    def is_dictionary(self, var_name):
        return var_name in self.current.dict_vars

    def is_list(self, var_name):
        return var_name in [matrix_var.var_name for matrix_var in self.current.list_vars]

    # Smarter mappings

    def map_el_to_list(self, el_var, list_var):
        assert self.is_el_var(el_var)
        self.current.for_el_vars[el_var] = list_var  # what matrix var this index el is tracking

    def list_var_from_el(self, el_var):
        assert self.is_el_var(el_var)
        return self.current.for_el_vars[el_var]

    # Util

    def dump(self):
        result_scopes_list = ['-' if scope.empty else str(scope.data) for scope in self.stack]
        return '[' + ', '.join(result_scopes_list) + ']'

@attrs
class MatrixVar(object):
    var_name = attrib(default='')
    by_ref_to_var = attrib(default='')

# TODO - change for_el_vars to be a list of these instead of generic dicts.
# @attrs
# class ForElVar(object):
#     var_name = attrib(default='')
#     in_matrix_var = attrib(default='')

@attrs
class Scope(object):
    data = attrib(default=Factory(dict))  # var name to register name
    for_range_vars = attrib(default=Factory(list))  # keep track of var names which are used in for loop ranges
    for_el_vars = attrib(default=Factory(dict))  # keep track of var names which are used in for..in loop list/dict element acceses - and what matrix they are tracking
    list_vars = attrib(default=Factory(list))  # keep track of var names which are lists
    dict_vars = attrib(default=Factory(list))  # keep track of var names which are dictionaries

    @property
    def empty(self):
        return len(self.data) == 0

