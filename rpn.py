import ast
from logger import config_log
from program import Program
from scope import Scopes
from labels import FunctionLabels
from attr import attrs, attrib, Factory
import settings
from cmd_list import cmd_list
import tokenize
import logging
from rpn_exceptions import RpnError

log = logging.getLogger(__name__)
config_log(log)

class RecursiveRpnVisitor(ast.NodeVisitor):
    """ recursive visitor with RPN generating capability :-) """

    def __init__(self):
        self.program = Program()
        self.pending_ops = []
        self.pending_stack_args = []
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
        self.inside_alpha = False
        self.alpha_append_mode = False
        self.alpha_already_cleared = False
        self.alpha_separator = ' '
        self.inside_binop = False
        self.disallow_string_args = False
        self.inside_list_access = False
        self.def_params_as_ints = False

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

    @property
    def indent_during(self):
        # if want to output messages inside a begin..end log pair
        return " " * (self.log_indent + 1) * 4

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
        self.log_pending_args()

    def log_pending_args(self):
        log.debug(f'{self.indent}{self.pending_stack_args}')

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
        return self.scopes.is_range_index(var_name)

    def find_comment(self, node):
        # Finds comment in the original python source code associated with this token.
        # See my discussion of various techniques at https://github.com/gristlabs/asttokens/issues/10
        def find_line_comment(start_token):
            t = start_token
            while t.type not in (tokenize.COMMENT, tokenize.NL, tokenize.NEWLINE, tokenize.ENDMARKER):
                t = self.atok.next_token(t, include_extra=True)
            return t.string if t.type == tokenize.COMMENT else ''
        return find_line_comment(node.first_token)

    # Visit support methods

    def body(self, statements):
        for stmt in statements:
            self.visit(stmt)

    def body_or_else(self, node):
        self.body(node.body)
        if node.orelse:
            log.debug('else:')
            self.body(node.orelse)

    def has_rpn_def_directive(self, node):
        comment = self.find_comment(node)
        return 'rpn: ' in comment and 'export' in comment

    def has_rpn_int_directive(self, node):
        comment = self.find_comment(node)
        return 'rpn: ' in comment and 'int' in comment

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

    def split_alpha_text(self, alpha_text, append=False):
        if alpha_text == '':
            if not append:
                self.program.insert('CLA')
        else:
            first = True
            s = alpha_text
            if append:
                first = False
            while s:
                fragment = s[0:14]
                s = s[14:]
                leading_symbol = '' if first else '├'
                first = False
                self.program.insert(f'{leading_symbol}"{fragment}"')  # , comment=alpha_text

    def check_supported(self, name, node):
        if name in ['NOT', 'OR', 'AND']:
            raise RpnError(f'The RPN command "{name}" is not supported - use native Python instead, line: {node.lineno}\n{node.first_token.line.strip()}')

    def is_built_in_cmd_with_param_fragments(self, func_name, node):
        return func_name in cmd_list and \
               cmd_list[func_name]['num_arg_fragments'] > 0

    def cmd_st_x_situation(self, func_name, node):
        # if its a variable reference, then we can happily construct an all in one cmd with fragment e.g. VIEW 00
        # otherwise its a cmd_st_x_situation situation where we visit recurse normally and then do a ST X as arg to the built in command
        return func_name in settings.CMDS_WHO_NEED_LITERAL_NUM_ON_STACK_X and \
               not isinstance(node.args[0], ast.Name)

    def friendly_type(self, node):
        if isinstance(node, ast.Dict):
            type_ = '(matrix type Dictionary)'
        elif isinstance(node, ast.List):
            type_ = '(matrix type List)'
        else:
            type_ = ''
        return type_

    # Finishing up

    def finish(self):
        self.program.emit_needed_rpn_templates()

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

        if self.has_rpn_int_directive(node):
            self.def_params_as_ints = True

        self.visit_children(node)

        if self.program.lines[-1].text != 'RTN':
            self.program.insert('RTN', comment=f'end def {node.name}')

        self.scopes.pop()
        self.def_params_as_ints = False
        self.end(node)

    def visit_arguments(self,node):
        """ visit arguments to a function"""
        self.begin(node)

        # reorder parameters into reverse order, ready for mapping and storage into registers
        num_args = len(node.args)
        if num_args in (0, 1):
            pass
        elif num_args == 2:
            self.program.insert_xeq('p2Param', comment='reorder 2 params for storage')
        elif num_args == 3:
            self.program.insert_xeq('p3Param', comment='reorder 3 params for storage')
        elif num_args == 4:
            self.program.insert_xeq('p4Param', comment='reorder 4 params for storage')
        else:
            raise RpnError(f'cannot handle more then four parameters to a function (4 level stack, remember), sorry.  You have {num_args}.')

        self.visit_children(node)
        self.end(node)

    def visit_arg(self,node):
        """ visit each argument """
        self.begin(node)
        if self.def_params_as_ints:
            self.program.insert('IP')
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
        if self.program.is_previous_line('string'):
            self.program.insert('ASTO ST X')
        self.program.insert(f'RTN', comment='return')
        self.end(node)

    def process_list_access(self, subscript_node):
        self.inside_list_access = True
        self.visit(subscript_node.value)  # RCL list name

        prepare_for_access = """
            XEQ "p1DMtx"
            INDEX "ZLIST"
        """
        self.program.insert_raw_lines(prepare_for_access)

        # Get the y:row onto the stack
        assert isinstance(subscript_node.slice, ast.Index)
        self.visit(subscript_node.slice.value)  # the index value

        code = f"""
            1        // y:row (adjust from 0 based to 1)
            +
            1        // x:column
            STOIJ
        """
        self.program.insert_raw_lines(code)
        self.inside_list_access = False

    def process_dict_access(self, subscript_node):
        # at this point the value we are assigning has already been emitted

        self.inside_list_access = True
        self.visit(subscript_node.value)  # RCL list name

        prepare_for_access = """
            XEQ "p2DMtx"
            //RDN  // get rid of matrix on stack **NEW
            INDEX "ZLIST"  // cos now all access via ZLIST matrix
        """
        self.program.insert_raw_lines(prepare_for_access)

        # Get the y:row onto the stack
        assert isinstance(subscript_node.slice, ast.Index)
        self.visit(subscript_node.slice.value)  # the key value

        # Need to translate the key into an index value by searching
        # ideally a hash function, but that's too complex re dealing with clashes etc.
        # j_col_value = 2  # always
        # i_row_key = 1  # hack for now, pending a lookup search
        code = f"""
            XEQ "p2DFindKey" // convert key on stack to i_row_key
            2                // j_col_value (always 2)
            X<>Y 
            STOIJ
            //RDN            // drop I,J off stack
            //RDN
        """
        self.program.insert_raw_lines(code)
        self.inside_list_access = False

    def visit_Assign(self,node):
        """ visit a Assign node and visits it recursively
            - targets
            - value
        """
        self.begin(node)
        self.assign_push_rhs(node)
        for target in node.targets:
            self.assign_assert_target_ok(target)
            if isinstance(target, ast.Subscript):
                self.assign_subscript_is_on_lhs(target)
            else:
                self.assign_normal_lhs(node, target)
        self.pending_stack_args = []  # must have, cos could just be assigning single values, not BinOp and not Expr
        self.end(node)

    def assign_assert_target_ok(self, target):
        assert '.Store' in str(target.ctx)
        assert isinstance(target.ctx, ast.Store)
        self.assert_assign_ensure_uppercase_for_matrices(target)

    def assign_normal_lhs(self, node, target):
        # Create the variable and mark its type
        type_ = self.friendly_type(node.value)
        log.info(f'{self.indent_during}variable "{target.id}" created {type_}')
        self.program.insert_sto(
            self.scopes.var_to_reg(target.id,
                                   is_dict_var=isinstance(node.value, ast.Dict)),
            comment=f'{target.id} {type_}')

    def assign_subscript_is_on_lhs(self, target):
        var_name = target.value.id  # drill into subscript to get it
        log.debug(f'{self.indent_during}subscript detected {var_name}')
        assert isinstance(target.ctx, ast.Store)
        if var_name.islower():
            raise RpnError(
                f'Can only assign dictionaries to uppercase variables not "{var_name}".  Please change the variable name to uppercase e.g. "{var_name.upper()}".')
        if self.scopes.is_dictionary(var_name):
            self.process_dict_access(target)
        else:
            self.process_list_access(target)
        code = """
            RCL ST T
            STOEL
            """
        self.program.insert_raw_lines(code)
        # if self.scopes.is_dictionary(var_name):
        self.program.insert_sto(self.scopes.var_to_reg(var_name), comment=f'{var_name}')  # needed for any dict or list

    def assert_assign_ensure_uppercase_for_matrices(self, target):
        # THIS SHOULD BE REMOVED
        # This is because lists are implemented as RPN matrices which need to be stored in a named register.
        # And can only specify named registers in my Python RPN converter by specifying uppercase variable name.
        # Arguably could allow lower case variables to be assigned to, and simply automatically map them to lowercase named registers BINGO!!!! YES!!!
        # This code happens when a = [] or a = {} because there is no subscript on l.h.s
        if self.program.is_previous_line_matrix_related() and target.id.islower():
            log.debug(f'previous line is {self.program.last_line}')
            raise RpnError(
                f'Can only assign lists to uppercase variables not "{target.id}".  Please change the variable name to uppercase e.g. "{target.id.upper()}".')

    def assign_push_rhs(self, node):
        self.visit(node.value)  # a single Num or Str or Name or List (of elements)
        if isinstance(node.targets[0], ast.Subscript) and self.program.is_previous_line(
                'string'):  # hack (looking ahead at first target to see if we are assigning to a list element)
            self.program.insert('ASTO ST X')

    def visit_AugAssign(self,node):
        """ visit a AugAssign e.g. += node and visits it recursively"""
        self.begin(node)
        self.visit_children(node)
        self.program.insert(f'STO{self.pending_ops[-1]} {self.scopes.var_to_reg(node.target.id)}')
        assert '.Store' in str(node.target.ctx)
        assert isinstance(node.target.ctx, ast.Store)
        self.pending_ops.pop()
        self.pending_stack_args = []  # must have, cos could just be assigning single values, not BinOp and not Expr
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
        self.inside_binop = True  # TODO probably should be a stack

        self.visit(node.left)
        # self.log_pending_args()

        self.visit(node.right)
        # self.log_pending_args()

        if len(self.pending_stack_args) > 4:
            raise RpnError(f'Potential RPN stack overflow detected - expression too complex for 4 level stack - simplify! {self.pending_stack_args}')

        self.visit(node.op)

        """
        The expression "x -= 1.0/i" will result in pending_ops growing to ['-', '/'] thus yes, we need pending_ops to be a stack. 
        """
        # Never gets triggered. pending_ops never gets above 2, no matter how complex the expression.  the operators
        # don't stack up so much as the parameters on the stack, which we track with pending_stack_args
        if len(self.pending_ops) > 4:
            raise RpnError("Potential RPN stack overflow detected - we blew our expression operator stack %s" % self.pending_ops)

        self.program.insert(self.pending_ops[-1])
        self.pending_ops.pop()

        if len(self.pending_stack_args) >= 2:
            self.pending_stack_args.pop()
            self.pending_stack_args.pop()
            self.pending_stack_args.append('_result_')  # to account for the two args to this binop) and then push a 'result'
            self.log_pending_args()

        self.inside_binop = False
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

        if isinstance(node.func, ast.Attribute) and node.func.attr == 'append':
            var_name = self.get_node_name_id_or_n(node.func.value)  # the name 'a' of the a.append()
            if var_name.islower():
                raise RpnError(f'Lists must be stored in uppercase variables not "{var_name}".  Please change the variable name to uppercase e.g. "{var_name.upper()}".')
            self.visit(node.func.value)
            self.program.insert_xeq('p1DMtx', comment=f'{node.first_token.line.strip()}')
            for arg in node.args:
                self.visit(arg)
                self.program.insert_xeq('LIST+')
            self.program.insert_sto(self.scopes.var_to_reg(node.func.value.id), comment=f'{node.func.value.id}')
            self.end(node)
            return


        func_name = node.func.id

        self.check_supported(func_name, node)

        if func_name == 'isFS':
            func_name = 'pFS'

        if func_name == 'isFC':
            func_name = 'pFC'


        if func_name in cmd_list and len(node.args) == 0:

            # Check that built in command has been given enough parameters
            if cmd_list[func_name]['num_arg_fragments'] > 0:
                raise RpnError(f'{func_name} requires {cmd_list[func_name]["num_arg_fragments"]} parameters to be supplied')

            # Check that built in command has been given parameters (anti stack philosophy), even though HP41S spec actually allows params
            elif func_name in settings.CMDS_WHO_OPERATE_ON_STACK_SO_DISALLOW_NO_ARGS:
                raise RpnError(f'{func_name} requires parameters (variable or literal number) to be supplied - referring to stack x not allowed')


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

        elif func_name in ('aview',):
            raise RpnError('The command "aview" is deprecated - use print or AVIEW.')

        elif func_name in ('alpha', 'AVIEW', 'print', 'PROMPT', 'PRA'):
            if len(node.args) == 0:
                if func_name != 'AVIEW':
                    self.program.insert('CLA', comment='empty string', type_='string')
            else:
                self.inside_alpha = True
                self.alpha_append_mode = False
                self.alpha_already_cleared = False

                for keyword in node.keywords:
                    if keyword.arg == 'sep':
                        if not isinstance(keyword.value, ast.Str):
                            raise RpnError(f'sep= must be a string separator')
                        self.alpha_separator = keyword.value.s
                    elif keyword.arg == 'append':
                        if not isinstance(keyword.value, ast.NameConstant):
                            raise RpnError(f'append= must be set to True or False')
                        named_constant_t_f = keyword.value
                        self.alpha_append_mode = named_constant_t_f.value

                for index,arg in enumerate(node.args):
                    self.visit(arg)  # usual insertion of a literal number, string or variable

                    if isinstance(arg, ast.Num):
                        self.program.insert('ARCL ST X')
                    elif isinstance(arg, ast.Name):
                        if self.var_name_is_loop_counter(arg.id):
                            self.program.insert('ARCL ST X')
                    elif isinstance(arg, ast.Str):
                        pass
                    elif isinstance(arg, ast.BinOp):   # other types?
                        self.program.insert('ARCL ST X')
                    elif isinstance(arg, ast.Subscript):
                        self.program.insert('ARCL ST X')
                    # else:
                    #     raise RpnError(f'Do not know how to alpha {arg} with value {self.get_node_name_id_or_n(arg)}')

                    if not self.alpha_append_mode:
                        self.alpha_append_mode = True

                    if self.alpha_separator and index + 1 < len(node.args):  # don't emit separator on last item
                        self.program.insert(f'├"{self.alpha_separator}"')

                self.inside_alpha = False
                self.alpha_append_mode = False
                self.alpha_already_cleared = False
                self.alpha_separator = ' '

            if func_name in ('print', 'AVIEW'):
                self.program.insert('AVIEW')
            elif func_name in ('PROMPT'):
                self.program.insert('PROMPT')
            elif func_name in ('PRA'):
                self.program.insert('PRA')

            if len(self.pending_stack_args):
                self.pending_stack_args.pop()
            self.end(node)
            return

        # # DEBUG
        # elif func_name in self.program.rpn_templates.template_names:
        #     # insert any rpn template by name - use for debugging
        #     self.program.rpn_templates.need_template(func_name)
        #     return

        elif func_name == 'PyLibAll':
            self.program.rpn_templates.need_all_templates()
            return

        elif self.is_built_in_cmd_with_param_fragments(func_name, node) and not self.cmd_st_x_situation(func_name, node):
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
                if to_ > 1000:
                    raise RpnError(f'for range() loops are limited to max to value of 999 (ISG ccccccc.fffii limitation of fff')
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
                    # if step not specified, specify it, because the rpn lib isg subroutine needs it - takes 3 params.
                    self.program.insert(1)
                self.program.insert_xeq('pISG')
            register = self.for_loop_info[-1].register
            var_name = self.for_loop_info[-1].var_name
            self.program.insert(f'STO {register}', comment=f'range {var_name}')
        else:
            # Common arg parsing for all functions
            # Note: we don't visit self.visit(node.func) cos we emit the function name ourselves below, RPN style
            if func_name in settings.CMDS_WHO_DISALLOW_STRINGS:
                self.disallow_string_args = True
            for item in node.args:
                self.visit(item)
            self.disallow_string_args = False

        if self.for_loop_info and func_name == 'range':
            pass  # already done our work, above

        elif func_name in cmd_list:
            # The built-in command is a simple one without command arg fragment "parameter" parts - yes it may take
            # actual parameters but these are generated through normal visit parsing and available on the stack.
            # Though we do handle an exception where the command needs to use ST X as its 'parameter' e.g. VIEW
            if func_name in settings.CMDS_WHO_NEED_PARAM_SWAPPING:
                self.program.insert('X<>Y', comment='change order of params to be more algebraic friendly')
            arg_val = ' ST X' if self.cmd_st_x_situation(func_name, node) else ''  # e.g. VIEW
            self.program.insert(f'{func_name}{arg_val}', comment=cmd_list[func_name]['description'])

        elif func_name in self.program.rpn_templates.get_user_insertable_pyrpn_cmds().keys():
            # Call to a rpn template function - not usually allowed, but some are exposed
            self.program.insert_xeq(func_name)
        else:
            # Local subroutine call to a local user python def - map these to a local label A..e (15 max)
            label = self.labels.func_to_lbl(func_name)
            comment = f'{func_name}()' if not self.labels.is_global_def(func_name) else ''  # only emit comment if local label
            self.program.insert(f'XEQ {label}', comment=comment)
            self.log_state('scope after XEQ')
        self.pending_stack_args = []  # TODO though if the call is part of an long expression, we could be prematurely clearing
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
        self.pending_stack_args = []

        """
        At this point, the last line in our rpn program is a boolean value.
        We now add the test for truth and a couple of gotos...
        """
        self.program.insert('X≠0?', comment='if true?')

        insert('GTO', label_if_body)                # true

        if label_elif: insert('GTO', label_elif)    # false/else/elif
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
                self.program.insert('X≠0?', comment='if true?')

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
        self.pending_stack_args = []
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
        self.pending_stack_args = []

        label_while_body = f.new('while body')
        label_resume = f.new('resume')
        label_else = f.new('else') if len(node.orelse) > 0 else None

        self.resume_labels.append(label_resume)  # just in case we hit a break
        self.continue_labels.append(label_while)  # just in case we hit a continue

        """
        At this point, the last line in our rpn program is a boolean value.
        We now add the test for truth and a couple of gotos...
        """
        self.program.insert('X≠0?', comment='while true?')

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
        self.pending_stack_args = []
        self.end(node)

    def visit_List(self,node):
        """
        Children nodes are:
            - elts (list of elements)
        """
        self.begin(node)
        self.program.insert('0', comment='not a matrix (empty)')
        self.program.insert_xeq('p1DMtx')
        for child in node.elts:
            self.visit(child)
            if self.program.is_previous_line('string'):
                self.program.insert('ASTO ST X')
            self.program.insert_xeq('LIST+')
        self.end(node)

    def visit_Dict(self,node):
        """
        Child nodes are:
            - keys
            - values
        """
        self.begin(node)
        self.program.insert('0', comment='not a matrix (empty)')
        self.program.insert_xeq('p2DMtx')
        for index, key in enumerate(node.keys):
            self.visit(key)
            if self.program.is_previous_line('string'):
                self.program.insert('ASTO ST X')
            self.visit(node.values[index])  # corresponding value
            if self.program.is_previous_line('string'):
                self.program.insert('ASTO ST X')
            self.program.insert_xeq('LIST+')
        self.end(node)

    def visit_Subscript(self,node):
        """
        Children nodes are:
            - value (the Name of the list we are accessing)
            - slice - with subchild Index.value which is a Num of the list index
            - ctx - Load or Store
        """
        self.begin(node)

        # Recall the list onto the stack
        assert isinstance(node.ctx, ast.Load)

        # DUPLICATE CODE - see visit_Assign line 369
        target = node
        var_name = target.value.id  # drill into subscript to get it
        if self.scopes.is_dictionary(var_name):
            self.process_dict_access(target)
        else:
            self.process_list_access(target)

        code = f"""
            RCLEL
        """
        self.program.insert_raw_lines(code)
        self.end(node)

    @recursive
    def visit_Break(self,node):
        """ visit a Break node """
        if self.resume_labels:
            label = self.resume_labels.pop()
            self.insert('GTO', label)
        # self.pending_stack_args = []

    @recursive
    def visit_Continue(self,node):
        """ visit a Continue node """
        if self.continue_labels:
            label = self.continue_labels.pop()
            self.insert('GTO', label)
        # self.pending_stack_args = []

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
        self.check_supported(node.id, node)
        if '.Load' in str(node.ctx):
            assert isinstance(node.ctx, ast.Load)
            if self.inside_alpha and not self.alpha_append_mode and not self.alpha_already_cleared:
                self.program.insert('CLA')
                self.alpha_already_cleared = True

            cmd = 'ARCL' if self.inside_alpha and \
                            not self.inside_binop and \
                            not self.var_name_is_loop_counter(node.id) and \
                            not self.inside_list_access else 'RCL'

            self.program.insert(f'{cmd} {self.scopes.var_to_reg(node.id)}', comment=node.id)
            self.pending_stack_args.append(node.id)
            if self.var_name_is_loop_counter(node.id):
                self.program.insert('IP')  # just get the integer portion of isg counter
            if self.pending_unary_op:
                self.program.insert('CHS')
                self.pending_unary_op = ''
        self.end(node)

    def visit_Num(self, node):
        self.begin(node)
        if self.inside_alpha and not self.alpha_append_mode and not self.alpha_already_cleared:
            self.program.insert('CLA')
            self.alpha_already_cleared = True
        self.program.insert(f'{self.pending_unary_op}{node.n}')
        self.pending_stack_args.append(node.n)
        self.pending_unary_op = ''
        self.end(node)

    def visit_Str(self, node):
        self.begin(node)
        if self.disallow_string_args:
            raise RpnError(f'Error: function disallows parameters of type string, line: {node.lineno}\n{node.first_token.line.strip()}')
        if self.inside_alpha:
            # self.program.insert(f'├"{node.s[0:15]}"')
            self.split_alpha_text(node.s, append=self.alpha_append_mode)
        else:
            self.program.insert(f'"{node.s[0:15]}"', type_='string')
        self.end(node)

    @recursive
    def visit_Expr(self, node):
        self.pending_stack_args = []

    # Most of these operators map to rpn in the opposite way, because of the stack order etc.
    # There are 12 RPN operators, p332
    cmpops = {
        "Eq":     "pEQ",
        "NotEq":  "pNEQ",
        "Lt":     "pLT",
        "LtE":    "pLTE",
        "Gt":     "pGT",
        "GtE":    "pGTE",
        # TODO
        "Is":     "PyIs",
        "IsNot":  "PyIsNot",
        "In":     "PyIn",
        "NotIn":  "PyNotIn",
        }
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
            subf = self.cmpops[o.__class__.__name__]
            self.program.insert_xeq(subf, comment='compare, return bool')

        self.end(node)

    def visit_UnaryOp(self, node):
        """
        op=USub(),
        operand=Num(n=1))],
        """
        if isinstance(node.op, ast.Not):
            self.visit(node.operand)
            self.visit(node.op)
        else:
            # for parsing e.g. -1
            self.visit(node.op)
            self.visit(node.operand)

    def visit_Or(self, node):
        self.program.insert_xeq('p2Bool')
        self.program.insert('OR')

    def visit_And(self, node):
        self.program.insert_xeq('p2Bool')
        self.program.insert('AND')

    def visit_Not(self, node):
        self.program.insert_xeq('pBool')
        self.program.insert_xeq('pNot')

    def visit_NameConstant(self, node):
        # True or False constants - node.value is either True or False (booleans). Are there any other NameConstants?
        if node.value:
            self.program.insert('1', comment='True')
        else:
            self.program.insert('0', comment='False')

    def visit_BoolOp(self, node):
        """
        BoolOp(
          op=Or(),
          values=[
            Num(n=1),
            Num(n=0),
            Num(n=1)]))])

        Push each pair and apply OP on-goingly, so as not to blow the stack.
        Probably don't need to track pending_stack_args here cos of this smart strategy.
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
        register = self.scopes.var_to_reg(varname, is_range_index=True)
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
