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
        last_info = '' if self.scopes.current_empty else str(self.scopes.current)
        scope_info = f'({self.scopes.length} {descr}) {last_info}'
        log.info(f'{msg}, {self.var_names}, {self.params}, {self.aug_assign_symbol} {scope_info}')

    def begin(self, node):
        self.log_state(f'BEGIN {type(node).__name__}')

    def end(self, node):
        self.log_state(f'END {type(node).__name__}')

    def children_complete(self, node):
        self.log_state(f'{type(node).__name__} children complete')

    # Names and params support

    def push_name(self, name):
        self.var_names.append(name)

    def push_param(self, val):
        self.params.append(val)

    # Assign support

    def _assign(self):
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
        self.reset()

    def var_name_to_register(self, var_name):
        """
        Figure out the register to use to store/recall 'var_name' e.g. "x" via our scope system
        Rules:
            if its uppercase - assign to named uppercase register of the same name e.g. "X"
                (if that name is already used in a previous scope, append __n to the register name e.g. X__2, starting at n=2)
            Otherwise if its a lowercase var name, map to a numbered register e.g. 00

        :param var_name: python identifier e.g. 'x'
        :return: register name as a string e.g. "X" or 00 - depending on rules
        """
        if var_name.isupper():
            register = f'"{var_name.upper()[-7:]}"'  # TODO still have to cater for clash of uppercase in multiple scopes - or do we?  maybe treat as global?
            if not self.scopes.has_mapping(var_name):
                self.scopes.add_mapping(var_name, register=register)
        else:
            if not self.scopes.has_mapping(var_name):
                self.scopes.add_mapping(var_name)
            # look up what register was allocated e.g. "00"
            register = self.scopes.get_register(var_name)
        log.debug(f'var_name {var_name} mapped to register {register}')
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

    def visit_Assign(self,node):
        """ visit a Assign node and visits it recursively"""
        self.begin(node)
        self.visit_children(node)
        self._assign()
        self.end(node)

    def visit_AugAssign(self,node):
        """ visit a AugAssign e.g. += node and visits it recursively"""
        self.begin(node)
        self.visit_children(node)
        self._assign()
        self.end(node)

    def visit_Return(self,node):
        self.begin(node)
        self.visit_children(node)
        self.program.RCL(self.var_name_to_register(self.var_names[0]))
        self.end(node)

    @recursive
    def visit_Add(self,node):
        self.begin(node)
        self.aug_assign_symbol = '+'

    @recursive
    def visit_BinOp(self, node):
        """ visit a BinOp node and visits it recursively"""
        self.begin(node)

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
        if self.in_for_loop_in and 'range' in self.var_names:
            self.program.insert(self.params[0], comment=f'range {self.var_names}')
            self.program.insert(self.params[1])
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
        log.info(f'visit_Name {node.id}')
        self.push_name(node.id)
        self.end(node)

    def visit_Num(self, node):
        log.info(f'visit_Num {node.n}')
        self.push_param(str(node.n))  # always a string
        self.end(node)

    def visit_For(self, node):
        self.begin(node)

        log.info('for ')
        self.visit(node.target)
        self.for_loop_info.append(
            ForLoopItem(register=self.var_name_to_register(self.var_names[0]),
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
