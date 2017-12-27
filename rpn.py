import ast
import logging
from logger import config_log
from program import Program
from scope import Scopes
import settings

log = logging.getLogger(__name__)
config_log(log)


class RecursiveRpnVisitor(ast.NodeVisitor):
    """ recursive visitor with RPN generating capability :-) """

    def __init__(self):
        self.program = Program()
        self.var_names = []
        self.params = []
        self.aug_assign_symbol = ''
        self.scopes = Scopes()
        self.for_loop_info = []
        self.next_local_label = 0
        self.log_indent = 0

    # Recursion support

    def recursive(func):
        """ decorator to make visitor work recursive """
        def wrapper(self,node):
            func(self,node)
            for child in ast.iter_child_nodes(node):
                self.visit(child)
        return wrapper

    def visit_children(self, node):
        for child in ast.iter_child_nodes(node):
            self.visit(child)
        self.children_complete(node)

    # Reset info

    def reset(self):
        self.var_names = []
        self.params = []
        self.aug_assign_symbol = ''

    # Logging support

    def log_state(self, msg):
        # log.info(f'{msg}, {self.var_names}, {self.params}, {self.aug_assign_symbol} {self.scope_stack}')
        descr = 'scope' if self.scopes.length == 1 else 'scopes'
        last_info = '' if self.scopes.current_empty else str(self.scopes.current.data)
        # scope_info = f'({self.scopes.length} {descr}) {last_info}'
        scope_info = f'scope {last_info}'

        if len(self.var_names) == 0 and len(self.params) == 0 and self.aug_assign_symbol == '':
            state_info = ''
        else:
            state_info = f'{self.var_names}, {self.params}, {self.aug_assign_symbol}'

        if self.scopes.current_empty:
            scope_info = ''

        log.info(f'{" "*4*self.log_indent}{msg} {state_info} {scope_info}')

    def begin(self, node, msg=''):
        self.log_state(f'BEGIN {type(node).__name__} {msg}')
        self.log_indent += 1

    def end(self, node):
        self.log_indent -= 1
        self.log_state(f'END {type(node).__name__}')

    def children_complete(self, node):
        self.log_state(f'{type(node).__name__} children complete')

    # Names and params support

    def push_name(self, name):
        self.var_names.append(name)

    def push_param(self, val):
        self.params.append(val)

    # Assign support

    def _assign(self, reset=True):
        to_register = self.var_name_to_register(self.var_names[0])
        if self.params:
            # we are assigning a parameter literal to a register
            val = self.params[0]
            self.program.assign(to_register, val, val_type='literal', aug_assign=self.aug_assign_symbol)
        elif len(self.var_names) >= 2:
            # we are assigning another variable to a register
            from_register = self.var_name_to_register(self.var_names[1])
            self.program.assign(to_register, from_register, val_type='var', aug_assign=self.aug_assign_symbol)
        else:
            raise RuntimeError("yeah dunno what assignment to make")
        if reset:
            self.reset()

    def perform_op(self, reset=True):
        if len(self.var_names) >= 2:
            # op between two registers
            register1 = self.var_name_to_register(self.var_names[0])
            register2 = self.var_name_to_register(self.var_names[1])
            self.program.insert(f'RCL {register1}')
            self.program.insert(f'RCL {register2}')
        elif self.var_names and self.params:
            # op between a register and a literal
            register1 = self.var_name_to_register(self.var_names[0])
            self.program.insert(f'RCL {register1}')
            self.program.insert(f'{self.params[0]}')
        elif self.params:
            # or just the literal to the previous result
            self.program.insert(f'{self.params[0]}')
        elif self.var_names:
            # or just a register to the previous result
            register = self.var_name_to_register(self.var_names[0])
            self.program.insert(f'RCL {register}')
        else:
            raise RuntimeError('unknown op situation')
        self.program.insert(f'{self.aug_assign_symbol}')
        if reset:
            self.reset()

    def var_name_to_register(self, var_name):
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
            if not self.scopes.has_mapping(var_name):
                self.scopes.add_mapping(var_name, register=register)

        # if use_stack_register != None:
        #     stack_register = ['X', 'Y', 'Z', 'T'][use_stack_register]
        #     register = f'ST {stack_register}'
        #     map_it(var_name, register)
        if var_name.isupper():
            register = f'"{var_name.upper()[-7:]}"'
            map_it(var_name, register)
        else:
            map_it(var_name)
            register = self.scopes.get_register(var_name)  # look up what register was allocated e.g. "00"
        # log.debug(f'var_name {var_name} mapped to register {register}')
        return register

    # For support

    def body(self, statements):
        # self.new_line = True
        # self.indentation += 1
        for stmt in statements:
            self.visit(stmt)
        # self.indentation -= 1

    def body_or_else(self, node):
        self.body(node.body)
        if node.orelse:
            # self.newline()
            log.info('else:')
            self.body(node.orelse)


    # Visit functions

    def visit_FunctionDef(self,node):
        """ visit a Function node and visits it recursively"""
        self.scopes.push()
        self.begin(node)

        self.program.LBL(node)

        self.visit_children(node)

        self.scopes.pop()
        self.end(node)

    def visit_arguments(self,node):
        """ visit arguments to a function"""
        self.begin(node)
        self.visit_children(node)
        for arg_name in self.var_names:
            to_register = self.var_name_to_register(arg_name)
            self.program.STO(to_register)
            self.program.insert('RDN')
            assert not self.scopes.current_empty
        self.reset()
        self.end(node)

    def visit_arg(self,node):
        """ visit each argument """
        self.begin(node)
        self.push_name(node.arg)
        self.visit_children(node)
        self.end(node)

    def visit_Assign(self,node):
        """ visit a Assign node and visits it recursively"""
        self.begin(node)
        self.visit_children(node)
        # self._assign()
        for target in node.targets:
            self.program.insert(f'STO {self.var_name_to_register(target.id)}')
            assert '.Store' in str(target.ctx)

        self.end(node)

    def visit_AugAssign(self,node):
        """ visit a AugAssign e.g. += node and visits it recursively"""
        self.begin(node)
        self.visit_children(node)
        # self._assign()
        if '.Add' in str(node.op):
            op = '+'
        self.program.insert(f'STO{op} {self.var_name_to_register(node.target.id)}')
        assert '.Store' in str(node.target.ctx)
        self.end(node)

    def visit_Return(self,node):
        self.begin(node)
        self.visit_children(node)

        # # if there is a pending operation, perform it and leave result on the stack ready to return
        # # otherwise just recall the register being returned
        # if self.aug_assign_symbol:
        #     self.perform_op()
        # else:
        #     register = self.var_name_to_register(self.var_names[0])
        #     self.program.RCL(register)

        # Another approach
        if self.var_names:
            register = self.var_name_to_register(self.var_names[0])
            self.program.RCL(register)
        elif self.params:
            self.program.insert(self.params[0])
        else:
            pass  # you get what's on the stack?

        self.end(node)

    def visit_Add(self,node):
        self.begin(node)
        # self.program.insert('+')
        assert len(list(ast.iter_child_nodes(node))) == 0  # should be no children
        # self.visit_children(node)
        self.end(node)

    def visit_BinOp(self, node):
        """ visit a BinOp node and visits it recursively"""
        self.begin(node)
        self.visit_children(node)

        # self.perform_op()
        # self._assign(reset=False)  # keep info around... hmmm

        if '.Add' in str(node.op):
            self.program.insert('+')

        self.end(node)

    def visit_Call(self,node):
        """
        Function call. The child nodes include the function name and the args.  do not use recursive decorator because
        we want more control, and we need to know the end of the calls so that we can generate rpn and clear params

        On the call
            self.visit(node.func)  # will emit the function name
        If we were using the decorator no need to visit explicitly as the recursive decorator will do it for us.
        if no decorator then don't do this call either !!, because visiting the children will do it for us.
        """
        self.begin(node)
        self.visit_children(node)
        if self.in_for_loop_in:  # and 'range' in self.var_names:
            # self.program.insert(self.params[0], comment=f'range {self.var_names}')
            # self.program.insert(self.params[1])
            self.program.insert(1000)
            self.program.insert('/')
            self.program.insert('+')

            self.program.insert(f'STO {self.for_loop_info[-1].register}', comment=f'range {self.var_names}')
            self.program.insert(f'LBL {self.for_loop_info[-1].label:02d}')
        self.reset()
        self.end(node)

    @recursive
    def visit_Lambda(self,node):
        """ visit a Function node """
        self.begin(node)

    @recursive
    def visit_Module(self,node):
        """ visit a Module node and the visits recursively"""
        self.begin(node)

    def generic_visit(self,node):
        log.warning(f'skipping {node}')
        if getattr(node, 'name', ''):
            log.warning(f'name {node.name}')

    def visit_Name(self, node):
        self.begin(node, msg=node.id)
        log.debug('Name node %s node.ctx %s', node.id, node.ctx)
        if node.id == 'range':
            pass # what to do with this situation
        else:
            if '.Load' in str(node.ctx):
                self.program.insert(f'RCL {self.var_name_to_register(node.id)}')
        self.end(node)

    def visit_Num(self, node):
        self.begin(node, msg=node.n)
        self.program.insert(str(node.n))
        self.end(node)

    def visit_For(self, node):
        self.begin(node)

        log.info('for ')
        self.visit(node.target)
        self.for_loop_info.append(
            ForLoopItem(register=self.var_name_to_register(node.target.id),
                        label=self.next_local_label))
        self.next_local_label += 1

        log.info(' in ')
        self.in_for_loop_in = True
        self.visit(node.iter)
        self.in_for_loop_in = False
        log.info(':')

        self.body_or_else(node)

        self.program.insert(f'ISG {self.for_loop_info[-1].register}', comment=f'{self.for_loop_info[-1]}')
        self.program.insert(f'GTO {self.for_loop_info[-1].label:02d}')
        self.for_loop_info.pop()
        self.end(node)

from attr import attrs, attrib, Factory

@attrs
class ForLoopItem(object):
    register = attrib(default=0)
    label = attrib(default=0)
