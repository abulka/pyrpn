import ast

class RecursiveVisitor(ast.NodeVisitor):
    """ example recursive visitor """

    def recursive(func):
        """ decorator to make visitor work recursive """
        def wrapper(self,node):
            func(self,node)
            for child in ast.iter_child_nodes(node):
                self.visit(child)
        return wrapper

    @recursive
    def visit_Assign(self,node):
        """ visit a Assign node and visits it recursively"""
        print(type(node).__name__)

    @recursive
    def visit_BinOp(self, node):
        """ visit a BinOp node and visits it recursively"""
        print(type(node).__name__)

    @recursive
    def visit_Call(self,node):
        """ visit a Call node and visits it recursively"""
        print(type(node).__name__)

    @recursive
    def visit_Lambda(self,node):
        """ visit a Function node """
        print(type(node).__name__)

    @recursive
    def visit_FunctionDef(self,node):
        """ visit a Function node and visits it recursively"""
        print(type(node).__name__)

    @recursive
    def visit_Module(self,node):
        """ visit a Module node and the visits recursively"""
        pass

    def generic_visit(self,node):
        pass

class SimpleVisitor(ast.NodeVisitor):
    """ simple visitor for comparison """

    def recursive(func):
        """ decorator to make visitor work recursive """
        def wrapper(self,node):
            func(self,node)
            for child in ast.iter_child_nodes(node):
                self.visit(child)
        return wrapper

    def visit_Assign(self,node):
        """ visit a Assign node """
        print(type(node).__name__)

    def visit_BinOp(self, node):
        """ visit a BinOp node """
        print(type(node).__name__)

    def visit_Call(self,node):
        """ visit a Call node """
        print(type(node).__name__)

    def visit_Lambda(self,node):
        """ visit a Function node """
        print(type(node).__name__)

    def visit_FunctionDef(self,node):
        """ visit a Function node """
        print(type(node).__name__)

    @recursive
    def visit_Module(self,node):
        """ visit a Module node and the visits recursively, otherwise you
        wouldn't see anything here"""
        pass

    def generic_visit(self,node):
        pass

# usage example
a = """
b= lambda x: x*5 +5
def hhh(u):
    b=19
    return u*b
m=hhh(9*4+5)
"""

recursive_visitor = RecursiveVisitor()
simple_visitor = SimpleVisitor()
tree = ast.parse(a)
print('\nvisit recursive\n')
recursive_visitor.visit(tree)
print('\nvisit simple\n')
simple_visitor.visit(tree)

