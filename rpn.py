import ast
import logging
from logger import config_log
from program import Program
from scope import Scopes
from labels import FunctionLabels
from attr import attrs, attrib, Factory
import settings
from cmd_list import cmd_list

log = logging.getLogger(__name__)
config_log(log)


class RecursiveRpnVisitor(ast.NodeVisitor):
    """ recursive visitor with RPN generating capability :-) """

    def __init__(self):
        self.program = Program()
        self.pending_op = ''
        self.pending_unary_op = ''
        self.scopes = Scopes()
        self.labels = FunctionLabels()
        self.local_labels = LocalLabels()
        self.for_loop_info = []
        self.log_indent = 0
        self.first_def = True
        self.first_def_name = None

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
        elif hasattr(child, 's'):
            return child.s
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
        s = f'END {type(node).__name__}'
        log.info(f'{self.indent}{s}')
        self.log_indent -= 1

    def children_complete(self, node):
        if settings.LOG_AST_CHILDREN_COMPLETE:
            self.log_state(f'{type(node).__name__} children complete')

    def var_name_is_loop_counter(self, var_name):
        return var_name == 'i'  # hack!  TODO - record this info in scope entry

    # For visit support

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
            self.first_def_name = label
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

    def visit_Mult(self,node):
        self.begin(node)
        self.pending_op = '*'
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
        # log.info(list(cmd_list.keys()))
        # log.info(node.func.id in cmd_list)

        if node.func.id == 'varmenu':
            for arg in node.args:
                self.program.insert(f'MVAR "{arg.s}"')
                self.scopes.var_to_reg(arg.s, force_reg_name=f'"{arg.s}"')
            self.program.insert(f'VARMENU "{self.first_def_name}"')
            self.program.insert('STOP')
            self.program.insert('EXITALL')
            for arg in node.args:
                self.scopes.var_to_reg(arg.s, force_reg_name=f'"{arg.s}"')
            self.end(node)
            return
        elif node.func.id in ('MVAR', 'VARMENU', 'STOP', 'EXITALL'):
            arg = f' "{node.args[0].s}"' if node.args else ''
            self.program.insert(f'{node.func.id}{arg}')

            if node.func.id in ('MVAR',):
                arg = node.args[0].s
                self.scopes.var_to_reg(arg, force_reg_name=f'"{arg}"')
            self.end(node)
            return

        elif node.func.id in cmd_list:

            """
            something wrong here
            we are missing out on
                        
            for item in node.args:
                self.visit(item)
            
            which is needed for proper unary op parsing of -1
            
            perhaps we are being too smart and pulling out args
            when they should be visited properly?
                        
            """
            cmd_info = cmd_list[node.func.id]
            args = ''
            for i in range(cmd_info['num_parameters']):
                arg = node.args[i]
                arg_val = self.get_node_name_id_or_n(arg)
                if 'Name' in str(arg):
                    arg_val = f'"{arg_val}"'
                elif 'Num' in str(arg):
                    arg_val = f'{arg_val:02d}'  # TODO probably need more formats e.g. nnnn
                args += ' ' if arg_val else ''
                args += arg_val
            self.program.insert(f'{node.func.id}{args}', comment=cmd_info['description'])
            self.end(node)
            return

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
        self.program.insert(f'{self.pending_unary_op}{node.n}')
        self.pending_unary_op = ''
        self.end(node)

    @recursive
    def visit_Expr(self, node):
        pass

    @recursive
    def visit_UnaryOp(self, node):
        """
        op=USub(),
        operand=Num(n=1))],
        """
        pass
        print('88'*88)

    @recursive
    def visit_USub(self, node):
        print('88'*88)
        self.pending_unary_op = '-'

    def visit_For(self, node):
        self.begin(node)

        log.info(f'{self.indent} for')
        self.visit(node.target)
        self.for_loop_info.append(
            ForLoopItem(register=self.scopes.var_to_reg(node.target.id),
                        label=self.local_labels.next_local_label))

        log.info(f'{self.indent} in')
        self.visit(node.iter)

        log.info(f'{self.indent} :')
        self.program.insert(f'LBL {self.for_loop_info[-1].label:02d}')

        self.body_or_else(node)

        self.program.insert(f'ISG {self.for_loop_info[-1].register}', comment=f'{self.for_loop_info[-1]}')
        self.program.insert(f'GTO {self.for_loop_info[-1].label:02d}')
        self.for_loop_info.pop()
        self.end(node)


@attrs
class ForLoopItem(object):
    register = attrib(default=0)
    label = attrib(default=0)

@attrs
class LocalLabels(object):
    label_num = attrib(default=0)

    @property
    def next_local_label(self):
        return self.label_num
        self.label_num += 1
