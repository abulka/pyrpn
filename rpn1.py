import ast
import astunparse


class RecursiveRpnVisitor(ast.NodeVisitor):
    """ recursive visitor with RPN generating capability :-) """

    def __init__(self):
        self.lineno = 0
        self.out = []
        self.assign_pending = None
        self.for_loop = False
        self.next_label = 0
        self.next_variable = 0

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
        print('call...', end=' ')
        print(type(node).__name__)
        # self.visit(node.func)  # no need to visit explicitly as the recursive decorator will do it for us

    @recursive
    def visit_Lambda(self,node):
        """ visit a Function node """
        print(type(node).__name__)

    @recursive
    def visit_FunctionDef(self,node):
        """ visit a Function node and visits it recursively"""
        print(type(node).__name__)
        self.add_rpn_label(node)

    def add_rpn_label(self, node):
        self.out.append(f'{self.lineno:02d} LBL "{node.name.upper()[-7:]}"')
        self.increment_lineno()

    def increment_lineno(self):
        self.lineno += 1

    @recursive
    def visit_Module(self,node):
        """ visit a Module node and the visits recursively"""
        pass

    def generic_visit(self,node):
        print(f'skipping {node}')
        if getattr(node, 'name', ''):
            print(f'name {node.name}')

    def visit_Name(self, node):
        print("visit_Name %s" % node.id)
        if self.for_loop and node.id == 'range':
            """
            00 1000  // for i in range....
            00 /
            00 1
            00 +
            00 STO 00  // counter
            00 LBL 00
            """
            self.out.append(f'{self.lineno:02d} {node.id}')
            self.increment_lineno()
        else:
            self.assign_pending = node.id

    def add_rpn_assign(self, val):
        self.out.append(f'{self.lineno:02d} {val}')
        self.increment_lineno()
        self.out.append(f'{self.lineno:02d} STO "{self.assign_pending.upper()[-7:]}"')
        self.increment_lineno()
        self.out.append(f'{self.lineno:02d} RDN')
        self.increment_lineno()

    def visit_Num(self, node):
        print(f'num {node.n}')
        self.add_rpn_assign(node.n)

    def write(self, s):
        print(s)

    def visit_For(self, node):
        # self.newline(node)
        self.for_loop = True
        self.write('for ')
        self.visit(node.target)
        self.write(' in ')
        self.visit(node.iter)
        self.write(':')
        self.body_or_else(node)
        self.for_loop = False
        self.write('END FOR ')

    def body(self, statements):
        # self.new_line = True
        # self.indentation += 1
        for stmt in statements:
            self.visit(stmt)
        # self.indentation -= 1

    def body_or_else(self, node):
        self.body(node.body)
        if node.orelse:
            # self.newline()
            self.write('else:')
            self.body(node.orelse)

# ANDY

s1 = """
def looper(n):
    x = 100
    for i in range(1, n):
        print(i)
        x += n
    return x
"""


visitor = RecursiveRpnVisitor()
tree = ast.parse(s1)
print(astunparse.dump(tree))
visitor.visit(tree)
print(visitor.out)

"""
expected

00 LBL "LOOPER"  // param n
01 100
02 STO "X"
00 RDN
00 1000  // for i in range....
00 /
00 1
00 +
00 STO 00  // counter
00 LBL 00
00 VIEW 00  // print(i)
00 RCL 00  // x += n
00 IP  // integer part
00 STO+ "X"
00 ISG 00
00 GTO 00
00 RCL "X"
00 RTN

 
"""