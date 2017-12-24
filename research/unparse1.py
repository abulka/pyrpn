import inspect
import ast
import astunparse

s1 = """
def do(n):
    x = 100
    y = x + 100
    return y

def do_again(n):
    do()

"""
root_node = ast.parse(s1)

# get back the source code
# astunparse.unparse(ast.parse(inspect.getsource(ast)))
s = astunparse.unparse(root_node)
# print(s)

# get a pretty-printed dump of the AST
# s = astunparse.dump(ast.parse(inspect.getsource(ast)))
s = astunparse.dump(root_node)
print(s)