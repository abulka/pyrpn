import ast
import asttokens
import astunparse
from rpn import RecursiveRpnVisitor
import logging
from logger import config_log
from rpn_exceptions import RpnError

log = logging.getLogger(__name__)
config_log(log)

def parse(text, debug_options={}):
    """
    Parse source code and emit a program object which has many line objects
    representing the RPN.

    :param text: python source code
    :param debug_options: a dictionary of debug options
        'gen_descriptive_labels': default False
        'dump_ast': default False,
        'emit_pyrpn_lib': default True
    :return: program object
    """

    try:
        # self.tree = ast.parse(text)

        atok = asttokens.ASTTokens(text, parse=True)
        tree = atok.tree
    except SyntaxError as e:
        raise RpnError(format_error_add_caret(e))

    if debug_options.get('dump_ast', False):
        dump_ast(tree)

    visitor = RecursiveRpnVisitor()
    visitor.debug_gen_descriptive_labels = debug_options.get('gen_descriptive_labels', False)
    visitor.atok = atok
    visitor.visit(tree)
    if debug_options.get('emit_pyrpn_lib', True):
        visitor.finish()

    return visitor.program

def dump_ast(tree):
    """Pretty dump AST"""
    log.debug(astunparse.dump(tree))  # output is nice and compact
    log.debug(f"{'~'*25}")

def format_error_add_caret(ex):
    """
    Formats a nice multi-line error from the SyntaxError exception.
    See also interesting discussion on caret placement https://bugs.python.org/issue25677

    :param ex: SyntaxError exception
    :return: string
        line1: error message, line number
        line2: source code line
        line3:    ^
    """
    s = f'{ex.msg}, line: {ex.lineno}\n'  # ex.msg is the actual error message
    s += ex.text  # source code line, including \n
    if ex.offset and ex.offset > 0:
        s += ' ' * (ex.offset - 1) + '^' + '\n'
    return s