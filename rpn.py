import ast
import logging
from logger import config_log
from program import Program
from scope import Scopes
from labels import FunctionLabels
from attr import attrs, attrib, Factory
import settings
from cmd_list import cmd_list
import rpn_templates
import tokenize

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
        self.needed_templates = []  # extra fragments that need to be emitted at the end
        self.log_indent = 0
        self.first_def_label = None
        self.debug_gen_descriptive_labels = False
        self.node_desc_short = lambda node : str(node)[6:9].strip() + '_' + str(node)[-4:-1].strip()
        self.insert = lambda cmd, label : self.program.insert(f'{cmd} {label.text}', comment=label.description)
        self.inside_alpha = False

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
        log.debug(f'{self.indent}{msg}')
        log.debug(f'{self.indent}{self.scopes.dump()}{self.labels.dump()}')

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
        log.debug('')
        self.log_indent += 1
        s = self.get_node_name_id_or_n(node)
        s = f"'{s}'" if s else ""
        s += f" op = '{self.pending_ops}'" if self.pending_ops else ""
        self.log_state(f'BEGIN {type(node).__name__} {s}')
        self.log_children(node)

    def end(self, node):
        s = f'END {type(node).__name__}'
        log.debug(f'{self.indent}{s}')
        self.log_indent -= 1

    def children_complete(self, node):
        if settings.LOG_AST_CHILDREN_COMPLETE:
            self.log_state(f'{type(node).__name__} children complete')

    def var_name_is_loop_counter(self, var_name):
        return var_name == 'i'  # hack!  TODO - record this info in scope entry

    def find_comment(self, node):
        # Finds comment in the original python source code associated with this token

        # Technique 1
        comment_ = self.atok.find_token(node.first_token, tokenize.COMMENT)  # requires asttokens >= 1.1.8

        # Technique 1A
        def find_line_comment(start_token):
            t = start_token
            while t.type not in (tokenize.COMMENT, tokenize.NL, tokenize.NEWLINE, tokenize.ENDMARKER):
                t = self.atok.next_token(t, include_extra=True)
            return t.string if t.type == tokenize.COMMENT else ''
        comment2 = find_line_comment(node.first_token)

        # Technique 2
        line = node.first_token.line
        comment_i = line.find('#')
        comment = line[comment_i:].strip() if comment_i != -1 else ''

        # assert comment_.string == comment
        assert comment2 == comment
        return comment

    # For visit support

    def body(self, statements):
        for stmt in statements:
            self.visit(stmt)

    def body_or_else(self, node):
        self.body(node.body)
        if node.orelse:
            log.debug('else:')
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

    def split_alpha_text(self, alpha_text):
        first = True
        s = alpha_text
        while s:
            fragment = s[0:14]
            s = s[14:]
            leading_symbol = '' if first else '├'
            first = False
            self.program.insert(f'{leading_symbol}"{fragment}"')  # , comment=alpha_text

    # Finishing up

    def finish(self):
        if 'isg_prepare' in self.needed_templates:
            self.program.insert_raw_lines(rpn_templates.ISG_PREPARE)


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
            self.program.insert(f'STO {self.scopes.var_to_reg(target.id)}', comment=f'{target.id}')
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

    def visit_Pow(self,node):
        """ visit a Power node """
        self.begin(node)
        self.pending_ops.append('Y↑X')
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

        log.debug(self.pending_ops)
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
        # log.debug(list(cmd_list.keys()))
        # log.debug(node.func.id in cmd_list)

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

        # elif func_name == 'AVIEW':
        #     if len(node.args) > 0:
        #         alpha_text = self.get_node_name_id_or_n(node.args[0])
        #         self.split_alpha_text(alpha_text)
        #     self.program.insert(f'{func_name}')
        #     self.end(node)
        #     return

        elif func_name in ('alpha', 'aview', 'print'):
            alpha_text = self.get_node_name_id_or_n(node.args[0])
            self.split_alpha_text(alpha_text)

            if len(node.args) > 0:
                self.inside_alpha = True
                skip_first = True
                for arg in node.args:
                    if skip_first:
                        skip_first = False
                        continue
                    self.visit(arg)
                    # if isinstance(arg, ast.Num):
                    if isinstance(arg, ast.Name):  # probably a recall of a register into stack X
                        self.program.insert('AIP')
                    elif isinstance(arg, ast.Str):  # a literal string
                        pass  # visit_Name will insert a alpha text append for us
                    else:
                        raise RpnError(f'Do not know how to alpha {arg} with value {self.get_node_name_id_or_n(arg)}')
                    # TODO what about string and string concatination etc.?
                self.inside_alpha = False
            if func_name in ('aview', 'print'):
                self.program.insert('AVIEW')
            self.end(node)
            return

        elif func_name == 'list':
            self.program.insert_raw_lines(rpn_templates.LIST_PUSH_POP)
            return

        elif func_name == 'nm':
            self.program.insert_raw_lines(rpn_templates.PRE_LOGIC_NORMALISE)
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

                    # hack if trying to access i
                    if self.var_name_is_loop_counter(arg_val):
                        comment = arg_val + ' (loop var)'
                        register = arg_val = self.scopes.var_to_reg(arg_val)
                        self.program.insert(f'RCL {register}', comment=comment)
                        self.program.insert('IP')  # just get the integer portion of isg counter
                        arg_val = 'ST X'  # access the value in stack x rather than in the register
                        assert cmd_info['indirect_allowed']
                    else:
                        arg_val = self.scopes.var_to_reg(arg_val)

                elif isinstance(arg, ast.Num):
                    arg_val = f'{arg_val:02d}'  # TODO probably need more formats e.g. nnnn
                args += ' ' if arg_val else ''
                args += arg_val
            self.program.insert(f'{func_name}{args}', comment=comment)
            self.end(node)
            return

        if self.for_loop_info and func_name == 'range':

            def all_literals(nodes):
                """
                Look ahead optimisation for ranges with simple number literals as parameters (no expressions or vars)
                But we do cater for Unary operators (e.g. -4) with a tiny little extra lookahead - tricky!
                :return: the list of arguments as numbers, incl all negative signs etc. already applied e.g. [-2, 200, 2]
                """
                arg_vals = []
                for arg in nodes:
                    if not isinstance(arg, ast.Num):
                        if isinstance(arg, ast.UnaryOp):
                            # still could be a literal number if we drill down past the Unary stuff
                            children = [arg.operand, arg.op]  # must do operand first to get the number onto the arg_vals list - not simply list(ast.iter_child_nodes(arg))
                            result = all_literals(children)  # recursive
                            if result:
                                arg_vals.extend(result)
                            else:
                                return []
                        elif isinstance(arg, (ast.UAdd, ast.USub)):
                            if isinstance(arg, ast.USub):
                                arg_vals[-1] = - arg_vals[-1]
                        else:
                            return []
                    else:
                        arg_vals.append(int(self.get_node_name_id_or_n(arg)))
                return arg_vals

            def num_after_point(x):
                # returns the frac digits, excluding the .
                s = str(x)
                if '.' not in s: raise RpnError(f'cannot construct range ISG value based on to of {x}')
                return s[s.index('.') + 1:]

            args = all_literals(node.args)
            if args:
                step_ = args[2] if len(args) == 3 else None
                if len(args) == 1:
                    from_ = 0
                    to_ = args[0]
                elif len(args) in (2, 3):
                    from_ = args[0]
                    to_ = args[1]
                from_ -= step_ if step_ else 1
                to_ -= 1
                # Calculate the .nnnss
                rhs = to_ / 1000
                if step_:
                    rhs += step_ / 100000
                self.program.insert(f'{from_}.{num_after_point(rhs)}')
            else:
                # range call involves complexity (expressions or variables)
                if len(node.args) == 1:
                    # if only one param to range, add implicit 0, which adjusted for ISG means -1
                    # self.program.insert(-1)
                    self.program.insert(0)  # no longer adjusted cos isg routine will do that
                for item in node.args:
                    self.visit(item)
                if len(node.args) in (1, 2):
                    # if step not specified, specify it, because the 'd' isg subroutine needs it, takes 3 params.
                    self.program.insert(1)
                self.program.insert('XEQ d')
                self.needed_templates.append('isg_prepare')
            register = self.for_loop_info[-1].register
            var_name = self.for_loop_info[-1].var_name
            self.program.insert(f'STO {register}', comment=f'range {var_name}')
        else:
            # Common arg parsing for all functions
            for item in node.args:
                self.visit(item)
            # self.visit(node.func)  # don't visit this name cos we emit it ourselves below, RPN style

        if self.for_loop_info and func_name == 'range':
            pass  # already done our work, above
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
        log.debug(f'{self.indent} if')

        f = LabelFactory(local_label_allocator=self.local_labels, descriptive=self.debug_gen_descriptive_labels)
        insert = self.insert

        label_if_body = f.new('if body')
        label_resume = f.new('resume')
        label_else = f.new('else') if len(node.orelse) > 0 else None
        label_elif = f.new('elif') if len(node.orelse) == 1 and isinstance(node.orelse[0], ast.If) else None

        # Begin here

        self.visit(node.test)
        log.debug(f'{self.indent} :')

        """
        At this point, the last line in our rpn program is a test/comparison operator 
        which now needs a couple of gotos added...
        
        We so far have had
            FS? 01      generated by FS(1)
            X<Y?        generated by n > 2
            X>Y?        generated by 1 < 2
            
        We need correct the above and also support other stuff.
        
        a and b
        -------
        should result in a sequence of commands ending in a test.  All the 'if' does is add the gotos.
        so for the and example, we need to:
            - XEQ "LGICNM"  // convert two params into proper booleans
            - AND
            - X≠O?  // we test for truth (non zero) 
        """

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
                log.debug(f'{self.indent} elif')
                insert('LBL', label_elif)
                self.visit(node.test)
                log.debug(f'{self.indent} :')

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
                    log.debug(f'{self.indent} else')
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
        log.debug(f'{self.indent} while')
        self.visit(node.test)
        log.debug(f'{self.indent} :')

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
        log.debug(f'skipping {node}')
        if getattr(node, 'name', ''):
            log.debug(f'name {node.name}')

    def visit_Name(self, node):
        self.begin(node)
        if '.Load' in str(node.ctx):
            assert isinstance(node.ctx, ast.Load)
            self.program.insert(f'RCL {self.scopes.var_to_reg(node.id)}', comment=node.id)
            if self.var_name_is_loop_counter(node.id):
                self.program.insert('IP')  # just get the integer portion of isg counter
        self.end(node)

    def visit_Num(self, node):
        self.begin(node)
        n = int(node.n)
        self.program.insert(f'{self.pending_unary_op}{n}')
        self.pending_unary_op = ''
        self.end(node)

    def visit_Str(self, node):
        self.begin(node)
        if self.inside_alpha:
            self.program.insert(f'├"{node.s[0:15]}"')
        else:
            self.program.insert(f'"{node.s[0:15]}"')
            self.program.insert('ASTO ST X')
        self.end(node)

    @recursive
    def visit_Expr(self, node):
        pass

    # Most of these operators map to rpn in the opposite way, because of the stack order etc.
    # There are 12 RPN operators, p332
    cmpops = {"Eq":"X=Y?",
              "NotEq":"//!=",
              "Lt":"X>Y?",
              "LtE":"//<=",
              "Gt":"X<Y?",
              "GtE":"//>=",
              "Is":"//is",
              "IsNot":"//is not",
              "In":"//in",
              "NotIn":"//not in"}
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

    def visit_Or(self, node):
        self.program.insert('XEQ "LGICNM"')
        self.program.insert('OR')
        self.program.insert('X≠O?', comment='true?')

    def visit_And(self, node):
        self.program.insert('XEQ "LGICNM"')
        self.program.insert('AND')
        self.program.insert('X≠O?', comment='true?')

    def visit_BoolOp(self, node):
        """
        BoolOp(
          op=Or(),
          values=[
            Num(n=1),
            Num(n=0),
            Num(n=1)]))])

        Push each pair and apply OP on-goingly, so as not to blow the stack.
        """
        self.begin(node)
        two_count = 0
        for child in node.values:
            self.visit(child)
            two_count += 1
            if two_count >= 2:
                self.visit(node.op)
        self.end(node)

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

        log.debug(f'{self.indent} for')
        self.visit(node.target)
        varname = node.target.id
        register = self.scopes.var_to_reg(varname)
        self.for_loop_info.append(ForLoopItem(varname, register, label_for))

        log.debug(f'{self.indent} in')
        self.visit(node.iter)

        log.debug(f'{self.indent} :')

        self.resume_labels.append(label_resume)  # just in case we hit a break
        self.continue_labels.append(label_for)  # just in case we hit a continue

        self.insert('LBL', label_for)
        self.program.insert(f'ISG {register}', comment=f'{varname}')
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
