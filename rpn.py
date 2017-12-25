import ast
import logging
from logger import config_log
from program import Program
from scope import ScopeStack
import settings

log = logging.getLogger(__name__)
config_log(log)


class RecursiveRpnVisitor(ast.NodeVisitor):
    """ recursive visitor with RPN generating capability :-) """

    def __init__(self, use_scope=True):
        self.program = Program()
        self.var_names = []
        self.params = []
        self.aug_assign_symbol = ''
        self.var_to_register_dict = {}  # maps var names to register numbers
        self.scope_stack = ScopeStack()
        self.use_scope = use_scope
        # self.next_label = 0
        # self.next_variable = 0

    def recursive(func):
        """ decorator to make visitor work recursive """
        def wrapper(self,node):
            func(self,node)
            for child in ast.iter_child_nodes(node):
                self.visit(child)
        return wrapper

    def reset(self):
        self.var_names = []
        self.params = []
        self.aug_assign_symbol = ''

    def log_state(self, msg):
        log.info(f'{msg}, {self.var_names}, {self.params}, {self.aug_assign_symbol} {self.scope_stack}')

    def begin(self, node):
        self.log_state(f'BEGIN {type(node).__name__}')

    def end(self, node):
        self.log_state(f'END {type(node).__name__}')

    def children_complete(self, node):
        self.log_state(f'{type(node).__name__} children complete')

    def visit_children(self, node):
        for child in ast.iter_child_nodes(node):
            self.visit(child)
        self.children_complete(node)

    # Visit functions

    def visit_FunctionDef(self,node):
        """ visit a Function node and visits it recursively"""
        self.scope_stack.push()
        self.begin(node)

        self.program.LBL(node)

        self.visit_children(node)

        self.scope_stack.pop()
        self.end(node)

    def visit_Assign(self,node):
        """ visit a Assign node and visits it recursively"""
        self.scope_stack.allow_mappings = True
        self.begin(node)

        self.visit_children(node)

        self._assign()

        self.scope_stack.allow_mappings = False
        self.end(node)

    def visit_AugAssign(self,node):
        """ visit a AugAssign e.g. += node and visits it recursively"""
        self.scope_stack.allow_mappings = True
        self.begin(node)

        self.visit_children(node)

        self._assign()

        self.scope_stack.allow_mappings = False
        self.end(node)

    def _assign(self):
        """
        var_name might be "x" and we need to map that to a register via our scope system
        possibly use rule that
            if its uppercase - assign to named register e.g. "X"
            otherwise map to a numbered register e.g. 00
        """
        to_register = self.var_to_register(self.var_names[0])
        if self.params:
            # we are assigning a parameter literal to a register
            val = self.params[0]
            self.program.assign(to_register, val, val_type='literal', aug_assign=self.aug_assign_symbol)
        elif len(self.var_names) >= 2:
            # we are assigning another variable to a register
            from_register = self.var_to_register(self.var_names[1])
            self.program.assign(to_register, from_register, val_type='var', aug_assign=self.aug_assign_symbol)
        else:
            raise RuntimeError("yeah dunno what assignment to make")
        self.reset()

    def var_to_register(self, var_name):
        if not self.scope_stack.allow_mappings:
            raise RuntimeError('mappings not enabled')

        if not self.scope_stack.has_mapping(var_name):
            self.scope_stack.add_mapping(var_name)
        register_name = self.scope_stack.get_register(var_name)  # convert name to a register name e.g. "00"
        log.debug(f'var_name {var_name} converted to register {register_name}')

        if self.use_scope:
            return register_name
        else:
            return f'"{var_name.upper()[-7:]}"'

    def visit_Return(self,node):
        log.info(type(node).__name__)
        for child in ast.iter_child_nodes(node):
            self.visit(child)
        self.log_state('END RETURN')
        self.program.RCL(self.var_names[0])

    @recursive
    def visit_Add(self,node):
        log.info(type(node).__name__)
        self.aug_assign_symbol = '+'

    @recursive
    def visit_BinOp(self, node):
        """ visit a BinOp node and visits it recursively"""
        log.info(type(node).__name__)

    def visit_Call(self,node):
        """
        Function call. The child nodes include the function name and the args.  do not use recursive decorator because
        we want more control, and we need to know the end of the calls so that we can generate rpn and clear params

        On the call
            self.visit(node.func)  # will emit the function name
        If we were using the decorator no need to visit explicitly as the recursive decorator will do it for us.
        if no decorator then don't do this call either !!, because visiting the children will do it for us.
        """
        log.info(type(node).__name__)
        for child in ast.iter_child_nodes(node):
            self.visit(child)
        self.log_state('END CALL')
        if 'range' in self.var_names:
            self.program.insert(self.params[0])
            self.program.insert(self.params[1])
        self.reset()

    @recursive
    def visit_Lambda(self,node):
        """ visit a Function node """
        log.info(type(node).__name__)

    @recursive
    def visit_Module(self,node):
        """ visit a Module node and the visits recursively"""
        pass

    def generic_visit(self,node):
        log.warning(f'skipping {node}')
        if getattr(node, 'name', ''):
            log.warning(f'name {node.name}')

    def visit_Name(self, node):
        log.info("visit_Name %s" % node.id)
        self.var_names.append(node.id)

    def visit_Num(self, node):
        log.info(f'Num {node.n}')
        self.push_param(str(node.n))  # always a string

    def push_param(self, val):
        self.params.append(val)

    def visit_For(self, node):
        # self.newline(node)
        log.info('for ')
        self.visit(node.target)
        log.info(' in ')
        self.visit(node.iter)
        log.info(':')
        self.program.insert(1000)
        self.program.insert('/')
        self.program.insert('+')
        self.program.insert('STO 00')
        self.program.insert('LBL 00')
        self.body_or_else(node)
        self.log_state('END FOR')
        self.program.insert('ISG 00')
        self.program.insert('GTO 00')

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

