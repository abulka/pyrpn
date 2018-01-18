import ast
import asttokens
import tokenize
from textwrap import dedent

src = dedent("""
    def hello():
        x = 5
        there()
        
    def there():
        return 999  # my silly comment
    
    hello()  # call it
    there()        
""")

class RecursiveVisitor(ast.NodeVisitor):
    """ example recursive visitor """

    def recursive(func):
        """ decorator to make visitor work recursive """
        def wrapper(self,node):
            self.dump_line_and_comment(node)
            func(self,node)
            for child in ast.iter_child_nodes(node):
                self.visit(child)
        return wrapper

    def dump_line_and_comment(self, node):
        comment = atok.find_token(node.first_token, tokenize.COMMENT)
        print(f'On line "{node.first_token.line.strip():20s}" find_token found "{comment}"')

    @recursive
    def visit_Assign(self,node):
        """ visit a Assign node and visits it recursively"""

    @recursive
    def visit_BinOp(self, node):
        """ visit a BinOp node and visits it recursively"""

    @recursive
    def visit_Call(self,node):
        """ visit a Call node and visits it recursively"""

    @recursive
    def visit_Lambda(self,node):
        """ visit a Function node """

    @recursive
    def visit_FunctionDef(self,node):
        """ visit a Function node and visits it recursively"""


atok = asttokens.ASTTokens(src, parse=True)
tree = atok.tree
visitor = RecursiveVisitor()
visitor.visit(tree)
