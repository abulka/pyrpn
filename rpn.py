import ast
import logging
from logger import config_log
from program import Program
from scope import Scopes
from labels import FunctionLabels
import settings

log = logging.getLogger(__name__)
config_log(log)


class RecursiveRpnVisitor(ast.NodeVisitor):
    """ recursive visitor with RPN generating capability :-) """

    def __init__(self):
        self.program = Program()
        self.pending_op = ''
        self.scopes = Scopes()
        self.labels = FunctionLabels()
        self.for_loop_info = []
        self.next_local_label = 0
        self.log_indent = 0
        self.first_def = True

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
        elif hasattr(child, 'arg'):
            return child.arg
        else:
            return ''

    def log_state(self, msg=''):
        log.info(f'{self.indent}{msg}')
        log.info(f'{self.indent}{self.scopes.dump()}{self.labels.dump()}')

    def log_children(self, node):
        result = []
        for child in ast.iter_child_nodes(node):
            s = self.get_node_name_id_or_n(child)
            s = f" '{s}'" if s else ""
            result.append(f'({type(child).__name__}{s})')
        s = ', '.join(result)
        if s:
            log.debug(f'{self.indent}{s}')

    def begin(self, node):
        log.info('')
        self.log_indent += 1
        s = self.get_node_name_id_or_n(node)
        s = f"'{s}'" if s else ""
        s += f" op = '{self.pending_op}'" if self.pending_op else ""
        self.log_state(f'BEGIN {type(node).__name__} {s}')
        self.log_children(node)

    def end(self, node):
        # self.log_state(f'END {type(node).__name__}')
        s = f'END {type(node).__name__}'
        log.info(f'{self.indent}{s}')
        # log.info(f'{self.indent}{"-"*len(s)}')
        # log.info('')
        self.log_indent -= 1

    def children_complete(self, node):
        # self.log_state(f'{type(node).__name__} children complete')
        # log.info(f'{self.indent}{type(node).__name__} children complete')
        pass

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
        self.begin(node)

        if self.first_def:
            label = node.name[:7]
            self.program.insert(f'LBL "{label}"')
            self.labels.func_to_lbl(node.name, label=label, called_from_def=True)
            self.first_def = False
        else:
            self.program.insert(f'LBL {self.labels.func_to_lbl(node.name, called_from_def=True)}')

        self.scopes.push()
        self.log_state('scope just pushed')
        self.visit_children(node)
        self.program.insert('RTN')
        self.log_state('scope pre pop')
        self.scopes.pop()
        self.log_state('scope just popped')
        self.end(node)

    def visit_arguments(self,node):
        """ visit arguments to a function"""
        self.begin(node)
        self.visit_children(node)
        self.end(node)

    def visit_arg(self,node):
        """ visit each argument """
        self.begin(node)
        self.program.insert(f'STO {self.scopes.var_to_reg(node.arg)}')
        self.program.insert('RDN')
        self.visit_children(node)
        self.end(node)

    def visit_Assign(self,node):
        """ visit a Assign node and visits it recursively"""
        self.begin(node)
        self.visit_children(node)
        for target in node.targets:
            self.program.insert(f'STO {self.scopes.var_to_reg(target.id)}')
            assert '.Store' in str(target.ctx)
        self.end(node)

    def visit_AugAssign(self,node):
        """ visit a AugAssign e.g. += node and visits it recursively"""
        self.begin(node)
        self.visit_children(node)
        self.program.insert(f'STO{self.pending_op} {self.scopes.var_to_reg(node.target.id)}')
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
        self.pending_op = ''
        self.end(node)

    def visit_Call(self,node):
        """
        Function call. The children are
            - node.func:
                Name node representing the function name. Usually visited first by generic iteration, which is not what
                we want since in rpn the function call goes last.  So we manually iterate.
                Turns out we can skip visiting this.
            - node.args (list):
                Manually looped through and visited.  Each visit emits a register rcl or literal onto the stack.
        """
        self.begin(node)
        for item in node.args:
            self.visit(item)
        # self.visit(node.func)  # don't visit this name cos we emit it ourselves below, RPN style

        if self.for_loop_info and node.func.id == 'range':
            self.program.insert(1000)
            self.program.insert('/')
            self.program.insert('+')
            self.program.insert(f'STO {self.for_loop_info[-1].register}', comment='range')
        else:
            self.program.insert(f'XEQ {self.labels.func_to_lbl(node.func.id)}')
            self.log_state('scope after XEQ')
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
        if '.Load' in str(node.ctx):
            self.program.insert(f'RCL {self.scopes.var_to_reg(node.id)}')
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
            ForLoopItem(register=self.scopes.var_to_reg(node.target.id),
                        label=self.next_local_label))
        self.next_local_label += 1

        log.info(f'{self.indent} in')
        self.visit(node.iter)

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
