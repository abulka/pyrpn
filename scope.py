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

    # this should be a separate class
    label_data = attrib(default=Factory(dict))  # function name to label name
    next_lbl = attrib(default=0)  # indexes into A-J, a-e
    labels_created_by_proper_def = attrib(default=Factory(list))

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

    # Variables

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

    # Function label support - not scoped

    def add_function_mapping(self, func_name, label=None, called_from_def=False):
        if self.has_function_mapping(func_name) and called_from_def and func_name in self.labels_created_by_proper_def:
            del self.label_data[func_name]
        if self.has_function_mapping(func_name):
            return

        if label == None:
            label = list('ABCDEFGHIJabcdefghij')[self.next_lbl]
            self.next_lbl += 1
        self.label_data[func_name] = label
        if called_from_def and func_name not in self.labels_created_by_proper_def:
            self.labels_created_by_proper_def.append(func_name)

    def has_function_mapping(self, func_name):
        return func_name in self.label_data

    def get_label(self, func_name):
        return self.label_data[func_name]

    @property
    def label_data_empty(self):
        return len(self.label_data) == 0

    # Util

    def dump_short(self):
        result_scopes_list = ['-' if scope.empty else str(scope.data) for scope in self.stack]
        result_labels = '-' if self.label_data_empty else str(self.label_data)
        return '[' + ', '.join(result_scopes_list) + ']' + ' [' + result_labels + ']'

@attrs
class Scope(object):
    data = attrib(default=Factory(dict))  # var name to register name
    next_reg = attrib(default=0)

    @property
    def empty(self):
        return len(self.data) == 0