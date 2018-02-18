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

Note that a scope stack is only necessary to handle the trickling of scope back to global scope
and also to handle nested scopes due to nested functions.  Viz referring to 'x' which doesn't
exist in the current scope might be satisfied by looking at the previous scope or two.
You are typically only ever going to get two or three scopes on this sort of stack.   

This compile time scope stack has nothing to do with runtime stack frame pushing and popping.  Each scope is only a 
compile time concept equivalent to a "code object”, described below: 

Hi Janis,

Thank for the link - I read your article, you explain it well and I understand.  

You use a phrase "code object” which looks like the compile time information about each python function - the offset 
values to use for each variable etc. Then at runtime we push a frame onto the stack based on that code object 
information - including the optimisations Python 3 does that you describe. 
 
Now that we have some terms synchronised I can explain my Python to RPN translator architecture more clearly.  When I 
create code objects, for each Python function that is compiled, instead of mapping variables to offsets that always 
start at ‘0’ (indicating the memory location on a newly pushed stack frame) I instead map to offsets into a fixed 
piece of memory, continually incrementing the offsets and never going backwards. The first Python function’s code 
object might use offsets 0..5, the next Python function’s code object would use 6..8 etc. 

At runtime there are no stack frames created and destroyed. Each function runs and uses its bit of the fixed memory. 
This precludes recursion, as you pointed out. And it uses up more memory because the fixed memory area where 
variables store their stuff is always at maximum size.  But it has been simpler to implement. 

This morning I sketched out a proper dynamic stack frame based approach for my Python to RPN converter, and it looks 
possible.  RPN does support data structures that grow and shrink, and I can implement offsets using a certain RPN 
indirection mechanism. However the price will be the added complexity and the overhead for each function call.  Might 
give it a go sometime anyway! 

