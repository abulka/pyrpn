import ast
import asttokens
import astunparse
from rpn import RecursiveRpnVisitor
import logging
from logger import config_log

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

    # self.tree = ast.parse(text)

    atok = asttokens.ASTTokens(text, parse=True)
    tree = atok.tree

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

