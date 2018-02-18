import ast
from labels import FunctionLabels
import tokenize
from rpn_exceptions import RpnError, source_code_line_info
import logging
from logger import config_log

log = logging.getLogger(__name__)
config_log(log)


class LookaheadRpnVisitor(ast.NodeVisitor):

    def __init__(self):
        self.first_def_label = None
        self.labels = FunctionLabels()
        # self.local_labels = LocalLabels()

    def make_global_label(self, func_name):
        label = f'"{func_name[:7]}"'
        self.labels.func_to_lbl(func_name, label=label, are_defining_a_def=True)
        return label

    def make_local_label(self, func_name):
        self.labels.func_to_lbl(func_name, are_defining_a_def=True)

    def has_rpn_def_directive(self, node):
        comment = self.find_comment(node)
        return 'rpn: ' in comment and 'export' in comment

    def find_comment(self, node):
        # Finds comment in the original python source code associated with this token.
        # See my discussion of various techniques at https://github.com/gristlabs/asttokens/issues/10
        def find_line_comment(start_token):
            t = start_token
            while t.type not in (tokenize.COMMENT, tokenize.NL, tokenize.NEWLINE, tokenize.ENDMARKER):
                t = self.atok.next_token(t, include_extra=True)
            return t.string if t.type == tokenize.COMMENT else ''
        return find_line_comment(node.first_token)

    def quick_error(self, msg, node):
        raise RpnError(f'{msg} (lookahead), {source_code_line_info(node)}')

    def recursive(func):
        """ decorator to make visitor work recursive """
        def wrapper(self,node):
            func(self,node)
            for child in ast.iter_child_nodes(node):
                self.visit(child)
        return wrapper

    def visit_Assign(self,node):
        """ visit a Assign node """

    def visit_BinOp(self, node):
        """ visit a BinOp node """

    @recursive
    def visit_Expr(self, node):
        """important to visit this, because Call is nested inside this"""

    @recursive
    def visit_Call(self,node):
        """ visit a Call node """
        try:
            func_name = node.func.id
        except AttributeError:
            pass
        else:
            log.debug(f'Call {func_name}')
            if func_name == 'LBL':
                if self.first_def_label != None: self.quick_error('Can only define a single main global label before any other defs', node)
                if len(node.args) != 1: self.quick_error('Wrong number of args to LBL', node)
                arg = node.args[0]
                if not isinstance(arg, ast.Str): self.quick_error('Wrong type of arg to LBL, should be string', node)
                lbl_name = arg.s
                self.first_def_label = self.make_global_label(lbl_name)  # main entry point to rpn program

    def visit_Lambda(self,node):
        """ visit a Function node """

    @recursive
    def visit_FunctionDef(self, node):
        if self.labels.has_function_mapping(node.name): self.quick_error(
            f'Duplicate function "{node.name}" not allowed, even if it is in another scope - sorry.  Try using a unique name', node)

        if not self.first_def_label:
            self.first_def_label = self.make_global_label(node.name)  # main entry point to rpn program
        else:
            if not self.has_rpn_def_directive(node):
                self.make_local_label(node.name)
            else:
                self.make_global_label(node.name)


    @recursive
    def visit_Module(self,node):
        """ visit a Module node and the visits recursively, otherwise you wouldn't see anything here"""

    def generic_visit(self,node):
        pass