cheers,
Andy
www.andypatterns.com  

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
                   force_named=False,
                   is_range_index=False,
                   is_range_index_el=False,
                   is_dict_var=False,
                   is_list_var=False,
                   by_ref_to_var='',
                   is_matrix_var=False,
                   is_complex_var=False,
                   ):
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
        Now supports 'is_matrix_var'
        Now supports 'force_named' boolean
        Now supports 'is_complex_var' which can be used in combination with 'is_matrix'

        :param var_name: python identifier e.g. 'x'
        :param force_reg_name: force the mapping to be to this
        :param is_range_index: record that this is a range loop related var
        :param is_range_index_el: record that this is a list or dict element accessing loop related var
        :param is_dict_var: record that this var is matrix related
        :param is_list_var: record that this var is matrix related
        :param by_ref_to_var: means accessing the variable will instead access the variable 'by_ref_to_var'
        :return: register name as a string
        """

        short_func = var_name[0:7]

        def map_it(var_name, register=None):
            if self._has_mapping(var_name):
                # Do nothing - mapping already exists

                # Upgrade a mapping from numeric to named
                if (is_list_var and var_name not in self.current.list_vars) or \
                        (is_dict_var and var_name not in self.current.dict_vars): # register exists but is not named
                    del self.current.data[var_name]  # delete the mapping
                    register = f'"{short_func}"'
                    map_it(var_name, register)  # call myself!
            else:
                # Create new mapping
                self._add_mapping(var_name, register=register)

                # Track variables which are used in range() for loops
                if is_range_index and var_name not in self.current.for_range_vars:
                    self.current.for_range_vars.append(var_name)

                # Track list vars
                if is_list_var and var_name not in [matrix_var.var_name for matrix_var in self.current.list_vars]:
                    self.current.list_vars.append(MatrixVar(var_name, by_ref_to_var))

                # Track dictionary vars
                if is_dict_var and var_name not in [matrix_var.var_name for matrix_var in self.current.dict_vars]:
                    self.current.dict_vars.append(MatrixVar(var_name, by_ref_to_var))

                # Track matrix vars
                if is_matrix_var and var_name not in [matrix_var.var_name for matrix_var in self.current.matrix_vars]:
                    self.current.matrix_vars.append(MatrixVar(var_name, by_ref_to_var))

                # Track indexes used to access elements of a list or dictionary
                if is_range_index_el and var_name not in self.current.for_el_vars.keys():
                    # Store matrix var so that we know for whom we are an el ref for
                    self.current.for_el_vars[var_name] = ''

        # Track complex vars - can add this attribute on top of any other is_* attribute, thus this code is accessible even if var already mapped
        if is_complex_var and var_name not in [matrix_var.var_name for matrix_var in self.current.complex_vars]:
            self.current.complex_vars.append(MatrixVar(var_name, by_ref_to_var))

        if force_reg_name:
            register = force_reg_name
            map_it(var_name, register)
        elif force_named:
            register = f'"{short_func}"'
            map_it(var_name, register)
        elif var_name.isupper() or force_named:
            register = f'"{short_func.upper()}"'
            map_it(var_name, register)
        elif is_list_var or is_dict_var or is_matrix_var or is_complex_var:  # must be a named register, case doesn't matter
            register = f'"{short_func}"'
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
        if self.is_list(var_name):
            matrix_var = [matrix_var for matrix_var in self.current.list_vars if matrix_var.var_name == var_name][0]
            if matrix_var.by_ref_to_var:
                register = self.get_register(matrix_var.by_ref_to_var)  # get the register of the original by ref to variable, not var_name variable
        elif self.is_dictionary(var_name):
            matrix_var = [matrix_var for matrix_var in self.current.dict_vars if matrix_var.var_name == var_name][0]
            if matrix_var.by_ref_to_var:
                register = self.get_register(matrix_var.by_ref_to_var)  # get the register of the original by ref to variable, not var_name variable
        return register

    def by_ref_to_var(self, var_name):
        to_var = ''
        if self.is_list(var_name):
            matrix_var = [matrix_var for matrix_var in self.current.list_vars if matrix_var.var_name == var_name][0]
            to_var = matrix_var.by_ref_to_var
        elif self.is_dictionary(var_name):
            matrix_var = [matrix_var for matrix_var in self.current.dict_vars if matrix_var.var_name == var_name][0]
            to_var = matrix_var.by_ref_to_var
        return to_var

    # Core

    def _add_mapping(self, var, register=None):
        if register == None:
            register = f'{self.next_reg:02d}'
            self.next_reg += 1
        self.current.data[var] = register

    def _has_mapping(self, var):
        # if len(self.stack) == 0:
        #     return False

        # old original
        # return var in self.current.data

        # new stage 1 trickle scope
        for scope in reversed(self.stack):
            if var in scope.data:
                return True
        return False

    def get_register(self, var):
        # old original
        # return self.current.data[var]

        # new stage 1 trickle scope
        for scope in reversed(self.stack):
            if var in scope.data:
                return scope.data[var]
        raise RpnError(f'no such variable {var}')

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

    def is_list(self, var_name):
        return var_name in [matrix_var.var_name for matrix_var in self.current.list_vars]

    def is_dictionary(self, var_name):
        return var_name in [matrix_var.var_name for matrix_var in self.current.dict_vars]

    def is_matrix(self, var_name):
        return var_name in [matrix_var.var_name for matrix_var in self.current.matrix_vars]

    def is_complex(self, var_name):
        return var_name in [matrix_var.var_name for matrix_var in self.current.complex_vars]

    # Smarter mappings

    def map_el_to_list(self, el_var, list_var):
        assert self.is_el_var(el_var)
        self.current.for_el_vars[el_var] = list_var  # what matrix var this index el is tracking

    def list_var_from_el(self, el_var):
        assert self.is_el_var(el_var)
        return self.current.for_el_vars[el_var]

    # Util

    def calc_var_type(self, var_name):
        if self.is_complex(var_name) and self.is_matrix(var_name):
            return 'complex matrix'
        elif self.is_complex(var_name):
            return 'complex'
        elif self.is_matrix(var_name):
            return 'matrix'
        elif self.is_list(var_name):
            return 'list'
        elif self.is_dictionary(var_name):
            return 'dict'
        else:
            return ''

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
    matrix_vars = attrib(default=Factory(list))  # keep track of var names which are pure matrices
    complex_vars = attrib(default=Factory(list))  # keep track of var names which are complex
    loose_code_allowed = attrib(default=True)  # set to false once have pushed past this point in the stack with a def

    @property
    def empty(self):
        return len(self.data) == 0

