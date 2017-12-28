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
        self.pending_op = ''
        self.scopes = Scopes()
        self.for_loop_info = []
        self.next_local_label = 0
        self.log_indent = 0
        # Yuk - don't like these one shot attributes - would a stack be better, containing info too?
        self.in_for_loop_in = False
        self.f_pending = False
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

    # Logging support

    @property
    def indent(self):
        return " " * self.log_indent * 4

    def get_node_name_id_or_n(self, child):
        if hasattr(child, 'name'):
            return child.name
        elif hasattr(child, 'id'):
            return child.id
        elif hasattr(child, 'n'):
            return child.n
        else:
            return''

    def log_state(self, msg):
        # log.info(f'{msg}, {self.var_names}, {self.params}, {self.aug_assign_symbol} {self.scope_stack}')
        descr = 'scope' if self.scopes.length == 1 else 'scopes'
        last_info = '' if self.scopes.current_empty else str(self.scopes.current.data)
        # scope_info = f'({self.scopes.length} {descr}) {last_info}'
        scope_info = f'scope {last_info}'

        if self.scopes.current_empty:
            scope_info = ''

        scope_info = ''  # Enable/Disable scope info
        log.info(f'{self.indent}{msg} {self.pending_op} {scope_info}')

    def log_children(self, node):
        for child in ast.iter_child_nodes(node):
            s = self.get_node_name_id_or_n(child)
            log.debug(f'{self.indent}({type(child).__name__} {s})')

    def begin(self, node):
        s = self.get_node_name_id_or_n(node)
        s = f"'{s}'" if s else ''
        self.log_state(f'BEGIN {type(node).__name__} {s}')
        self.log_indent += 1
        self.log_children(node)

    def end(self, node):
        self.log_indent -= 1
        # self.log_state(f'END {type(node).__name__}')
        log.info(f'{self.indent}END {type(node).__name__}')

    def children_complete(self, node):
        # self.log_state(f'{type(node).__name__} children complete')
        # log.info(f'{self.indent}{type(node).__name__} children complete')
        pass

    def func_name_to_lbl(self, func_name):
        return 'A'  # Hack - TODO map this properly

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

        if var_name.isupper():
            register = f'"{var_name.upper()[-7:]}"'
            map_it(var_name, register)
        else:
            map_it(var_name)
            register = self.scopes.get_register(var_name)  # look up what register was allocated e.g. "00"
        # log.debug(f'var_name {var_name} mapped to register {register}')
        return register

    def var_name_is_loop_counter(self, var_name):
        return var_name == 'i'  # hack!  TODO - record this info in scope entry

    # For support

    def body(self, statements):
        for stmt in statements:
            self.visit(stmt)

    def body_or_else(self, node):
        self.body(node.body)
        if node.orelse:
            log.info('else:')
            self.body(node.orelse)

    # Visit functions

    def visit_FunctionDef(self,node):
        """ visit a Function node and visits it recursively"""
        self.scopes.push()
        self.begin(node)
        self.program.insert(f'LBL "{node.name[:7]}"')
        self.visit_children(node)
        self.program.insert('RTN')
        self.scopes.pop()
        self.end(node)

    def visit_arguments(self,node):
        """ visit arguments to a function"""
        self.begin(node)
        self.visit_children(node)
        self.end(node)

    def visit_arg(self,node):
        """ visit each argument """
        self.begin(node)
        self.program.insert(f'STO {self.var_name_to_register(node.arg)}')
        self.program.insert('RDN')
        self.visit_children(node)
        self.end(node)

    def visit_Assign(self,node):
        """ visit a Assign node and visits it recursively"""
        self.begin(node)
        self.visit_children(node)
        for target in node.targets:
            self.program.insert(f'STO {self.var_name_to_register(target.id)}')
            assert '.Store' in str(target.ctx)
        self.end(node)

    def visit_AugAssign(self,node):
        """ visit a AugAssign e.g. += node and visits it recursively"""
        self.begin(node)
        self.visit_children(node)
        self.program.insert(f'STO{self.pending_op} {self.var_name_to_register(node.target.id)}')
        assert '.Store' in str(node.target.ctx)
        self.pending_op = ''
        self.end(node)

    def visit_Return(self,node):
        self.begin(node)
        self.visit_children(node)
        self.end(node)

    def visit_Add(self,node):
        self.begin(node)
        self.pending_op = '+'
        self.end(node)

    def visit_BinOp(self, node):
        """ visit a BinOp node and visits it recursively"""
        self.begin(node)
        self.visit_children(node)
        assert self.pending_op
        self.program.insert(self.pending_op)
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

        # AA1
        self.f_pending = True  # this prevents function name being emitted first by the children visit_Name,
                                # cos it must come out last cos its RPN :-) - see later in this method below...
        # self.log_children(node)
        # self.visit_children(node)
        self.visit(node.func)
        self.f_pending = False

        # self.visit(node.args)  # doesn't loop through list of args!
        # self.generic_visit(node.args)  # loops only through whole node
        for item in node.args:
            self.visit(item)

        # if self.for_loop_info and node.func.id == 'range':
        if self.in_for_loop_in and node.func.id == 'range':
            self.program.insert(1000)
            self.program.insert('/')
            self.program.insert('+')
            self.program.insert(f'STO {self.for_loop_info[-1].register}', comment='range')
        # AA2
        else:
            self.program.insert(f'XEQ {self.func_name_to_lbl(node.func.id)}')

        # self.f_pending = False
        self.end(node)

    @recursive
    def visit_Lambda(self,node):
        """ visit a Function node """
        pass

    @recursive
    def visit_Module(self,node):
        """ visit a Module node and the visits recursively"""
        pass

    def generic_visit(self,node):
        log.warning(f'skipping {node}')
        if getattr(node, 'name', ''):
            log.warning(f'name {node.name}')

    def visit_Name(self, node):
        self.begin(node)
        # log.debug('Name node "%s" node.ctx %s', node.id, node.ctx)
        if node.id == 'range':
            pass # what to do with this situation
        # AA3
        elif self.f_pending:
            pass
        # elif self.f_pending == True and not self.in_for_loop_in:
        #     log.info('zzzzzz visit_Name %s in_for_loop_in %s %s', node.id, self.in_for_loop_in, self.for_loop_info)
        #     self.f_pending = False
        else:
            if '.Load' in str(node.ctx):
                self.program.insert(f'RCL {self.var_name_to_register(node.id)}')
                if self.var_name_is_loop_counter(node.id):
                    self.program.insert('IP')  # just get the integer portion of isg counter
        self.end(node)

    def visit_Num(self, node):
        self.begin(node)
        self.program.insert(str(node.n))
        self.end(node)

    @recursive
    def visit_Expr(self, node):
        pass

    def visit_For(self, node):
        self.begin(node)

        log.info(f'{self.indent} for')
        self.visit(node.target)
        self.for_loop_info.append(
            ForLoopItem(register=self.var_name_to_register(node.target.id),
                        label=self.next_local_label))
        self.next_local_label += 1

        log.info(f'{self.indent} in')
        self.in_for_loop_in = True
        self.visit(node.iter)
        self.in_for_loop_in = False
        log.info(f'{self.indent} :')
        self.program.insert(f'LBL {self.for_loop_info[-1].label:02d}')

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
