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

class RpnError(Exception):
    pass

class RecursiveRpnVisitor(ast.NodeVisitor):
    """ recursive visitor with RPN generating capability :-) """

    def __init__(self):
        self.program = Program()
        self.pending_ops = []
        self.pending_unary_op = ''
        self.scopes = Scopes()
        self.labels = FunctionLabels()
        self.local_labels = LocalLabels()
        self.resume_labels = []  # created by the current while or for loop so that break and continue know where to go
        self.continue_labels = []  # created by the current while or for loop so that break and continue know where to go
        self.for_loop_info = []
        self.log_indent = 0
        self.first_def_label = None
        self.debug_gen_descriptive_labels = False
        self.node_desc_short = lambda node : str(node)[6:9].strip() + '_' + str(node)[-4:-1].strip()
        self.insert = lambda cmd, label : self.program.insert(f'{cmd} {label.text}', comment=label.description)


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
        s += f" op = '{self.pending_ops}'" if self.pending_ops else ""
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

    def find_comment(self, node):
        # Finds comment in the original python source code associated with this token
        line = node.first_token.line
        comment_i = line.find('#')
        return line[comment_i:] if comment_i != -1 else ''

    # For visit support

    def body(self, statements):
        for stmt in statements:
            self.visit(stmt)

    def body_or_else(self, node):
        self.body(node.body)
        if node.orelse:
            log.info('else:')
            self.body(node.orelse)

    def has_rpn_def_directive(self, node):
        return 'rpn: export' in self.find_comment(node)

    def check_rpn_def_directives(self, node):
        # Adds an additional string label to the rpn code
        comment = self.find_comment(node)
        if 'rpn: export' in comment:
            label = node.name[:7]
            self.program.insert(f'LBL "{label}"', comment=f'def {node.name} (rpn: export)')

    def make_global_label(self, node):
        label = f'"{node.name[:7]}"'
        self.program.insert(f'LBL {label}')
        self.labels.func_to_lbl(node.name, label=label, called_from_def=True)
        return label

    def make_local_label(self, node):
        self.program.insert(f'LBL {self.labels.func_to_lbl(node.name, called_from_def=True)}', comment=f'def {node.name}')

    # Visit functions

    def visit_FunctionDef(self,node):
        """ visit a Function node and visits it recursively"""
        self.begin(node)

        if not self.first_def_label:
            self.first_def_label = self.make_global_label(node)  # main entry point to rpn program
        else:
            if not self.has_rpn_def_directive(node):
                self.make_local_label(node)
            elif self.labels.has_function_mapping(node.name):
                self.make_local_label(node)
                self.check_rpn_def_directives(node)
            else:
                self.make_global_label(node)

        self.scopes.push()

        self.visit_children(node)

        if self.program.lines[-1].text != 'RTN':
            self.program.insert('RTN', comment=f'end def {node.name}')

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
        self.program.insert(f'STO {self.scopes.var_to_reg(node.arg)}', comment=f'param: {node.arg}')
        self.program.insert('RDN')
        self.visit_children(node)
        self.end(node)

    def visit_Return(self,node):
        """
        Child nodes are:
            - node.value
        """
        self.begin(node)
        self.visit_children(node)
        self.program.insert(f'RTN', comment='return')
        self.end(node)

    def visit_Assign(self,node):
        """ visit a Assign node and visits it recursively"""
        self.begin(node)
        self.visit_children(node)
        for target in node.targets:
            comment = self.find_comment(target)
            self.program.insert(f'STO {self.scopes.var_to_reg(target.id)}', comment=f'{target.id} = {comment}')
            assert '.Store' in str(target.ctx)
            assert isinstance(target.ctx, ast.Store)
        self.end(node)

    def visit_AugAssign(self,node):
        """ visit a AugAssign e.g. += node and visits it recursively"""
        self.begin(node)
        self.visit_children(node)
        self.program.insert(f'STO{self.pending_ops[-1]} {self.scopes.var_to_reg(node.target.id)}')
        assert '.Store' in str(node.target.ctx)
        assert isinstance(node.target.ctx, ast.Store)
        self.pending_ops.pop()
        self.end(node)

    def visit_Add(self,node):
        self.begin(node)
        self.pending_ops.append('+')
        self.end(node)

    def visit_Sub(self,node):
        self.begin(node)
        self.pending_ops.append('-')
        self.end(node)

    def visit_Mult(self,node):
        self.begin(node)
        self.pending_ops.append('*')
        self.end(node)

    def visit_Div(self,node):
        self.begin(node)
        self.pending_ops.append('/')
        self.end(node)

    def visit_BinOp(self, node):
        """
        visit a BinOp node and visits it recursively,
        Child nodes are:
            - node.left
            - node.op
            - node.right

        Operator precedence has already taken care of in the building of the AST.

        We visit in a certain order left, right, op because this suits our rpn output.
        The default visit order when using `self.visit_children(node)` is op, left, right - no good.

        It doesn't matter if we do left, right or right, left - operators will stack up
        before being resolved, so we do need a stack of operators, and we risk blowing the rpn stack.
        """
        self.begin(node)

        self.visit(node.left)
        self.visit(node.right)
        self.visit(node.op)

        log.info(self.pending_ops)
        assert self.pending_ops
        if len(self.pending_ops) > 4:
            raise RpnError("We blew our expression stack %s" % self.pending_ops)
        # assert len(self.pending_ops) == 1  # TODO if this is true, then we don't need a op list
        self.program.insert(self.pending_ops[-1])
        self.pending_ops.pop()
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

        func_name = node.func.id
        if func_name == 'FS':
            func_name = 'FS?'  # Hack to allow question marks

        if func_name == 'varmenu':
            for arg in node.args:
                self.program.insert(f'MVAR "{arg.s}"')
                self.scopes.var_to_reg(arg.s, force_reg_name=f'"{arg.s}"')
            self.program.insert(f'VARMENU {self.first_def_label}')
            self.program.insert('STOP')
            self.program.insert('EXITALL')
            for arg in node.args:
                self.scopes.var_to_reg(arg.s, force_reg_name=f'"{arg.s}"')
            self.end(node)
            return
        elif func_name in ('MVAR', 'VARMENU', 'STOP', 'EXITALL'):
            arg = f' "{node.args[0].s}"' if node.args else ''
            self.program.insert(f'{func_name}{arg}')

            if func_name in ('MVAR',):
                arg = node.args[0].s
                self.scopes.var_to_reg(arg, force_reg_name=f'"{arg}"')
            self.end(node)
            return

        elif func_name in cmd_list and cmd_list[func_name]['num_arg_fragments'] > 0:
            # The built-in command has arg fragment "parameter" parts which must be emitted immediately as part of the
            # command, thus we cannot rely on normal visit parsing but must look ahead and extract needed info.
            cmd_info = cmd_list[func_name]
            args = ''
            comment = cmd_info['description']
            for i in range(cmd_info['num_arg_fragments']):
                arg = node.args[i]
                arg_val = self.get_node_name_id_or_n(arg)
                if isinstance(arg, ast.Str):
                    arg_val = f'"{arg_val}"'
                if isinstance(arg, ast.Name):  # reference to a variable, thus pull out a register name
                    comment = arg_val
                    arg_val = self.scopes.var_to_reg(arg_val)
                elif isinstance(arg, ast.Num):
                    arg_val = f'{arg_val:02d}'  # TODO probably need more formats e.g. nnnn
                args += ' ' if arg_val else ''
                args += arg_val
            self.program.insert(f'{func_name}{args}', comment=comment)
            self.end(node)
            return

        # if only one param to range, add implicit 0, which adjusted for ISG means -1
        if self.for_loop_info and func_name == 'range' and len(node.args) == 1:
            self.program.insert(-1)

        for item in node.args:
            self.visit(item)
        # self.visit(node.func)  # don't visit this name cos we emit it ourselves below, RPN style

        if self.for_loop_info and func_name == 'range':
            self.program.insert(1000)
            self.program.insert('/')
            self.program.insert('+')
            register = self.for_loop_info[-1].register
            var_name = self.for_loop_info[-1].var_name
            self.program.insert(f'STO {register}', comment=f'range {var_name}')
        elif func_name in cmd_list:
            # The built-in command is a simple one without command arg fragment "parameter" parts - yes it may take
            # actual parameters but these are generated through normal visit parsing and available on the stack.
            self.program.insert(f'{func_name}', comment=cmd_list[func_name]['description'])
        else:
            label = self.labels.func_to_lbl(func_name)
            comment = f'{func_name}()' if not self.labels.is_global_def(func_name) else ''  # only emit comment if local label
            self.program.insert(f'XEQ {label}', comment=comment)
            self.log_state('scope after XEQ')
        self.end(node)

    def visit_If(self, node):
        """
        If's sub-nodes are:
            - test
            - body
            - orelse
        where orelse[0] might be another if node (elif situation) otherwise might be a body (else situation)
        or the orelse list might be empty (no else situation).
        """
        self.begin(node)
        log.info(f'{self.indent} if')

        self.visit(node.test)
        log.info(f'{self.indent} :')

        f = LabelFactory(local_label_allocator=self.local_labels, descriptive=self.debug_gen_descriptive_labels)
        insert = self.insert

        label_if_body = f.new('if body')
        label_resume = f.new('resume')
        label_else = f.new('else') if len(node.orelse) > 0 else None
        label_elif = f.new('elif') if len(node.orelse) == 1 and isinstance(node.orelse[0], ast.If) else None

        insert('GTO', label_if_body)
        if label_elif: insert('GTO', label_elif)
        elif label_else: insert('GTO', label_else)
        else: insert('GTO', label_resume)

        insert('LBL', label_if_body)
        self.body(node.body)

        if label_else:
            insert('GTO', label_resume)

        more_elifs_coming = lambda node : len(node.orelse) == 1 and isinstance(node.orelse[0], ast.If)
        while True:
            else_ = node.orelse
            if len(else_) == 1 and isinstance(else_[0], ast.If):
                node = else_[0]
                log.info(f'{self.indent} elif')
                insert('LBL', label_elif)
                self.visit(node.test)
                log.info(f'{self.indent} :')

                label_elif_body = f.new('elif body')

                insert('GTO', label_elif_body)

                if more_elifs_coming(node):
                    label_elif = f.new('elif')
                    insert('GTO', label_elif)
                else:
                    insert('GTO', label_else)

                insert('LBL', label_elif_body)
                self.body(node.body)
                insert('GTO', label_resume)
            else:
                if len(else_) > 0:
                    log.info(f'{self.indent} else')
                    insert('LBL', label_else)
                    self.body(else_)
                break

        insert('LBL', label_resume)
        self.end(node)

    def visit_While(self,node):
        """
        visit a While node.  Children nodes are:
            - test
            - body
            - orelse
        """
        self.begin(node)

        f = LabelFactory(local_label_allocator=self.local_labels, descriptive=self.debug_gen_descriptive_labels)
        insert = self.insert

        label_while = f.new('while')
        insert('LBL', label_while)
        log.info(f'{self.indent} while')
        self.visit(node.test)
        log.info(f'{self.indent} :')

        label_while_body = f.new('while body')
        label_resume = f.new('resume')
        label_else = f.new('else') if len(node.orelse) > 0 else None

        self.resume_labels.append(label_resume)  # just in case we hit a break
        self.continue_labels.append(label_while)  # just in case we hit a continue

        insert('GTO', label_while_body)
        if label_else: insert('GTO', label_else)
        else: insert('GTO', label_resume)

        insert('LBL', label_while_body)
        self.body(node.body)
        insert('GTO', label_while)

        if label_else:
            insert('LBL', label_else)
            self.body(node.orelse)

        insert('LBL', label_resume)
        self.end(node)

    @recursive
    def visit_Break(self,node):
        """ visit a Break node """
        if self.resume_labels:
            label = self.resume_labels.pop()
            self.insert('GTO', label)

    @recursive
    def visit_Continue(self,node):
        """ visit a Continue node """
        if self.continue_labels:
            label = self.continue_labels.pop()
            self.insert('GTO', label)

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
            assert isinstance(node.ctx, ast.Load)
            self.program.insert(f'RCL {self.scopes.var_to_reg(node.id)}', comment=node.id)
            if self.for_loop_info:
                self.program.insert('1')  # adjust the for loop end by -1 to conform to python range
                self.program.insert('-')
            if self.var_name_is_loop_counter(node.id):
                self.program.insert('IP')  # just get the integer portion of isg counter
        self.end(node)

    def visit_Num(self, node):
        self.begin(node)
        n = int(node.n)
        if self.for_loop_info:
            n -= 1  # adjust the for loop end by -1 to conform to python range
        self.program.insert(f'{self.pending_unary_op}{n}')
        self.pending_unary_op = ''
        self.end(node)

    def visit_Str(self, node):
        self.begin(node)
        # self.program.insert(f'{self.pending_unary_op}"{node.s}"')
        # self.pending_unary_op = ''
        self.program.insert(f'"{node.s}"')
        self.program.insert('ASTO ST X')
        self.end(node)

    @recursive
    def visit_Expr(self, node):
        pass

    # Most of these operators map to rpn in the opposite way, because of the stack order etc.
    cmpops = {"Eq":"X=Y?", "NotEq":"//!=", "Lt":"X>Y?", "LtE":"//<=", "Gt":"X<Y?", "GtE":"//>=",
              "Is":"//is", "IsNot":"//is not", "In":"//in", "NotIn":"//not in"}
    def visit_Compare(self, node):
        """
        A comparison of two or more values. left is the first value in the comparison, ops the list of operators,
        and comparators the list of values after the first. If that sounds awkward, that’s because it is:
            - left
            - ops
            - comparators
        """
        self.begin(node)

        self.visit(node.left)
        for o, e in zip(node.ops, node.comparators):
            self.visit(e)
            self.program.insert(self.cmpops[o.__class__.__name__])

        self.end(node)

    @recursive
    def visit_UnaryOp(self, node):
        """
        op=USub(),
        operand=Num(n=1))],
        """
        pass

    @recursive
    def visit_Pass(self, node):
        pass

    @recursive
    def visit_USub(self, node):
        self.pending_unary_op = '-'

    def visit_For(self, node):
        self.begin(node)

        f = LabelFactory(local_label_allocator=self.local_labels, descriptive=self.debug_gen_descriptive_labels)
        insert = self.insert

        label_for = f.new('for')
        label_for_body = f.new('for body')
        label_resume = f.new('resume')

        log.info(f'{self.indent} for')
        self.visit(node.target)
        self.for_loop_info.append(
            ForLoopItem(var_name=node.target.id,
                        register=self.scopes.var_to_reg(node.target.id),
                        label=label_for))

        log.info(f'{self.indent} in')
        self.visit(node.iter)

        log.info(f'{self.indent} :')

        self.resume_labels.append(label_resume)  # just in case we hit a break
        self.continue_labels.append(label_for)  # just in case we hit a continue

        self.insert('LBL', label_for)
        self.program.insert(f'ISG {self.for_loop_info[-1].register}', comment=f'{self.for_loop_info[-1]}')
        self.for_loop_info.pop()
        self.insert('GTO', label_for_body)
        self.insert('GTO', label_resume)

        self.insert('LBL', label_for_body)
        self.body_or_else(node)

        self.insert('GTO', label_for)
        insert('LBL', label_resume)
        self.end(node)


@attrs
class ForLoopItem(object):
    var_name = attrib(default='')
    register = attrib(default=0)
    label = attrib(default=0)


@attrs
class LocalLabels(object):
    label_num = attrib(default=0)

    @property
    def next_local_label(self):
        result = self.label_num
        self.label_num += 1
        return f'{result:02d}'


@attrs
class LabelFactory(object):
    local_label_allocator = attrib()
    descriptive = attrib(default=False)
    next_elif_num = attrib(default=1)
    next_elif_body_num = attrib(default=1)

    def new(self, description):
        # Creates a new label via the smart label factory
        if description == 'elif':
            description = f'{description} {self.next_elif_num}'
            self.next_elif_num += 1
        elif description == 'elif body':
            description = f'{description} {self.next_elif_body_num}'
            self.next_elif_body_num += 1
        label_text = description if self.descriptive else self.local_label_allocator.next_local_label
        return Label(text=label_text, description=description)

@attrs
class Label(object):
    text = attrib(default='')
    description = attrib(default='')
